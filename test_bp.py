"""
Simple test endpoint to check session status
"""
from flask import Blueprint, jsonify, session

test_bp = Blueprint('test', __name__)

@test_bp.route('/session-status')
def session_status():
    """Show current session data for debugging"""
    return jsonify({
        'has_user_id': 'user_id' in session,
        'user_id': session.get('user_id'),
        'session_data': dict(session),
        'permanent': session.permanent,
        'modified': session.modified
    })
