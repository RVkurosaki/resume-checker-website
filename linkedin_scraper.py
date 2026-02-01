"""
LinkedIn Profile Scraper Module
Scrapes public LinkedIn profile data for analysis
"""
import re
import time
import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
SCRAPING_ENABLED = os.getenv('LINKEDIN_SCRAPING_ENABLED', 'True') == 'True'
REQUEST_DELAY = int(os.getenv('LINKEDIN_REQUEST_DELAY', '2'))

# User agent to mimic browser request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}


def validate_linkedin_url(url: str) -> bool:
    """
    Validate if the URL is a LinkedIn profile URL
    
    Args:
        url: The URL to validate
        
    Returns:
        bool: True if valid LinkedIn profile URL
    """
    if not url:
        return False
    
    url = url.strip()
    
    if 'linkedin.com' not in url.lower():
        return False
    
    # Valid LinkedIn profile patterns
    linkedin_patterns = [
        r'linkedin\.com/in/[\w\-]+',
        r'linkedin\.com/pub/[\w\-]+',
        r'www\.linkedin\.com/in/[\w\-]+',
        r'www\.linkedin\.com/pub/[\w\-]+'
    ]
    
    return any(re.search(pattern, url.lower()) for pattern in linkedin_patterns)


def scrape_linkedin_profile(url: str) -> Dict:
    """
    Scrape public LinkedIn profile data
    
    Args:
        url: LinkedIn profile URL
        
    Returns:
        dict: Profile data with keys: success, headline, about, experience, education, skills, error
    """
    # Validate URL
    if not validate_linkedin_url(url):
        return {
            'success': False,
            'error': 'Invalid LinkedIn URL. Please provide a valid LinkedIn profile URL (e.g., https://www.linkedin.com/in/username)',
            'headline': '',
            'about': '',
            'experience': '',
            'education': '',
            'skills': [],
            'full_name': ''
        }
    
    # Check if scraping is enabled
    if not SCRAPING_ENABLED:
        return {
            'success': False,
            'error': 'LinkedIn scraping is disabled. Please manually enter your profile information.',
            'headline': '',
            'about': '',
            'experience': '',
            'education': '',
            'skills': [],
            'full_name': ''
        }
    
    try:
        # Polite delay before request
        time.sleep(REQUEST_DELAY)
        
        # Send request to LinkedIn
        response = requests.get(url, headers=HEADERS, timeout=10)
        
        # Check response status
        if response.status_code == 999:
            return {
                'success': False,
                'error': 'LinkedIn is blocking automated requests. Please manually enter your profile information below.',
                'headline': '',
                'about': '',
                'experience': '',
                'education': '',
                'skills': [],
                'full_name': ''
            }
        
        if response.status_code != 200:
            return {
                'success': False,
                'error': f'Failed to access LinkedIn profile (HTTP {response.status_code}). Make sure the profile is public or manually enter information below.',
                'headline': '',
                'about': '',
                'experience': '',
                'education': '',
                'skills': [],
                'full_name': ''
            }
        
        # Parse HTML
        profile_data = parse_profile_html(response.text, url)
        profile_data['success'] = True
        
        return profile_data
        
    except requests.Timeout:
        return {
            'success': False,
            'error': 'Request timed out. Please check your connection or manually enter information.',
            'headline': '',
            'about': '',
            'experience': '',
            'education': '',
            'skills': [],
            'full_name': ''
        }
    except requests.RequestException as e:
        return {
            'success': False,
            'error': f'Network error: {str(e)}. Please manually enter your profile information.',
            'headline': '',
            'about': '',
            'experience': '',
            'education': '',
            'skills': [],
            'full_name': ''
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Error scraping profile: {str(e)}. Please manually enter information.',
            'headline': '',
            'about': '',
            'experience': '',
            'education': '',
            'skills': [],
            'full_name': ''
        }


