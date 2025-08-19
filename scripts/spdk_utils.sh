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


