#!/usr/bin/env bash
set -euo pipefail

# Enable debug output if DEBUG is set
[[ "${DEBUG:-}" == "true" ]] && set -x

zstore_dir=$(git rev-parse --show-toplevel)
# source "$zstore_dir"/.env
source "$zstore_dir"/scripts/network_env.sh

cd "$zstore_dir"/subprojects/spdk


# Normal run
# $ sudo ./emulation-target.sh

# Debug mode
# $ DEBUG=true sudo ./emulation-target.sh

# With custom hugepage memory
# $ HUGEMEM=8192 sudo ./emulation-target.sh

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
}

# Get available vfio-pci bound NVMe devices
get_available_nvme_devices() {
    ./scripts/setup.sh status | grep -E "NVMe.*vfio-pci" | awk '{print $2}' | grep -E '^[0-9a-f]{4}:[0-9a-f]{2}:[0-9a-f]{2}\.[0-9]$'
}

# Check if a device is bound to vfio-pci
is_device_available() {
    local pci_addr=$1
    ./scripts/setup.sh status | grep -E "^$pci_addr.*vfio-pci" >/dev/null 2>&1
}

# Attach NVMe controller and return the namespace name
attach_nvme_controller() {
    local bdev_name=$1
    local pci_addr=$2
    local max_retries=3
    local retry=0
    
    # Check if device is available
    if ! is_device_available "$pci_addr"; then
        log_error "Device $pci_addr is not bound to vfio-pci"
        return 1
    fi
    
    # Try to attach with retries
    while [ $retry -lt $max_retries ]; do
        if output=$(./scripts/rpc.py bdev_nvme_attach_controller -b "$bdev_name" -t PCIe -a "$pci_addr" 2>&1); then
            # Extract the namespace name from the output
            ns_name=$(echo "$output" | tail -n1 | tr -d '[:space:]')
            log_info "Successfully attached $pci_addr as $ns_name"
            echo "$ns_name"
            return 0
        else
            retry=$((retry + 1))
            log_warn "Failed to attach controller at $pci_addr (attempt $retry/$max_retries)"
            [ $retry -lt $max_retries ] && sleep 2
        fi
    done
    
    log_error "Failed to attach controller at $pci_addr after $max_retries attempts"
    return 1
}

if pidof nvmf_tgt; then
	scripts/rpc.py spdk_kill_instance SIGTERM >/dev/null || true
	scripts/rpc.py spdk_kill_instance SIGKILL >/dev/null || true
	pkill -f nvmf_tgt || true
	pkill -f reactor_0 || true
	sleep 3
fi

HUGEMEM=4096 ./scripts/setup.sh

./build/bin/nvmf_tgt -m '[0,1,2,3]' &
sleep 3

# Main configuration structure
declare -A HOST_CONFIG

# Define configurations for each host
HOST_CONFIG[zstore2]="06:00.0,0c:00.0"  # Use available devices
HOST_CONFIG[zstore3]="02:00.0,0c:00.0"
HOST_CONFIG[zstore4]="06:00.0,0c:00.0"
HOST_CONFIG[zstore5]="06:00.0,0c:00.0"
HOST_CONFIG[zstore6]="06:00.0,07:00.0"

# Get configuration for this host
if [[ ! -v HOST_CONFIG[$HOSTNAME] ]]; then
	log_error "No configuration found for hostname: $HOSTNAME"
	exit 1
fi

# Parse PCIe addresses
IFS=',' read -r pci1 pci2 <<< "${HOST_CONFIG[$HOSTNAME]}"
ctrl_nqn="nqn.2024-04.io.$HOSTNAME:cnode1"

# Check available devices
log_info "Checking available NVMe devices..."
available_devices=($(get_available_nvme_devices))
log_info "Available devices: ${available_devices[*]}"

# Try to use configured devices, fall back to available ones if needed
if ! is_device_available "$pci1"; then
	log_warn "Configured device $pci1 not available, using first available device"
	exit 1
fi

if ! is_device_available "$pci2"; then
	log_warn "Configured device $pci2 not available, using second available device"
	exit 1
fi

if [[ -z "$pci1" ]] || [[ -z "$pci2" ]]; then
	log_error "Not enough available NVMe devices"
	exit 1
fi

log_info "Using devices: $pci1 and $pci2"

# Attach controllers
ns1=$(attach_nvme_controller "nvme0" "$pci1") || exit 1
ns2=$(attach_nvme_controller "nvme1" "$pci2") || exit 1

# Create zone block devices based on hostname
case "$HOSTNAME" in
	zstore2|zstore3|zstore6)
		create_zone_block "zone0" "$ns1"
		create_zone_block "zone1" "$ns2"
		namespaces=("zone0" "zone1")
		;;
	zstore4|zstore5)
		# These hosts use raw namespaces
		namespaces=("${ns1}2" "${ns2}2")
		;;
	*)
		log_error "Unknown configuration for $HOSTNAME"
		exit 1
		;;
