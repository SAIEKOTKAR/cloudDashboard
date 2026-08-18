from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    vms = db.relationship('VM', backref='owner', lazy=True)
    firewall_rules = db.relationship('FirewallRule', backref='owner', lazy=True)
    networks = db.relationship('Network', backref='owner', lazy=True)

class VM(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vm_name = db.Column(db.String(100), nullable=False)
    cpu_cores = db.Column(db.Integer, nullable=False)
    ram_gb = db.Column(db.Integer, nullable=False)
    storage_gb = db.Column(db.Integer, nullable=False)
    os_type = db.Column(db.String(50), default='Ubuntu 22.04')
    status = db.Column(db.String(20), default='Running')
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FirewallRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rule_name = db.Column(db.String(100), nullable=False)
    protocol = db.Column(db.String(10), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    source_ip = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(10), nullable=False)
    priority = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Network(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    network_name = db.Column(db.String(100), nullable=False)
    cidr = db.Column(db.String(50), nullable=False)
    gateway = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(200), nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)