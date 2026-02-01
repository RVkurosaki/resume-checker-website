"""
Enhanced LinkedIn Profile Analysis Module
Professional-grade analysis with detailed scoring, visibility optimization, and sample content generation
"""
import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv
import time

load_dotenv()

MOCK_AI = os.getenv('MOCK_AI', 'True') == 'True'


def validate_linkedin_url(url: str) -> bool:
    """Validate if the URL is a LinkedIn profile URL"""
    if not url:
        return False
    
    url = url.strip()
    
    if 'linkedin.com' not in url.lower():
        return False
    
    linkedin_patterns = [
        r'linkedin\.com/in/[\w\-]+',
        r'linkedin\.com/pub/[\w\-]+',
        r'www\.linkedin\.com/in/[\w\-]+',
        r'www\.linkedin\.com/pub/[\w\-]+'
    ]
    
    return any(re.search(pattern, url.lower()) for pattern in linkedin_patterns)


def analyze_linkedin_profile(linkedin_url: str = '', profile_text: str = '', headline: str = '', 
                            about: str = '', experience: str = '', education: str = '',
                            skills: list = None, current_role: str = '', industry: str = '') -> dict:
    """
    Enhanced LinkedIn profile analysis with detailed scoring and 6-point comprehensive review
    
    Args:
        linkedin_url: LinkedIn profile URL
        profile_text: Combined profile information
        headline: LinkedIn headline (optional, separate field)
        about: About/Summary section (optional, separate field)
        experience: Experience section text
        education: Education section text
        skills: List of skills
        current_role: Current job title
        industry: Industry/field
    
    Returns:
        dict with comprehensive analysis results including:
            - overall_rating (0-10)
            - section_feedback (dict with feedback for each section)
            - keyword_suggestions
            - actionable_improvements
            - industry_positioning
            - final_summary
    """
    # Validate LinkedIn URL
    url_valid = validate_linkedin_url(linkedin_url) if linkedin_url else False
    
    # Combine all text sources
    all_text = ' '.join(filter(None, [profile_text, headline, about, experience, education])).strip()
    
    # Add skills to text
    if skills:
        all_text += ' ' + ' '.join(skills)
    
    # If we have a valid URL but no content, provide helpful minimal analysis
    if url_valid and (not all_text or len(all_text) < 10):
        return get_minimal_analysis(has_url=True)
    
    # If no URL and no meaningful content
    if not url_valid and (not all_text or len(all_text) < 10):
        return get_minimal_analysis(has_url=False)
    
    # We have enough data to analyze
    if MOCK_AI:
        return get_enhanced_mock_analysis(
            profile_text=all_text,
            headline=headline,
            about=about,
            experience=experience,
            education=education,
            skills=skills or [],
            current_role=current_role,
            industry=industry
        )
    
    return analyze_with_chatgpt_enhanced(all_text, headline, about, current_role, industry)



