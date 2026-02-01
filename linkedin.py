"""
LinkedIn Profile Analyzer Blueprint
Flask routes for LinkedIn profile analysis feature
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from linkedin_scraper import scrape_linkedin_profile, get_profile_summary, validate_linkedin_url
from linkedin_analysis import analyze_linkedin_profile
import time

linkedin_bp = Blueprint('linkedin', __name__)


@linkedin_bp.route('/')
def index():
    """LinkedIn analyzer main page"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('linkedin_analyzer.html')


@linkedin_bp.route('/analyze', methods=['POST'])
def analyze():
    """Analyze LinkedIn profile from URL or manual input"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Get form data
    linkedin_url = request.form.get('linkedin_url', '').strip()
    manual_headline = request.form.get('headline', '').strip()
    manual_about = request.form.get('about', '').strip()
    current_role = request.form.get('current_role', '').strip()
    industry = request.form.get('industry', '').strip()
    
    # Initialize profile data
    profile_data = {
        'success': False,
        'headline': manual_headline,
        'about': manual_about,
        'experience': '',
        'education': '',
        'skills': [],
        'full_name': '',
        'error': None
    }
    
    # Try to scrape if URL provided
    if linkedin_url:
        if validate_linkedin_url(linkedin_url):
            scraped_data = scrape_linkedin_profile(linkedin_url)
            
            if scraped_data['success']:
                # Use scraped data, but allow manual override
                profile_data['success'] = True
                profile_data['headline'] = manual_headline or scraped_data['headline']
                profile_data['about'] = manual_about or scraped_data['about']
                profile_data['experience'] = scraped_data['experience']
                profile_data['education'] = scraped_data['education']
                profile_data['skills'] = scraped_data['skills']
                profile_data['full_name'] = scraped_data['full_name']
            else:
                # Scraping failed, show error and use manual data
                if scraped_data['error']:
                    flash(f"Note: {scraped_data['error']}", 'warning')
                profile_data['error'] = scraped_data['error']
        else:
            flash('Invalid LinkedIn URL format. Please use manual input below.', 'error')
            profile_data['error'] = 'Invalid LinkedIn URL'
    
    # Check if we have enough data to analyze
    combined_text = get_profile_summary(profile_data)
    
    if not combined_text or len(combined_text) < 20:
        flash('Please provide either a valid LinkedIn URL or manually enter your headline and about section.', 'error')
        return redirect(url_for('linkedin.index'))
    
    # Store in session for loading page
    session['linkedin_url'] = linkedin_url
    session['linkedin_data'] = profile_data
    session['linkedin_role'] = current_role
    session['linkedin_industry'] = industry
    
    # Redirect to loading page
    return redirect(url_for('linkedin.loading'))


@linkedin_bp.route('/loading')
def loading():
    """Loading screen for LinkedIn analysis"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if 'linkedin_data' not in session:
        return redirect(url_for('linkedin.index'))
    
    return render_template('loading.html', analysis_type='linkedin')


@linkedin_bp.route('/process')
def process():
    """Process LinkedIn analysis (called from loading screen)"""
    if 'user_id' not in session or 'linkedin_data' not in session:
        return redirect(url_for('auth.login'))
    
    # Get data from session
    profile_data = session.get('linkedin_data', {})
    linkedin_url = session.get('linkedin_url', '')
    current_role = session.get('linkedin_role', '')
    industry = session.get('linkedin_industry', '')
    
    # Perform analysis
    analysis = analyze_linkedin_profile(
        linkedin_url=linkedin_url,
        profile_text=get_profile_summary(profile_data),
        headline=profile_data.get('headline', ''),
        about=profile_data.get('about', ''),
        experience=profile_data.get('experience', ''),
        education=profile_data.get('education', ''),
        skills=profile_data.get('skills', []),
        current_role=current_role,
        industry=industry
    )
    
    # Add profile name to analysis
    analysis['profile_name'] = profile_data.get('full_name', 'Your Profile')
    analysis['linkedin_url'] = linkedin_url
    analysis['current_role'] = current_role
    analysis['industry'] = industry
    
    # Store results in session
    session['linkedin_analysis'] = analysis
    
    # Redirect to results
    return redirect(url_for('linkedin.results'))


@linkedin_bp.route('/results')
def results():
    """Display LinkedIn analysis results"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    analysis = session.get('linkedin_analysis')
    
    if not analysis:
        flash('No analysis data found. Please analyze your profile first.', 'error')
        return redirect(url_for('linkedin.index'))
    
    return render_template('linkedin_results.html', analysis=analysis)
