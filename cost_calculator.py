# Pricing in INR per month
CPU_COST_PER_CORE = 500
RAM_COST_PER_GB = 200
STORAGE_COST_PER_GB = 50

def calculate_cost(cpu_cores, ram_gb, storage_gb):
    """Calculate monthly cost for a single VM"""
    cpu_cost = cpu_cores * CPU_COST_PER_CORE
    ram_cost = ram_gb * RAM_COST_PER_GB
    storage_cost = storage_gb * STORAGE_COST_PER_GB
    return cpu_cost + ram_cost + storage_cost

def calculate_all_vms_cost(vms):
    """Calculate total cost for all VMs"""
    total = 0
    breakdown = []
    for vm in vms:
        cost = calculate_cost(vm.cpu_cores, vm.ram_gb, vm.storage_gb)
        total += cost
        breakdown.append({
            'name': vm.vm_name,
            'cpu': vm.cpu_cores * CPU_COST_PER_CORE,
            'ram': vm.ram_gb * RAM_COST_PER_GB,
            'storage': vm.storage_gb * STORAGE_COST_PER_GB,
            'total': cost
        })
    return total, breakdown

def get_pricing_summary():
    """Get pricing rate card"""
    return {
        'CPU': {'rate': CPU_COST_PER_CORE, 'unit': 'per core'},
        'RAM': {'rate': RAM_COST_PER_GB, 'unit': 'per GB'},
        'Storage': {'rate': STORAGE_COST_PER_GB, 'unit': 'per GB'}
    }

def estimate_savings(current_cost, new_cost):
    """Calculate savings between two costs"""
    savings = current_cost - new_cost
    percentage = (savings / current_cost) * 100 if current_cost > 0 else 0
    return savings, percentage