def get_minimal_analysis(has_url: bool = False) -> dict:
    """Return enhanced minimal analysis when no profile data provided"""
    
    # If user provided URL, give them credit for that and provide helpful starting scores
    profile_score = 25 if has_url else 0
    completeness_score = 20 if has_url else 0
    
    # Provide actionable baseline
    strengths = []
    if has_url:
        strengths.append("LinkedIn profile URL provided - good first step!")
        strengths.append("Profile exists and is accessible")
    
    improvements = [
        'Add your complete LinkedIn headline for detailed analysis (30+ characters recommended)',
        'Paste your About/Summary section (150+ words for best results)',
        'Include specific achievements with metrics (e.g., "Increased revenue by 25%")',
        'List your key technical skills and industry expertise',
        'Add your current role and industry for personalized recommendations'
    ]
    
    if not has_url:
        improvements.insert(0, 'Provide your LinkedIn profile URL to enable analysis')
        strengths = ['Ready to analyze your LinkedIn profile - just add your information above']
    
    return {
        # Core scores
        'profile_score': profile_score,
        'completeness_score': completeness_score,
        'branding_score': 0,
        'optimization_score': 0,
        
        # NEW: Detailed category scores
        'headline_score': 0,
        'about_score': 0,
        'visibility_score': 15 if has_url else 0,
        'engagement_score': 0,
        
        # Analysis sections
        'headline_quality': 'Not provided - add your headline for analysis',
        'about_quality': 'Not provided - paste your About section for detailed review',
        'visibility_rating': 'Basic' if has_url else 'Unknown',
        
        # Recommendations
        'strengths': strengths,
        'improvements': improvements,
        
        # NEW: Keyword recommendations
        'keywords_to_add': [
            'Leadership',
            'Strategy',
            'Innovation',
            'Results-Driven',
            'Industry Expertise',
            'Team Collaboration',
            'Problem Solving',
            'Data-Driven'
        ],
        
        # NEW: Sample content
        'sample_headlines': [
            'Your Role | Key Skill | Value Proposition',
            'Industry Expert | Problem Solver | Innovation Driver',
            'Experienced Professional | Passionate About [Your Field] | Helping Teams Succeed'
        ],
        'sample_summary_points': [
            'Start with a compelling hook about your unique value',
            'Highlight X years of experience in your field',
            'Showcase specific achievements with measurable results',
            'List 3-4 core competencies',
            'Express your professional passion and goals',
            'Include a call-to-action to connect'
        ],
        
        # NEW: Completeness checklist
        'completeness_checklist': {
            'has_professional_headline': False,
            'has_detailed_summary': False,
            'has_experience_metrics': False,
            'has_sufficient_keywords': False,
            'has_custom_url': has_url
        },
        
        # NEW: Benchmarking
        'percentile_rank': 20 if has_url else 0,
        'visibility_multiplier': 5.0,  # Huge potential for improvement
        
        'summary': f'{"LinkedIn profile URL detected. " if has_url else ""}Add your headline, about section, and experience details to receive a comprehensive professional analysis with personalized recommendations and sample content.'
    }


