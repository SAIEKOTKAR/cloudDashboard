from models import db, VM
import random

def generate_ip():
    """Generate a random private IP address"""
    return f"10.0.{random.randint(1,255)}.{random.randint(1,255)}"

def create_vm(user_id, vm_name, cpu_cores, ram_gb, storage_gb, os_type):
    """Create a new virtual machine"""
    ip_address = generate_ip()
    vm = VM(
        user_id=user_id,
        vm_name=vm_name,
        cpu_cores=cpu_cores,
        ram_gb=ram_gb,
        storage_gb=storage_gb,
        os_type=os_type,
        ip_address=ip_address
    )
    db.session.add(vm)
    db.session.commit()
    return vm

def delete_vm(vm_id, user_id):
    """Delete a virtual machine (only if owned by user)"""
    vm = VM.query.get_or_404(vm_id)
    if vm.user_id != user_id:
        return None
    db.session.delete(vm)
    db.session.commit()
    return vm

def toggle_vm_status(vm_id, user_id):
    """Start/Stop a virtual machine"""
    vm = VM.query.get_or_404(vm_id)
    if vm.user_id != user_id:
        return None
    vm.status = 'Stopped' if vm.status == 'Running' else 'Running'
    db.session.commit()
    return vm

def get_user_vms(user_id):
    """Get all VMs for a user"""
    return VM.query.filter_by(user_id=user_id).all()

def get_vm_count(user_id):
    """Get total VM count for a user"""
    return VM.query.filter_by(user_id=user_id).count()