esac

# Display device information
log_info "Device configuration:"
for ns in "${namespaces[@]}"; do
	if info=$(get_ns_info "$ns" 2>/dev/null); then
		echo "$info"
	fi
done

# Create NVMf transport
log_info "Creating NVMf RDMA transport..."
scripts/rpc.py nvmf_create_transport -t RDMA -q 256 -m 512 -c 4096 -i 131072 -u 8192 -a 256 -b 32 -n 8192

# Create subsystem
log_info "Creating NVMf subsystem: $ctrl_nqn"
scripts/rpc.py nvmf_create_subsystem "$ctrl_nqn" -a -s SPDK02 -d SPDK_Controller2 -m 8
sleep 1

# Add namespaces to subsystem
case "$HOSTNAME" in
	zstore2|zstore3|zstore6)
		scripts/rpc.py nvmf_subsystem_add_ns "$ctrl_nqn" zone0
		scripts/rpc.py nvmf_subsystem_add_ns "$ctrl_nqn" zone1
		;;
	zstore4|zstore5)
		scripts/rpc.py nvmf_subsystem_add_ns "$ctrl_nqn" "${ns1}2"
		scripts/rpc.py nvmf_subsystem_add_ns "$ctrl_nqn" "${ns2}2"
		;;
esac

# Add listeners
ip_suffix=${HOSTNAME: -1}
log_info "Adding NVMf listeners on 12.12.12.$ip_suffix"
for port in 5520 5521 5522; do
	scripts/rpc.py nvmf_subsystem_add_listener "$ctrl_nqn" -t RDMA -f ipv4 -a "12.12.12.$ip_suffix" -s "$port"
done


# if [ "$HOSTNAME" == "zstore2" ]; then
# 	pci1=06:00.0
# 	pci2=0c:00.0
# 	ctrl_nqn="nqn.2024-04.io.zstore2:cnode1"
# ./scripts/rpc.py bdev_nvme_attach_controller -b nvme0 -t PCIe -a "$pci1"
# ./scripts/rpc.py bdev_nvme_attach_controller -b nvme4 -t PCIe -a "$pci2"
# ./scripts/rpc.py bdev_zone_block_create -b zone0 -n nvme0n1 -z 262144 -o 16
# ./scripts/rpc.py bdev_zone_block_create -b zone1 -n nvme4n1 -z 262144 -o 16
# elif [ "$HOSTNAME" == "zstore3" ]; then
# 	pci1=02:00.0
# 	pci2=0c:00.0
# 	ctrl_nqn="nqn.2024-04.io.zstore3:cnode1"
# elif [ "$HOSTNAME" == "zstore4" ]; then
# 	pci1=06:00.0
# 	pci2=0c:00.0
# 	ctrl_nqn="nqn.2024-04.io.zstore4:cnode1"
# elif [ "$HOSTNAME" == "zstore5" ]; then
# 	pci1=06:00.0
# 	pci2=0c:00.0
# 	ctrl_nqn="nqn.2024-04.io.zstore5:cnode1"
# elif [ "$HOSTNAME" == "zstore6" ]; then
# 	pci1=06:00.0
# 	pci2=07:00.0
# 	ctrl_nqn="nqn.2024-04.io.zstore6:cnode1"
# fi

# List all bdevs
# Get information about all bdevs (including zone devices)
# ./scripts/rpc.py bdev_get_bdevs

# Get information about a specific zone device
# ./scripts/rpc.py bdev_get_bdevs -b zone1

# You can also format the output as JSON for easier parsing
# ./scripts/rpc.py bdev_get_bdevs -b zone1 | python -m json.tool


# scripts/rpc.py nvmf_create_transport -t TCP -u 16384 -m 8 -c 8192
# scripts/rpc.py nvmf_create_transport -t RDMA -u 8192 -i 131072 -c 8192
# scripts/rpc.py nvmf_create_transport -t RDMA -q 32 -n 1023

# scripts/rpc.py nvmf_create_transport -t RDMA -q 256 -m 512 -c 4096 -i 131072 -u 8192 -a 256 -b 32 -n 8192
# {
# trtype: "RDMA"
# max_queue_depth: 128
# max_qpairs_per_ctrlr: 64
# in_capsule_data_size: 4096
# max_io_size: 131072
# io_unit_size: 8192
# max_aq_depth: 128
# num_shared_buffers: 8192
# buf_cache_size: 32
# }

