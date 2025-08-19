#!/usr/bin/env bash
set -euo pipefail

# Enable debug output if DEBUG is set
[[ "${DEBUG:-}" == "true" ]] && set -x

zstore_dir=$(git rev-parse --show-toplevel)
# source "$zstore_dir"/.env
source "$zstore_dir"/scripts/network_env.sh
source "$zstore_dir"/scripts/spdk_utils.sh

cd "$zstore_dir"/subprojects/spdk


# Normal run
# $ sudo ./emulation-target.sh

# Debug mode
# $ DEBUG=true sudo ./emulation-target.sh

# With custom hugepage memory
# $ HUGEMEM=8192 sudo ./emulation-target.sh

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
HOST_CONFIG[zstore2]="06:00.0,0c:00.0,nvme1,nvme2"
HOST_CONFIG[zstore3]="02:00.0,0c:00.0,nvme0,nvme1"
# HOST_CONFIG[zstore4]="06:00.0,0c:00.0"
# HOST_CONFIG[zstore5]="06:00.0,0c:00.0"
HOST_CONFIG[zstore6]="06:00.0,07:00.0,nvme1,nvme2"

# Get configuration for this host
if [[ ! -v HOST_CONFIG[$HOSTNAME] ]]; then
	log_error "No configuration found for hostname: $HOSTNAME"
	exit 1
fi

# Parse PCIe addresses
IFS=',' read -r pci1 pci2 nvme1 nvme2 <<< "${HOST_CONFIG[$HOSTNAME]}"


ctrl_nqn="nqn.2024-04.io.$HOSTNAME:cnode1"

scripts/rpc.py bdev_nvme_attach_controller -b "$nvme1" -t PCIe -a "$pci1"
scripts/rpc.py bdev_nvme_attach_controller -b "$nvme2" -t PCIe -a "$pci2"
scripts/rpc.py bdev_zone_block_create -b zone0 -n "$nvme1"n1 -z 262144 -o 16
scripts/rpc.py bdev_zone_block_create -b zone1 -n "$nvme2"n1 -z 262144 -o 16

# List all bdevs
# Get information about all bdevs (including zone devices)
./scripts/rpc.py bdev_get_bdevs

# Get information about a specific zone device
./scripts/rpc.py bdev_get_bdevs -b zone1

# You can also format the output as JSON for easier parsing
./scripts/rpc.py bdev_get_bdevs -b zone1 | python -m json.tool


# scripts/rpc.py nvmf_create_transport -t TCP -u 16384 -m 8 -c 8192
# scripts/rpc.py nvmf_create_transport -t RDMA -u 8192 -i 131072 -c 8192
# scripts/rpc.py nvmf_create_transport -t RDMA -q 32 -n 1023

scripts/rpc.py nvmf_create_transport -t RDMA -q 256 -m 512 -c 4096 -i 131072 -u 8192 -a 256 -b 32 -n 8192
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

scripts/rpc.py nvmf_create_subsystem "$ctrl_nqn" -a -s SPDK02 -d SPDK_Controller2 -m 8
sleep 1
scripts/rpc.py nvmf_subsystem_add_ns "$ctrl_nqn" zone0
scripts/rpc.py nvmf_subsystem_add_ns "$ctrl_nqn" zone1

# Add listeners
ip_suffix=${HOSTNAME: -1}
log_info "Adding NVMf listeners on 12.12.12.$ip_suffix"
for port in 5520 5521 5522; do
	scripts/rpc.py nvmf_subsystem_add_listener "$ctrl_nqn" -t RDMA -f ipv4 -a "12.12.12.$ip_suffix" -s "$port"
done

scripts/rpc.py framework_set_scheduler dynamic

wait
