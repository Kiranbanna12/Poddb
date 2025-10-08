"""
Database queries for authentication system
"""
import time
import secrets
import string
from typing import Optional, Dict, List, Tuple
from .db import get_db_connection

def generate_token(length: int = 32) -> str:
    """Generate a secure random token"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# ============================================================================
# USER QUERIES
# ============================================================================

def create_user(username: str, email: str, password_hash: str, full_name: Optional[str] = None) -> int:
    """Create a new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    current_time = int(time.time())
    cursor.execute('''
        INSERT INTO users (username, email, password_hash, full_name, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, email, password_hash, full_name, current_time, current_time))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return user_id

def get_user_by_email(email: str) -> Optional[Dict]:
    """Get user by email"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_user_by_username(username: str) -> Optional[Dict]:
    """Get user by username"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_user_by_id(user_id: int) -> Optional[Dict]:
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def check_username_exists(username: str) -> bool:
    """Check if username already exists"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM users WHERE username = ?', (username,))
    count = cursor.fetchone()['count']
    conn.close()
    
    return count > 0

def check_email_exists(email: str) -> bool:
    """Check if email already exists"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as count FROM users WHERE email = ?', (email,))
    count = cursor.fetchone()['count']
    conn.close()
    
    return count > 0

def update_user_email_verified(user_id: int, verified: bool = True) -> bool:
    """Update user email verified status"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users 
        SET email_verified = ?, updated_at = ?
        WHERE id = ?
    ''', (1 if verified else 0, int(time.time()), user_id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success

def update_user_last_login(user_id: int) -> bool:
    """Update user's last login timestamp"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users 
        SET last_login = ?
        WHERE id = ?
    ''', (int(time.time()), user_id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success

def update_user_password(user_id: int, new_password_hash: str) -> bool:
    """Update user password"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users 
        SET password_hash = ?, updated_at = ?
        WHERE id = ?
    ''', (new_password_hash, int(time.time()), user_id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success

def update_user_profile(user_id: int, data: Dict) -> bool:
    """Update user profile data"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build dynamic update query
    fields = []
    values = []
    
    allowed_fields = ['full_name', 'bio', 'avatar_path']
    for field in allowed_fields:
        if field in data:
            fields.append(f'{field} = ?')
            values.append(data[field])
    
    if not fields:
        conn.close()
        return False
    
    fields.append('updated_at = ?')
    values.append(int(time.time()))
    values.append(user_id)
    
    query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
    cursor.execute(query, values)
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success

def update_user_email(user_id: int, new_email: str) -> bool:
    """Update user email (sets email_verified to 0)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users 
        SET email = ?, email_verified = 0, updated_at = ?
        WHERE id = ?
    ''', (new_email, int(time.time()), user_id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success

def soft_delete_user(user_id: int) -> bool:
    """Soft delete user (set is_active to 0)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users 
        SET is_active = 0, updated_at = ?
        WHERE id = ?
    ''', (int(time.time()), user_id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success

def ban_user(user_id: int, reason: str) -> bool:
    """Ban a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users 
        SET is_banned = 1, ban_reason = ?, updated_at = ?
        WHERE id = ?
    ''', (reason, int(time.time()), user_id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success

def unban_user(user_id: int) -> bool:
    """Unban a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users 
        SET is_banned = 0, ban_reason = NULL, updated_at = ?
        WHERE id = ?
    ''', (int(time.time()), user_id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success

def update_user_role(user_id: int, role: str) -> bool:
    """Update user role"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE users 
        SET role = ?, updated_at = ?
        WHERE id = ?
    ''', (role, int(time.time()), user_id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success

def get_all_users(page: int = 1, limit: int = 20, filters: Optional[Dict] = None) -> Tuple[List[Dict], int]:
    """Get paginated list of users with optional filters"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Build WHERE clause
    where_clauses = []
    params = []
    
    if filters:
        if filters.get('role'):
            where_clauses.append('role = ?')
            params.append(filters['role'])
        
        if filters.get('status') == 'active':
            where_clauses.append('is_active = 1 AND is_banned = 0')
        elif filters.get('status') == 'banned':
            where_clauses.append('is_banned = 1')
        elif filters.get('status') == 'inactive':
            where_clauses.append('is_active = 0')
        elif filters.get('status') == 'unverified':
            where_clauses.append('email_verified = 0')
        
        if filters.get('search'):
            where_clauses.append('(username LIKE ? OR email LIKE ? OR full_name LIKE ?)')
            search_term = f"%{filters['search']}%"
            params.extend([search_term, search_term, search_term])
    
    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""
    
    # Get total count
    cursor.execute(f'SELECT COUNT(*) as count FROM users {where_sql}', params)
    total = cursor.fetchone()['count']
    
    # Get paginated results
    offset = (page - 1) * limit
    params.extend([limit, offset])
    
    cursor.execute(f'''
        SELECT id, username, email, email_verified, full_name, avatar_path, role, 
               contribution_count, review_count, is_active, is_banned, ban_reason, 
               last_login, created_at
        FROM users 
        {where_sql}
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    ''', params)
    
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return users, total

# ============================================================================
# SESSION QUERIES
# ============================================================================

def create_session(user_id: int, expires_hours: int = 24, device_info: Optional[Dict] = None) -> str:
    """Create a new session"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    session_token = generate_token(64)
    current_time = int(time.time())
    expires = current_time + (expires_hours * 3600)
    
    cursor.execute('''
        INSERT INTO sessions (session_token, user_id, expires, device_info, ip_address, user_agent, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        session_token,
        user_id,
        expires,
        device_info.get('device') if device_info else None,
        device_info.get('ip') if device_info else None,
        device_info.get('user_agent') if device_info else None,
        current_time,
        current_time
    ))
    
    conn.commit()
    conn.close()
    
    return session_token

def get_session(session_token: str) -> Optional[Dict]:
    """Get session by token"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.*, u.id as user_id, u.username, u.email, u.role, u.is_active, u.is_banned
        FROM sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.session_token = ? AND s.expires > ?
    ''', (session_token, int(time.time())))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def delete_session(session_token: str) -> bool:
    """Delete a session"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success

def delete_user_sessions(user_id: int, except_token: Optional[str] = None) -> int:
    """Delete all sessions for a user (optionally except one)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if except_token:
        cursor.execute('DELETE FROM sessions WHERE user_id = ? AND session_token != ?', (user_id, except_token))
    else:
        cursor.execute('DELETE FROM sessions WHERE user_id = ?', (user_id,))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted_count

def get_user_sessions(user_id: int) -> List[Dict]:
    """Get all active sessions for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, session_token, device_info, ip_address, user_agent, created_at, updated_at, expires
        FROM sessions
        WHERE user_id = ? AND expires > ?
        ORDER BY created_at DESC
    ''', (user_id, int(time.time())))
    
    sessions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return sessions

def cleanup_expired_sessions() -> int:
    """Delete expired sessions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM sessions WHERE expires < ?', (int(time.time()),))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted_count

# ============================================================================
# VERIFICATION TOKEN QUERIES
# ============================================================================

def create_verification_token(identifier: str, token_type: str, expires_hours: int = 24) -> str:
    """Create a verification token"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    token = generate_token(48)
    current_time = int(time.time())
    expires = current_time + (expires_hours * 3600)
    
    cursor.execute('''
        INSERT INTO verification_tokens (identifier, token, expires, type, created_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (identifier, token, expires, token_type, current_time))
    
    conn.commit()
    conn.close()
    
    return token

def get_verification_token(token: str) -> Optional[Dict]:
    """Get verification token"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM verification_tokens 
        WHERE token = ? AND expires > ? AND used = 0
    ''', (token, int(time.time())))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def mark_token_used(token: str) -> bool:
    """Mark a verification token as used"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('UPDATE verification_tokens SET used = 1 WHERE token = ?', (token,))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success

def delete_user_tokens(identifier: str, token_type: Optional[str] = None) -> int:
    """Delete verification tokens for a user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if token_type:
        cursor.execute('DELETE FROM verification_tokens WHERE identifier = ? AND type = ?', (identifier, token_type))
    else:
        cursor.execute('DELETE FROM verification_tokens WHERE identifier = ?', (identifier,))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    return deleted_count

# ============================================================================
# LOGIN ATTEMPT QUERIES
# ============================================================================

def log_login_attempt(identifier: str, ip_address: Optional[str], success: bool) -> None:
    """Log a login attempt"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO login_attempts (identifier, ip_address, success, attempted_at)
        VALUES (?, ?, ?, ?)
    ''', (identifier, ip_address, 1 if success else 0, int(time.time())))
    
    conn.commit()
    conn.close()

def get_recent_failed_attempts(identifier: str, minutes: int = 15) -> int:
    """Get count of recent failed login attempts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cutoff_time = int(time.time()) - (minutes * 60)
    
    cursor.execute('''
        SELECT COUNT(*) as count 
        FROM login_attempts 
        WHERE identifier = ? AND success = 0 AND attempted_at > ?
    ''', (identifier, cutoff_time))
    
    count = cursor.fetchone()['count']
    conn.close()
    
    return count

def get_recent_failed_attempts_by_ip(ip_address: str, minutes: int = 15) -> int:
    """Get count of recent failed login attempts from an IP"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cutoff_time = int(time.time()) - (minutes * 60)
    
    cursor.execute('''
        SELECT COUNT(*) as count 
        FROM login_attempts 
        WHERE ip_address = ? AND success = 0 AND attempted_at > ?
    ''', (ip_address, cutoff_time))
    
    count = cursor.fetchone()['count']
    conn.close()
    
    return count

# ============================================================================
# ACTIVITY LOG QUERIES
# ============================================================================

def log_user_activity(user_id: int, action_type: str, action_details: Optional[str] = None, 
                      ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> None:
    """Log user activity"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO user_activity_logs (user_id, action_type, action_details, ip_address, user_agent, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, action_type, action_details, ip_address, user_agent, int(time.time())))
    
    conn.commit()
    conn.close()

def get_user_activity_logs(user_id: int, page: int = 1, limit: int = 50) -> Tuple[List[Dict], int]:
    """Get user activity logs"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get total count
    cursor.execute('SELECT COUNT(*) as count FROM user_activity_logs WHERE user_id = ?', (user_id,))
    total = cursor.fetchone()['count']
    
    # Get paginated results
    offset = (page - 1) * limit
    
    cursor.execute('''
        SELECT * FROM user_activity_logs 
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    ''', (user_id, limit, offset))
    
    logs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return logs, total

# ============================================================================
# EMAIL QUEUE QUERIES
# ============================================================================

def queue_email(recipient: str, subject: str, body: str) -> int:
    """Add email to queue"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO email_queue (recipient, subject, body, created_at)
        VALUES (?, ?, ?, ?)
    ''', (recipient, subject, body, int(time.time())))
    
    email_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return email_id

def get_pending_emails(limit: int = 10) -> List[Dict]:
    """Get pending emails from queue"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM email_queue 
        WHERE status = 'pending'
        ORDER BY created_at ASC
        LIMIT ?
    ''', (limit,))
    
    emails = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return emails

def mark_email_sent(email_id: int) -> bool:
    """Mark email as sent"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE email_queue 
        SET status = 'sent', sent_at = ?
        WHERE id = ?
    ''', (int(time.time()), email_id))
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    
    return success