# if [ "$HOSTNAME" == "zstore1" ]; then
# 	scripts/rpc.py nvmf_create_subsystem "$ctrl_nqn" -a -s SPDK01 -d SPDK_Controller1 -m 8
# 	sleep 1
# 	scripts/rpc.py nvmf_subsystem_add_ns "$ctrl_nqn" nvme0n2
# 	scripts/rpc.py nvmf_subsystem_add_ns "$ctrl_nqn" nvme1n2
# 	scripts/rpc.py nvmf_subsystem_add_listener "$ctrl_nqn" -t RDMA -f ipv4 -a 12.12.12.1 -s 5520
# 	scripts/rpc.py nvmf_subsystem_add_listener "$ctrl_nqn" -t RDMA -f ipv4 -a 12.12.12.1 -s 5521
# 	scripts/rpc.py nvmf_subsystem_add_listener "$ctrl_nqn" -t RDMA -f ipv4 -a 12.12.12.1 -s 5522
# elif [ "$HOSTNAME" == "zstore2" ]; then
# 	scripts/rpc.py nvmf_create_subsystem "$ctrl_nqn" -a -s SPDK02 -d SPDK_Controller2 -m 8
# 	sleep 1
# 	# scripts/rpc.py nvmf_subsystem_add_ns "$ctrl_nqn" zone0
# 	scripts/rpc.py nvmf_subsystem_add_ns "$ctrl_nqn" zone1
# 	scripts/rpc.py nvmf_subsystem_add_listener "$ctrl_nqn" -t RDMA -f ipv4 -a 12.12.12.2 -s 5520
# 	scripts/rpc.py nvmf_subsystem_add_listener "$ctrl_nqn" -t RDMA -f ipv4 -a 12.12.12.2 -s 5521
# 	scripts/rpc.py nvmf_subsystem_add_listener "$ctrl_nqn" -t RDMA -f ipv4 -a 12.12.12.2 -s 5522
# elif [ "$HOSTNAME" == "zstore3" ]; then
# 	scripts/rpc.py nvmf_create_subsystem "$ctrl_nqn" -a -s SPDK02 -d SPDK_Controller2 -m 8
# 	sleep 1
# 	scripts/rpc.py nvmf_subsystem_add_ns "$ctrl_nqn" zone0
# 	scripts/rpc.py nvmf_subsystem_add_ns "$ctrl_nqn" zone1
# 	scripts/rpc.py nvmf_subsystem_add_listener "$ctrl_nqn" -t RDMA -f ipv4 -a 12.12.12.3 -s 5520
# 	scripts/rpc.py nvmf_subsystem_add_listener "$ctrl_nqn" -t RDMA -f ipv4 -a 12.12.12.3 -s 5521
# 	scripts/rpc.py nvmf_subsystem_add_listener "$ctrl_nqn" -t RDMA -f ipv4 -a 12.12.12.3 -s 5522
# elif [ "$HOSTNAME" == "zstore4" ]; then
# 	scripts/rpc.py nvmf_create_subsystem "$ctrl_nqn" -a -s SPDK02 -d SPDK_Controller2 -m 8
# 	sleep 1
# 	scripts/rpc.py nvmf_subsystem_add_ns "$ctrl_nqn" nvme0n2
# 	scripts/rpc.py nvmf_subsystem_add_ns "$ctrl_nqn" nvme1n2
# 	scripts/rpc.py nvmf_subsystem_add_listener "$ctrl_nqn" -t RDMA -f ipv4 -a 12.12.12.4 -s 5520
# 	scripts/rpc.py nvmf_subsystem_add_listener "$ctrl_nqn" -t RDMA -f ipv4 -a 12.12.12.4 -s 5521
# 	scripts/rpc.py nvmf_subsystem_add_listener "$ctrl_nqn" -t RDMA -f ipv4 -a 12.12.12.4 -s 5522
# elif [ "$HOSTNAME" == "zstore5" ]; then
# 	scripts/rpc.py nvmf_create_subsystem "$ctrl_nqn" -a -s SPDK02 -d SPDK_Controller2 -m 8
# 	sleep 1
# 	scripts/rpc.py nvmf_subsystem_add_ns "$ctrl_nqn" nvme0n2
# 	scripts/rpc.py nvmf_subsystem_add_ns "$ctrl_nqn" nvme1n2
# 	scripts/rpc.py nvmf_subsystem_add_listener "$ctrl_nqn" -t RDMA -f ipv4 -a 12.12.12.5 -s 5520
# 	scripts/rpc.py nvmf_subsystem_add_listener "$ctrl_nqn" -t RDMA -f ipv4 -a 12.12.12.5 -s 5521
# 	scripts/rpc.py nvmf_subsystem_add_listener "$ctrl_nqn" -t RDMA -f ipv4 -a 12.12.12.5 -s 5522
# fi

scripts/rpc.py framework_set_scheduler dynamic

wait
