from models import db, FirewallRule

def add_firewall_rule(user_id, rule_name, protocol, port, source_ip, action):
    """Add a new firewall rule"""
    rule = FirewallRule(
        user_id=user_id,
        rule_name=rule_name,
        protocol=protocol,
        port=port,
        source_ip=source_ip,
        action=action
    )
    db.session.add(rule)
    db.session.commit()
    return rule

def delete_firewall_rule(rule_id, user_id):
    """Delete a firewall rule (only if owned by user)"""
    rule = FirewallRule.query.get_or_404(rule_id)
    if rule.user_id != user_id:
        return None
    db.session.delete(rule)
    db.session.commit()
    return rule

def get_user_rules(user_id):
    """Get all firewall rules for a user"""
    return FirewallRule.query.filter_by(user_id=user_id).all()

def check_firewall_allows(user_id, protocol, port, source_ip):
    """Check if traffic is allowed by firewall rules"""
    rules = FirewallRule.query.filter_by(user_id=user_id).order_by(FirewallRule.priority).all()
    
    # Default: Deny all if no rules match
    default_action = 'Deny'
    
    for rule in rules:
        # Check if rule matches
        if (rule.protocol == protocol or rule.protocol == 'ANY') and \
           (rule.port == port or rule.port == 0) and \
           (source_ip == rule.source_ip or rule.source_ip == '0.0.0.0/0'):
            return rule.action == 'Allow'
    
    return default_action == 'Allow'