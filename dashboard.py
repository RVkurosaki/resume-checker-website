from flask import Blueprint, render_template, session, redirect, url_for
from analysis import analyze_resume_with_ai, get_job_roles

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    print(f"DEBUG: Session data: {dict(session)}")  # Debug log
    print(f"DEBUG: 'user_id' in session: {'user_id' in session}")  # Debug log
    if 'user_id' not in session:
        print("DEBUG: No user_id in session, redirecting to login")  # Debug log
        return redirect(url_for('auth.login'))
    job_roles = get_job_roles()
    print(f"DEBUG: Successfully loaded dashboard for user_id: {session.get('user_id')}")  # Debug log
    return render_template('dashboard.html', job_roles=job_roles)

@dashboard_bp.route('/loading')
def loading():
    """Show loading screen while analysis is processing"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('loading.html')

@dashboard_bp.route('/analyze')
def analyze():
    print(f"DEBUG /analyze: Session data: {dict(session)}")  # Debug log
    print(f"DEBUG /analyze: 'user_id' in session: {'user_id' in session}")  # Debug log
    print(f"DEBUG /analyze: 'resume_text' in session: {'resume_text' in session}")  # Debug log
    
    if 'user_id' not in session or 'resume_text' not in session:
        print(f"DEBUG /analyze: Missing required session data, redirecting to login")  # Debug log
        return redirect(url_for('auth.login'))
    
    text = session['resume_text']
    job_role = session.get('job_role', 'software_engineer')
    
    # Get comprehensive AI analysis
    analysis = analyze_resume_with_ai(text, job_role)
    
    # Add job role info to analysis
    from analysis import JOB_ROLES, get_interview_tips
    role_info = JOB_ROLES.get(job_role, JOB_ROLES['software_engineer'])
    analysis['job_role_title'] = role_info['title']
    
    # Add interview tips
    analysis['interview_tips'] = get_interview_tips(job_role)
    
    session['analysis'] = analysis
    return render_template('result.html', analysis=analysis)