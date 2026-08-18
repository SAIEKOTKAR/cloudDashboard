from models import db, ActivityLog
from datetime import datetime, timedelta
import pytz

# Set the timezone to Indian Standard Time (IST)
ist = pytz.timezone('Asia/Kolkata')

def log_activity(user_id, action, details=""):
    """Log user activity"""
    # Get the current time in IST
    now_ist = datetime.now(ist)
    
    log = ActivityLog(
        user_id=user_id,
        action=action,
        details=details,
        timestamp=now_ist  # Save directly in IST
    )
    db.session.add(log)
    db.session.commit()
    return log

def get_user_logs(user_id, limit=50):
    """Get recent logs for a user"""
    return ActivityLog.query.filter_by(user_id=user_id)\
        .order_by(ActivityLog.timestamp.desc())\
        .limit(limit)\
        .all()

def get_all_logs(limit=100):
    """Get all logs (admin only)"""
    return ActivityLog.query\
        .order_by(ActivityLog.timestamp.desc())\
        .limit(limit)\
        .all()

def get_logs_by_action(user_id, action):
    """Get logs filtered by action type"""
    return ActivityLog.query.filter_by(user_id=user_id, action=action)\
        .order_by(ActivityLog.timestamp.desc())\
        .all()

def get_logs_by_date_range(user_id, start_date, end_date):
    """Get logs within date range"""
    return ActivityLog.query.filter_by(user_id=user_id)\
        .filter(ActivityLog.timestamp >= start_date)\
        .filter(ActivityLog.timestamp <= end_date)\
        .order_by(ActivityLog.timestamp.desc())\
        .all()

def delete_old_logs(days=30):
    """Delete logs older than specified days"""
    cutoff_date = datetime.now(ist) - timedelta(days=days)
    logs = ActivityLog.query.filter(ActivityLog.timestamp < cutoff_date).all()
    for log in logs:
        db.session.delete(log)
    db.session.commit()
    return len(logs)

def get_log_stats(user_id):
    """Get log statistics for a user"""
    total = ActivityLog.query.filter_by(user_id=user_id).count()
    
    # Get latest activity
    latest = ActivityLog.query.filter_by(user_id=user_id)\
        .order_by(ActivityLog.timestamp.desc()).first()
    
    return {
        'total_logs': total,
        'latest_activity': latest.timestamp if latest else None,
        'latest_action': latest.action if latest else None
    }