def get_enhanced_mock_analysis(profile_text: str, headline: str = '', about: str = '', 
                               experience: str = '', education: str = '', skills: list = None,
                               current_role: str = '', industry: str = '') -> dict:
    """Generate enhanced mock LinkedIn analysis"""
    text_lower = profile_text.lower()
    word_count = len(profile_text.split())
    
    # Analyze headline
    headline_text = headline or profile_text.split('\n')[0] if '\n' in profile_text else profile_text[:100]
    headline_score = analyze_headline_quality(headline_text, current_role)
    
    # Analyze about section
    about_text = about or profile_text
    about_score = analyze_about_quality(about_text)
    
    # Calculate completeness (enhanced)
    completeness = 0
    checklist = {
        'has_professional_headline': len(headline_text) > 30,
        'has_detailed_summary': word_count > 80,
        'has_experience_metrics': bool(re.search(r'\d+%|\d+\+|increased|improved|reduced', text_lower)),
        'has_sufficient_keywords': len(re.findall(r'\b(expert|specialist|professional|certified|experienced)\b', text_lower)) >= 2,
        'has_custom_url': True  # Assume true if analyzing
    }
    
    for check in checklist.values():
        if check:
            completeness += 20
    
    # Calculate branding score
    branding = 0
    if any(word in text_lower for word in ['passionate', 'dedicated', 'experienced', 'expert', 'specialist']):
        branding += 25
    if word_count >= 100:
        branding += 25
    if any(char.isdigit() for char in profile_text):  # Has metrics
        branding += 30
    if 'help' in text_lower or 'solve' in text_lower or 'deliver' in text_lower:
        branding += 20
    
    # Calculate optimization score (visibility)
    optimization = 0
    action_verbs = ['develop', 'lead', 'manage', 'create', 'build', 'design', 'implement', 'drive', 'optimize']
    if any(verb in text_lower for verb in action_verbs):
        optimization += 30
    if re.search(r'\d+\s*(?:years?|months?)', text_lower):
        optimization += 20
    keywords_count = sum(1 for word in ['technical', 'business', 'strategy', 'innovation', 'growth', 'digital'] 
                        if word in text_lower)
    optimization += min(keywords_count * 10, 50)
    
    # NEW: Engagement potential score
    engagement = calculate_engagement_score(profile_text)
    
    # NEW: Visibility score (SEO-focused)
    visibility = calculate_visibility_score(profile_text, headline_text, about_text)
    
    # Overall score
    profile_score = int((headline_score + about_score + completeness + branding + optimization + visibility + engagement) / 7)
    
    # Generate strengths
    strengths = []
    if completeness >= 70:
        strengths.append("Profile sections are well-filled with key information")
    if headline_score >= 70:
        strengths.append("Headline effectively communicates value proposition")
    if branding >= 60:
        strengths.append("Strong professional branding and storytelling elements")
    if optimization >= 70:
        strengths.append("Good use of keywords and action verbs for visibility")
    if engagement >= 70:
        strengths.append("Profile content is engaging and results-oriented")
    if not strengths:
        strengths.append("Profile has been created - foundation established")
    
    # Generate improvements
    improvements = []
    if headline_score < 70:
        improvements.append("Enhance headline with specific skills and value proposition")
    if about_score < 70:
        improvements.append("Expand About section with compelling career narrative (aim for 150+ words)")
    if visibility < 70:
        improvements.append("Add industry-specific keywords to improve search visibility by 3-5x")
    if not re.search(r'\d+%|\d+x|increased|grew|reduced', profile_text):
        improvements.append("Include quantifiable achievements (e.g., 'Increased revenue by 25%')")
    if optimization < 60:
        improvements.append("Use more action verbs (led, built, designed) to strengthen impact")
    if engagement < 60:
        improvements.append("Add call-to-action elements to increase profile engagement")
    
    # NEW: Generate keyword recommendations
    keywords = generate_keyword_recommendations(current_role, industry, profile_text)
    
    # NEW: Generate sample headlines
    sample_headlines = generate_sample_headlines(current_role, industry)
    
    # NEW: Generate sample summary points
    sample_summary = generate_sample_summary_points(current_role, industry)
    
    # NEW: Calculate benchmarking
    percentile = calculate_percentile_rank(profile_score)
    visibility_mult = calculate_visibility_multiplier(visibility)
    
    # Determine quality labels
    headline_quality = "Excellent" if headline_score >= 80 else "Good" if headline_score >= 60 else "Needs improvement"
    about_quality = "Excellent" if about_score >= 80 else "Good" if about_score >= 60 else "Needs expansion"
    visibility_rating = "High" if visibility >= 75 else "Moderate" if visibility >= 50 else "Low"
    
    summary = f"LinkedIn profile scores {profile_score}/100 (Top {100-percentile}% of professionals). "
    if profile_score >= 75:
        summary += "Excellent professional presence - fine-tune for maximum impact."
    elif profile_score >= 60:
        summary += "Strong foundation - enhance visibility and keyword optimization for better reach."
    elif profile_score >= 40:
        summary += "Good start - expand key sections and add more specific achievements."
    else:
        summary += "Significant opportunity for improvement - focus on completeness and compelling content."
    
    # NEW: Calculate overall rating (0-10 scale)
    overall_rating = calculate_overall_rating(profile_score)
    
    # NEW: Generate section-by-section feedback
    section_feedback = generate_section_feedback(
        headline_text, about_text, experience, education, skills or [],
        headline_score, about_score
    )
    
    # NEW: Generate industry positioning
    positioning = generate_industry_positioning(profile_score, percentile, visibility_mult, current_role, industry)
    
    # NEW: Generate final motivational summary
    final_summary = generate_final_summary(profile_score, percentile, improvements)
    
    return {
        # Core scores
        'profile_score': profile_score,
        'completeness_score': min(completeness, 100),
        'branding_score': min(branding, 100),
        'optimization_score': min(optimization, 100),
        
        # NEW: Detailed category scores
        'headline_score': headline_score,
        'about_score': about_score,
        'visibility_score': visibility,
        'engagement_score': engagement,
        
        # Analysis sections
        'headline_quality': headline_quality,
        'about_quality': about_quality,
        'visibility_rating': visibility_rating,
        
        # Current content
        'current_headline': headline_text[:150] if headline_text else "No headline provided",
        'current_about_preview': about_text[:200] if about_text else "No about section provided",
        
        # Recommendations
        'strengths': strengths[:5],
        'improvements': improvements[:6],
        
        # NEW: Keyword recommendations
        'keywords_to_add': keywords,
        
        # NEW: Sample content
        'sample_headlines': sample_headlines,
        'sample_summary_points': sample_summary,
        
        # NEW: Completeness checklist
        'completeness_checklist': checklist,
        
        # NEW: Benchmarking
        'percentile_rank': percentile,
        'visibility_multiplier': visibility_mult,
        
        # NEW: 6-POINT COMPREHENSIVE REVIEW
        'overall_rating': overall_rating,  # 0-10 scale
        'section_feedback': section_feedback,  # Detailed section analysis
        'keyword_suggestions': keywords,  # Industry keywords
        'actionable_improvements': improvements[:8],  # Specific action items
        'industry_positioning': positioning,  # Comparison to peers
        'final_summary': final_summary,  # Motivational overview
        
        'summary': summary
    }


