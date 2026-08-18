from models import db, Network
from netaddr import IPNetwork

def create_network(user_id, network_name, cidr, gateway):
    """Create a new virtual network"""
    # Validate CIDR
    try:
        ip_net = IPNetwork(cidr)
    except:
        return None
    
    network = Network(
        user_id=user_id,
        network_name=network_name,
        cidr=cidr,
        gateway=gateway
    )
    db.session.add(network)
    db.session.commit()
    return network

def delete_network(network_id, user_id):
    """Delete a network (only if owned by user)"""
    network = Network.query.get_or_404(network_id)
    if network.user_id != user_id:
        return None
    db.session.delete(network)
    db.session.commit()
    return network

def get_user_networks(user_id):
    """Get all networks for a user"""
    return Network.query.filter_by(user_id=user_id).all()

def get_network_info(cidr):
    """Get network details from CIDR"""
    try:
        net = IPNetwork(cidr)
        return {
            'network': str(net.network),
            'broadcast': str(net.broadcast),
            'netmask': str(net.netmask),
            'hosts': list(net.iter_hosts()),
            'host_count': len(list(net.iter_hosts()))
        }
    except:
        return None

def get_available_ips(cidr, used_ips):
    """Get available IPs in a network"""
    try:
        net = IPNetwork(cidr)
        available = []
        for ip in net.iter_hosts():
            ip_str = str(ip)
            if ip_str not in used_ips:
                available.append(ip_str)
        return available
    except:
        return []