def parse_profile_html(html: str, url: str) -> Dict:
    """
    Parse LinkedIn profile HTML to extract data
    
    Args:
        html: HTML content from LinkedIn profile
        url: Original profile URL
        
    Returns:
        dict: Extracted profile data
    """
    soup = BeautifulSoup(html, 'lxml')
    
    profile_data = {
        'full_name': '',
        'headline': '',
        'about': '',
        'experience': '',
        'education': '',
        'skills': [],
        'error': None
    }
    
    # Note: LinkedIn's public profile HTML structure can change frequently
    # This is a best-effort extraction from publicly visible content
    
    # Try to extract name
    name_selectors = [
        'h1.top-card-layout__title',
        'h1.text-heading-xlarge',
        '.pv-text-details__left-panel h1',
        'div.mt2.relative h1'
    ]
    for selector in name_selectors:
        name_elem = soup.select_one(selector)
        if name_elem:
            profile_data['full_name'] = name_elem.get_text(strip=True)
            break
    
    # Try to extract headline
    headline_selectors = [
        'div.top-card-layout__headline',
        'div.text-body-medium',
        '.pv-text-details__left-panel .text-body-medium',
        'div.mt1.relative div.text-body-medium'
    ]
    for selector in headline_selectors:
        headline_elem = soup.select_one(selector)
        if headline_elem:
            profile_data['headline'] = headline_elem.get_text(strip=True)
            break
    
    # Try to extract about/summary section
    about_selectors = [
        'section.summary .core-section-container__content',
        'section[data-section="summary"] .core-section-container__content',
        'div.summary .pv-shared-text-with-see-more',
        '.pv-about-section .pv-about__summary-text'
    ]
    for selector in about_selectors:
        about_elem = soup.select_one(selector)
        if about_elem:
            profile_data['about'] = about_elem.get_text(strip=True)
            break
    
    # Try to extract experience
    experience_section = soup.select_one('section.experience, section[data-section="experience"]')
    if experience_section:
        experience_items = experience_section.select('.pvs-entity, .pv-entity__position-group-pager')
        exp_texts = []
        for item in experience_items[:5]:  # Limit to first 5 experiences
            exp_texts.append(item.get_text(strip=True))
        profile_data['experience'] = ' | '.join(exp_texts) if exp_texts else ''
    
    # Try to extract education
    education_section = soup.select_one('section.education, section[data-section="education"]')
    if education_section:
        education_items = education_section.select('.pvs-entity, .pv-entity__degree-info')
        edu_texts = []
        for item in education_items[:3]:  # Limit to first 3 education entries
            edu_texts.append(item.get_text(strip=True))
        profile_data['education'] = ' | '.join(edu_texts) if edu_texts else ''
    
    # Try to extract skills
    skills_section = soup.select_one('section.skills, section[data-section="skills"]')
    if skills_section:
        skill_items = skills_section.select('.pvs-entity__path, .pv-skill-category-entity__name')
        profile_data['skills'] = [skill.get_text(strip=True) for skill in skill_items[:15]]
    
    # If we didn't get much data, it might be because the profile is not public
    # or LinkedIn's structure has changed
    if not profile_data['headline'] and not profile_data['about']:
        profile_data['error'] = 'Could not extract profile data. The profile may not be public, or you may need to manually enter information.'
    
    return profile_data


def get_profile_summary(profile_data: Dict) -> str:
    """
    Create a combined text summary of profile for analysis
    
    Args:
        profile_data: Dictionary with profile fields
        
    Returns:
        str: Combined text summary
    """
    parts = []
    
    if profile_data.get('full_name'):
        parts.append(f"Name: {profile_data['full_name']}")
    
    if profile_data.get('headline'):
        parts.append(f"Headline: {profile_data['headline']}")
    
    if profile_data.get('about'):
        parts.append(f"About: {profile_data['about']}")
    
    if profile_data.get('experience'):
        parts.append(f"Experience: {profile_data['experience']}")
    
    if profile_data.get('education'):
        parts.append(f"Education: {profile_data['education']}")
    
    if profile_data.get('skills'):
        parts.append(f"Skills: {', '.join(profile_data['skills'])}")
    
    return '\n\n'.join(parts)