def analyze_headline_quality(headline: str, current_role: str = '') -> int:
    """Analyze LinkedIn headline quality (0-100)"""
    if not headline or len(headline) < 10:
        return 0
    
    score = 0
    headline_lower = headline.lower()
    
    # Length check (30-120 characters is ideal)
    if 30 <= len(headline) <= 120:
        score += 25
    elif 20 <= len(headline) < 30:
        score += 15
    
    # Has role/title
    if current_role.lower() in headline_lower or any(title in headline_lower for title in ['engineer', 'manager', 'developer', 'designer', 'analyst', 'consultant', 'director']):
        score += 20
    
    # Has skills or technologies
    if re.search(r'\b(python|java|react|aws|sql|marketing|sales|design|data|ai|ml)\b', headline_lower):
        score += 20
    
    # Has value proposition words
    value_words = ['helping', 'building', 'creating', 'driving', 'leading', 'expert', 'specialist', 'focused on']
    if any(word in headline_lower for word in value_words):
        score += 20
    
    # Has separators (|, •, –) indicating structured headline
    if re.search(r'[|•–]', headline):
        score += 15
    
    return min(score, 100)


def analyze_about_quality(about_text: str) -> int:
    """Analyze About/Summary section quality (0-100)"""
    if not about_text or len(about_text) < 20:
        return 0
    
    score = 0
    word_count = len(about_text.split())
    about_lower = about_text.lower()
    
    # Length assessment
    if word_count >= 150:
        score += 30
    elif word_count >= 80:
        score += 20
    elif word_count >= 40:
        score += 10
    
    # Has first-person narrative (engaging storytelling)
    if re.search(r'\b(i am|i\'ve|i help|my|i specialize)\b', about_lower):
        score += 15
    
    # Has achievements/metrics
    if re.search(r'\d+%|\d+x|\d+ years|increased|grew|achieved', about_lower):
        score += 20
    
    # Has call to action or contact info
    if any(word in about_lower for word in ['connect', 'reach out', 'contact', 'let\'s', 'email', 'message']):
        score += 10
    
    # Has industry keywords
    if len(re.findall(r'\b(experience|expertise|specialist|professional|skilled|certified)\b', about_lower)) >= 2:
        score += 15
    
    # Paragraph structure (has line breaks indicating organization)
    if about_text.count('\n') >= 2:
        score += 10
    
    return min(score, 100)


def calculate_engagement_score(profile_text: str) -> int:
    """Calculate engagement potential (0-100)"""
    score = 0
    text_lower = profile_text.lower()
    
    # Has call-to-action language
    cta_words = ['connect', 'collaborate', 'reach out', 'let\'s talk', 'get in touch', 'message me']
    if any(word in text_lower for word in cta_words):
        score += 30
    
    # Has results/impact language
    impact_words = ['achieved', 'delivered', 'increased', 'improved', 'led', 'grew', 'built']
    score += min(sum(1 for word in impact_words if word in text_lower) * 10, 40)
    
    # Has personality (not just dry facts)
    personality_indicators = ['passionate', 'love', 'enjoy', 'thrive', 'excited', 'enthusiastic']
    if any(word in text_lower for word in personality_indicators):
        score += 20
    
    # Readability (not too long sentences)
    sentences = re.split(r'[.!?]+', profile_text)
    avg_sentence_length = sum(len(s.split()) for s in sentences) / max(len(sentences), 1)
    if 10 <= avg_sentence_length <= 20:
        score += 10
    
    return min(score, 100)


