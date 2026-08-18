from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, VM, FirewallRule, Network, ActivityLog
from vm_manager import create_vm, delete_vm, toggle_vm_status, get_user_vms
from firewall_manager import add_firewall_rule, delete_firewall_rule, get_user_rules
from network_manager import create_network, delete_network, get_user_networks
from cost_calculator import calculate_cost, calculate_all_vms_cost
from logger import log_activity, get_user_logs, get_all_logs
import bcrypt
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# --- Database Configuration ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "cloud_manager.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ==================== ROUTES ====================

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'danger')
            return redirect(url_for('register'))
        
        hashed_pw = hash_password(password)
        user = User(username=username, email=email, password_hash=hashed_pw)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password(password, user.password_hash):
            login_user(user)
            log_activity(user.id, 'User logged in')
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    log_activity(current_user.id, 'User logged out')
    logout_user()
    flash('Logged out!', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    vms = get_user_vms(current_user.id)
    total_cost, _ = calculate_all_vms_cost(vms)
    
    return render_template('dashboard.html',
                         vms=vms,
                         total_vms=len(vms),
                         total_cpu=sum(vm.cpu_cores for vm in vms),
                         total_ram=sum(vm.ram_gb for vm in vms),
                         total_storage=sum(vm.storage_gb for vm in vms),
                         total_cost=total_cost)

@app.route('/vms')
@login_required
def manage_vms():
    vms = get_user_vms(current_user.id)
    return render_template('vms.html', vms=vms)

@app.route('/create_vm', methods=['POST'])
@login_required
def create_vm_route():
    vm_name = request.form['vm_name']
    cpu_cores = int(request.form['cpu_cores'])
    ram_gb = int(request.form['ram_gb'])
    storage_gb = int(request.form['storage_gb'])
    os_type = request.form['os_type']
    
    vm = create_vm(current_user.id, vm_name, cpu_cores, ram_gb, storage_gb, os_type)
    log_activity(current_user.id, f'Created VM: {vm_name}', f'CPU: {cpu_cores}, RAM: {ram_gb}GB')
    flash(f'VM "{vm_name}" created! IP: {vm.ip_address}', 'success')
    return redirect(url_for('manage_vms'))

@app.route('/delete_vm/<int:vm_id>')
@login_required
def delete_vm_route(vm_id):
    vm = delete_vm(vm_id, current_user.id)
    if vm:
        log_activity(current_user.id, f'Deleted VM: {vm.vm_name}')
        flash('VM deleted!', 'success')
    else:
        flash('Unauthorized!', 'danger')
    return redirect(url_for('manage_vms'))

@app.route('/toggle_vm/<int:vm_id>')
@login_required
def toggle_vm_route(vm_id):
    vm = toggle_vm_status(vm_id, current_user.id)
    if vm:
        log_activity(current_user.id, f'Toggled VM: {vm.vm_name} to {vm.status}')
        flash(f'VM is now {vm.status}!', 'success')
    else:
        flash('Unauthorized!', 'danger')
    return redirect(url_for('manage_vms'))

@app.route('/firewall')
@login_required
def manage_firewall():
    rules = get_user_rules(current_user.id)
    return render_template('firewall.html', rules=rules)

@app.route('/add_firewall_rule', methods=['POST'])
@login_required
def add_firewall_route():
    rule_name = request.form['rule_name']
    protocol = request.form['protocol']
    port = int(request.form['port'])
    source_ip = request.form['source_ip']
    action = request.form['action']
    
    rule = add_firewall_rule(current_user.id, rule_name, protocol, port, source_ip, action)
    log_activity(current_user.id, f'Added firewall rule: {rule_name}')
    flash('Firewall rule added!', 'success')
    return redirect(url_for('manage_firewall'))

@app.route('/delete_firewall_rule/<int:rule_id>')
@login_required
def delete_firewall_route(rule_id):
    rule = delete_firewall_rule(rule_id, current_user.id)
    if rule:
        log_activity(current_user.id, f'Deleted firewall rule: {rule.rule_name}')
        flash('Rule deleted!', 'success')
    else:
        flash('Unauthorized!', 'danger')
    return redirect(url_for('manage_firewall'))

@app.route('/networks')
@login_required
def manage_networks():
    networks = get_user_networks(current_user.id)
    return render_template('networks.html', networks=networks)

@app.route('/add_network', methods=['POST'])
@login_required
def add_network_route():
    network_name = request.form['network_name']
    cidr = request.form['cidr']
    gateway = request.form['gateway']
    
    network = create_network(current_user.id, network_name, cidr, gateway)
    if network:
        log_activity(current_user.id, f'Created network: {network_name}')
        flash('Network created!', 'success')
    else:
        flash('Invalid CIDR!', 'danger')
    return redirect(url_for('manage_networks'))

@app.route('/delete_network/<int:network_id>')
@login_required
def delete_network_route(network_id):
    network = delete_network(network_id, current_user.id)
    if network:
        log_activity(current_user.id, f'Deleted network: {network.network_name}')
        flash('Network deleted!', 'success')
    else:
        flash('Unauthorized!', 'danger')
    return redirect(url_for('manage_networks'))

@app.route('/monitor')
@login_required
def monitor():
    vms = get_user_vms(current_user.id)
    return render_template('monitor.html', vms=vms)

@app.route('/cost')
@login_required
def cost():
    vms = get_user_vms(current_user.id)
    total_cost, cost_breakdown = calculate_all_vms_cost(vms)
    return render_template('cost.html', total_cost=total_cost, cost_breakdown=cost_breakdown)

@app.route('/logs')
@login_required
def view_logs():
    logs = get_user_logs(current_user.id)
    return render_template('logs.html', logs=logs)

@app.route('/admin')
@login_required
def admin():
    if current_user.role != 'admin':
        flash('Admin access required!', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    all_vms = VM.query.all()
    all_logs = get_all_logs()
    return render_template('admin.html', users=users, all_vms=all_vms, all_logs=all_logs)

@app.route('/setup_admin')
def setup_admin():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        hashed_pw = hash_password('admin123')
        admin = User(username='admin', email='admin@cloud.com', password_hash=hashed_pw, role='admin')
        db.session.add(admin)
        db.session.commit()
        return '✅ Admin created!<br>Username: admin<br>Password: admin123'
    return '⚠️ Admin already exists!'

# ==================== MAIN EXECUTION ====================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)