def calculate_visibility_score(profile_text: str, headline: str, about: str) -> int:
    """Calculate search visibility / SEO score (0-100)"""
    score = 0
    combined_text = ' '.join([profile_text, headline, about]).lower()
    
    # Keyword density
    total_words = len(combined_text.split())
    if total_words > 100:
        score += 20
    elif total_words > 50:
        score += 10
    
    # Has role-specific keywords
    role_keywords = ['engineer', 'developer', 'manager', 'designer', 'analyst', 'consultant', 'director', 'specialist']
    if any(keyword in combined_text for keyword in role_keywords):
        score += 20
    
    # Has technical/industry keywords (these improve search ranking)
    tech_keywords = ['leadership', 'strategy', 'data', 'digital', 'cloud', 'software', 'product', 'project']
    keyword_count = sum(1 for keyword in tech_keywords if keyword in combined_text)
    score += min(keyword_count * 8, 32)
    
    # Has location indicators
    if re.search(r'\b(remote|based in|located|area|region)\b', combined_text):
        score += 8
    
    # Headline has keywords (most important for SEO)
    if headline and len(headline.split()) >= 5:
        score += 20
    
    return min(score, 100)


def generate_keyword_recommendations(current_role: str, industry: str, existing_text: str) -> list:
    """Generate keyword recommendations based on role and industry"""
    existing_lower = existing_text.lower()
    keywords = []
    
    # Generic high-value keywords
    base_keywords = ['Leadership', 'Strategy', 'Innovation', 'Digital Transformation', 'Cross-functional Collaboration']
    
    # Role-specific keywords
    role_keywords = {
        'engineer': ['Software Development', 'System Architecture', 'Code Review', 'CI/CD', 'Agile/Scrum'],
        'developer': ['Full-Stack Development', 'API Design', 'Database Optimization', 'Cloud Services', 'Version Control'],
        'manager': ['Team Leadership', 'Project Management', 'Stakeholder Communication', 'Budget Management', 'Process Improvement'],
        'designer': ['User Experience (UX)', 'User Interface (UI)', 'Design Thinking', 'Prototyping', 'Visual Design'],
        'analyst': ['Data Analysis', 'Business Intelligence', 'Statistical Modeling', 'Data Visualization', 'Insights Generation'],
        'consultant': ['Client Relations', 'Solution Architecture', 'Change Management', 'Requirements Gathering', 'Strategic Planning']
    }
    
    # Add role-specific keywords
    role_lower = current_role.lower() if current_role else ''
    for role_key, role_kws in role_keywords.items():
        if role_key in role_lower:
            for kw in role_kws:
                if kw.lower() not in existing_lower:
                    keywords.append(kw)
            break
    
    # Add base keywords if not present
    for kw in base_keywords:
        if kw.lower() not in existing_lower and len(keywords) < 8:
            keywords.append(kw)
    
    return keywords[:8]


def generate_sample_headlines(current_role: str, industry: str) -> list:
    """Generate sample LinkedIn headlines"""
    role = current_role or "Professional"
    
    samples = [
        f"{role} | Driving Innovation & Results | Passionate About Technology & Growth",
        f"Experienced {role} | Helping Organizations Scale | Expert in Digital Solutions",
        f"{role} Specializing in [Your Key Skill] | Building High-Performance Teams | [Industry] Leader"
    ]
    
    # Add role-specific samples
    if 'engineer' in current_role.lower():
        samples.append("Senior Software Engineer | Full-Stack Expert (React, Node.js, AWS) | Building Scalable Applications")
        samples.append("Software Engineer | Cloud Architecture Specialist | Passionate About Clean Code & Innovation")
    elif 'manager' in current_role.lower():
        samples.append("Product Manager | Driving Data-Driven Decisions | Launching Products That Users Love")
        samples.append("Engineering Manager | Building & Scaling High-Performance Teams | Agile Enthusiast")
    elif 'designer' in current_role.lower():
        samples.append("UX/UI Designer | Creating Delightful User Experiences | Design Systems Expert")
        samples.append("Product Designer | User-Centered Design Advocate | Turning Ideas Into Beautiful Products")
    
    return samples[:5]


def generate_sample_summary_points(current_role: str, industry: str) -> list:
    """Generate sample summary/about section points"""
    samples = [
        "Start with a compelling hook about your passion or unique value proposition",
        f"Experienced {current_role or 'professional'} with [X] years of expertise in [key skill/industry]",
        "Proven track record of [specific achievement with metrics - e.g., 'increasing efficiency by 40%']",
        "Specializing in [your core competencies - list 3-4 key skills]",
        "Passionate about [what drives you professionally - innovation, problem-solving, mentoring, etc.]",
        "Looking to [your goal - e.g., 'connect with fellow industry leaders' or 'explore new opportunities in...']",
        "Let's connect! I'm always open to discussing [relevant topics in your field]"
    ]
    
    return samples[:7]


def calculate_percentile_rank(profile_score: int) -> int:
    """Calculate approximate percentile rank based on profile score"""
    if profile_score >= 90:
        return 95  # Top 5%
    elif profile_score >= 80:
        return 85  # Top 15%
    elif profile_score >= 70:
        return 70  # Top 30%
    elif profile_score >= 60:
        return 55  # Top 45%
    elif profile_score >= 50:
        return 40  # Top 60%
    else:
        return max(20, profile_score // 2)  # Lower ranges


def calculate_visibility_multiplier(visibility_score: int) -> float:
    """Calculate how much more visible profile could be"""
    if visibility_score >= 80:
        return 1.2  # Already highly visible
    elif visibility_score >= 60:
        return 2.0  # Could be 2x more visible
    elif visibility_score >= 40:
        return 3.5  # Could be 3-4x more visible
    else:
        return 5.0  # Could be 5x more visible


def calculate_overall_rating(profile_score: int) -> float:
    """Convert profile score (0-100) to overall rating (0-10)"""
    return round(profile_score / 10, 1)


def generate_section_feedback(headline: str, about: str, experience: str, 
                             education: str, skills: list, headline_score: int, 
                             about_score: int) -> dict:
    """Generate detailed feedback for each profile section"""
    feedback = {}
    
    # Headline feedback
    if headline_score >= 80:
        feedback['headline'] = {
            'score': headline_score,
            'rating': 'Excellent',
            'feedback': 'Your headline is compelling and effectively communicates your value proposition. It includes key skills and is well-structured.',
            'strength': 'Strong use of keywords and clear professional identity',
            'improvement': 'Consider A/B testing different headlines to maximize profile views'
        }
    elif headline_score >= 60:
        feedback['headline'] = {
            'score': headline_score,
            'rating': 'Good',
            'feedback': 'Your headline is decent but could be more impactful. Consider adding specific skills or value propositions.',
            'strength': 'Includes role information',
            'improvement': 'Add 2-3 key skills and a value proposition (e.g., "| Helping companies scale efficiently")'
        }
    else:
        feedback['headline'] = {
            'score': headline_score,
            'rating': 'Needs Improvement',
            'feedback': 'Your headline needs significant enhancement. It should be 30-120 characters and include your role, key skills, and value proposition.',
            'strength': 'Has basic structure',
            'improvement': 'Rewrite using this formula: [Role] | [Key Skills] | [Value Proposition]. Example: "Software Engineer | Python, AWS, React | Building scalable web applications"'
        }
    
    # About section feedback
    word_count = len(about.split()) if about else 0
    if about_score >= 80:
        feedback['about'] = {
            'score': about_score,
            'rating': 'Excellent',
            'feedback': f'Your About section is well-crafted with {word_count} words. It tells a compelling story and includes metrics.',
            'strength': 'Strong narrative with quantifiable achievements',
            'improvement': 'Ensure it ends with a clear call-to-action'
        }
    elif about_score >= 60:
        feedback['about'] = {
            'score': about_score,
            'rating': 'Good',
            'feedback': f'Your About section has {word_count} words and provides solid information, but could be more engaging.',
            'strength': 'Covers key professional information',
            'improvement': 'Add specific achievements with numbers (e.g., "increased revenue by 30%") and inject more personality'
        }
    else:
        feedback['about'] = {
            'score': about_score,
            'rating': 'Needs Expansion',
            'feedback': f'Your About section is too brief ({word_count} words). Aim for 150-300 words to fully showcase your value.',
            'strength': 'Space for significant improvement',
            'improvement': 'Write 3-4 paragraphs covering: (1) Who you are and what drives you, (2) Key achievements with metrics, (3) Core competencies, (4) What you\'re looking for / call-to-action'
        }
    
    # Experience feedback
    has_experience = len(experience) > 50 if experience else False
    if has_experience:
        feedback['experience'] = {
            'score': 75,
            'rating': 'Good',
            'feedback': 'Experience section is populated with work history.',
            'strength': 'Shows professional background',
            'improvement': 'For each role, use bullet points with metrics (e.g., "Led team of 5 engineers, delivered 20+ features")'
        }
    else:
        feedback['experience'] = {
            'score': 30,
            'rating': 'Limited',
            'feedback': 'Experience section appears incomplete or brief.',
            'strength': 'Opportunity to showcase achievements',
            'improvement': 'Add detailed descriptions for each role with bullet points highlighting key accomplishments and metrics'
        }
    
    # Education feedback
    has_education = len(education) > 20 if education else False
    if has_education:
        feedback['education'] = {
            'score': 80,
            'rating': 'Complete',
            'feedback': 'Education section is filled out.',
            'strength': 'Shows educational background',
            'improvement': 'Add relevant coursework, honors, or activities if applicable'
        }
    else:
        feedback['education'] = {
            'score': 40,
            'rating': 'Incomplete',
            'feedback': 'Education section needs more detail.',
            'strength': 'Basic structure exists',
            'improvement': 'Add your degree, institution, graduation year, and any relevant achievements'
        }
    
    # Skills feedback
    skill_count = len(skills) if skills else 0
    if skill_count >= 10:
        feedback['skills'] = {
            'score': 85,
            'rating': 'Excellent',
            'feedback': f'You have {skill_count} skills listed, which is great for visibility.',
            'strength': 'Comprehensive skills coverage',
            'improvement': 'Ensure your top 3-5 skills have 10+ endorsements by asking colleagues'
        }
    elif skill_count >= 5:
        feedback['skills'] = {
            'score': 65,
            'rating': 'Good',
            'feedback': f'You have {skill_count} skills listed. Aim for 10-15 relevant skills.',
            'strength': 'Core skills identified',
            'improvement': 'Add 5-8 more industry-relevant skills and get endorsements'
        }
    else:
        feedback['skills'] = {
            'score': 35,
            'rating': 'Insufficient',
            'feedback': f'Only {skill_count} skills listed. LinkedIn allows up to 50 skills.',
            'strength': 'Significant opportunity for improvement',
            'improvement': 'Add at least 10-15 core skills relevant to your industry and role. This dramatically improves search visibility.'
        }
    
    return feedback


def generate_industry_positioning(profile_score: int, percentile: int, 
                                 visibility_mult: float, current_role: str, 
                                 industry: str) -> str:
    """Generate industry positioning analysis"""
    role_text = f" in the {industry} industry" if industry else ""
    role_title = current_role if current_role else "your field"
    
    positioning_text = f"""## Industry Positioning Analysis

Your LinkedIn profile currently ranks in the **top {100-percentile}%** of professionals{role_text}. 

### Visibility Potential
With optimization, your profile visibility could increase by **{visibility_mult}x**, meaning you could appear in {int(visibility_mult)} times more recruiter and hiring manager searches.

### Competitive Standing
"""
    
    if profile_score >= 80:
        positioning_text += f"""You're in the **elite tier** for {role_title} profiles. Your profile stands out and effectively positions you as a top professional. Continue fine-tuning to maintain this competitive edge.

**Key Competitive Advantages:**
- Strong keyword optimization for search visibility
- Compelling personal branding and storytelling  
- Complete profile sections with detailed information
- Professional presentation that builds credibility
"""
    elif profile_score >= 65:
        positioning_text += f"""You're in the **strong performer** tier for {role_title} profiles. You're ahead of most professionals, but there's room to reach elite status.

**To Reach Top 10%:**
- Enhance keyword density for better search ranking
- Add more quantified achievements and metrics
- Expand About section with compelling narrative
- Get 5-10 endorsements on top skills
"""
    elif profile_score >= 45:
        positioning_text += f"""You're in the **solid foundation** tier for {role_title} profiles. You have the basics covered but need optimization to compete for top opportunities.

**To Reach Top 30%:**
- Rewrite headline with role + skills + value proposition
- Expand About section to 150+ words with achievements
- Add industry-specific keywords throughout profile
- Complete all profile sections (experience, education, skills)
"""
    else:
        positioning_text += f"""You're in the **significant opportunity** tier for {role_title} profiles. Most professionals have more optimized profiles, but this means you have huge upside potential.

**Quick Wins to Jump to Top 50%:**
- Create a professional headline (30+ characters)
- Write a 150+ word About section with your story
- Add 10+ relevant skills
- Include metrics in experience descriptions
- Upload a professional profile photo (if missing)
"""
    
    return positioning_text


def generate_final_summary(profile_score: int, percentile: int, improvements: list) -> str:
    """Generate motivational final summary with next steps"""
    
    if profile_score >= 80:
        summary = f"""## 🌟 Congratulations! You're in the Top {100-percentile}%

Your LinkedIn profile is **excellent** and positions you as a standout professional. You've done the hard work of building a strong online presence.

### Next Steps to Maintain Excellence:
1. **Stay Active**: Share industry insights, engage with posts, and publish articles to boost visibility
2. **Network Strategically**: Connect with 10-15 new professionals in your field each week
3. **Gather Recommendations**: Aim for 3-5 recommendations from colleagues or clients
4. **A/B Test**: Try variations of your headline and track profile views
5. **Keep Updated**: Refresh your profile quarterly with new achievements

### Your Competitive Edge
With your optimized profile, you're **{(100-percentile)*5}% more likely** to be contacted by recruiters compared to the average professional. Keep up the great work!
"""
    elif profile_score >= 60:
        summary = f"""## 💪 Strong Foundation - You're Almost There!

Your LinkedIn profile is **good** and you're in the top {100-percentile}% of professionals. With a few strategic improvements, you can reach elite status.

### Priority Action Items (Next 48 Hours):
"""
        for i, improvement in enumerate(improvements[:3], 1):
            summary += f"{i}. {improvement}\n"
        
        summary += f"""\n### The Impact
Implementing these changes could **double your profile visibility** and increase recruiter outreach by 40-60%.

### Mini Challenge
Can you dedicate 2 hours this week to LinkedIn optimization? The ROI on your career could be substantial. Set a calendar reminder right now!
"""
    else:
        summary = f"""## 🚀 Huge Opportunity Ahead!

Your LinkedIn profile has **significant room for growth**, which is actually exciting news! Every improvement you make will have a big impact.

### Your 7-Day LinkedIn Transformation Plan:

**Days 1-2: Foundation**
- Craft a compelling headline (use the samples provided)
- Write a 200-word About section telling your professional story

**Days 3-4: Content**
- Add bullet points with metrics to your top 3 work experiences
- List 10-15 relevant skills

**Days 5-6: Polish**
- Complete education section
- Ask 5 colleagues for skill endorsements

**Day 7: Visibility**
- Share an industry article with your thoughts
- Connect with 10 professionals in your field

### The Prize
A fully optimized profile could **increase your visibility by 5x** and open doors to opportunities you didn't even know existed. Many professionals have found their dream jobs simply by having a strong LinkedIn presence.

**Start today**—future you will be grateful! 🎯
"""
    
    return summary


def analyze_with_chatgpt_enhanced(profile_text: str, headline: str, about: str, 
                                  current_role: str, industry: str) -> dict:
    """Use ChatGPT for enhanced LinkedIn analysis (fallback to mock on failure)"""
    # Implementation would use OpenAI API similar to existing code
    # For now, fallback to enhanced mock analysis
    return get_enhanced_mock_analysis(profile_text, headline, about, 
                                     current_role=current_role, industry=industry)
