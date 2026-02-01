"""
AI-powered resume analysis module using ChatGPT
Enhanced with accurate skill detection and scoring
"""
import os
import json
import re
import time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

MOCK_AI = os.getenv('MOCK_AI', 'True') == 'True'

# Comprehensive skill keywords for detection
SKILL_KEYWORDS = {
    # Programming Languages
    'python': ['python', 'py', 'django', 'flask', 'fastapi'],
    'java': ['java', 'spring', 'spring boot', 'hibernate', 'maven'],
    'javascript': ['javascript', 'js', 'node.js', 'nodejs', 'express', 'react', 'vue', 'angular'],
    'c': ['c programming', ' c ', 'c language'],
    'c++': ['c++', 'cpp'],
    'c#': ['c#', 'csharp', '.net', 'dotnet'],
    'sql': ['sql', 'mysql', 'postgresql', 'postgres', 'sqlite', 'oracle', 'database'],
    'html': ['html', 'html5'],
    'css': ['css', 'css3', 'sass', 'scss', 'tailwind', 'bootstrap'],
    'typescript': ['typescript', 'ts'],
    'go': ['golang', 'go lang'],
    'rust': ['rust'],
    'php': ['php', 'laravel'],
    'ruby': ['ruby', 'rails', 'ruby on rails'],
    'swift': ['swift', 'ios development'],
    'kotlin': ['kotlin', 'android'],
    
    # Programming Concepts & Fundamentals
    'oop': ['oop', 'object oriented', 'object-oriented', 'object oriented programming', 'inheritance', 'polymorphism', 'encapsulation'],
    'data structures': ['data structures', 'data structure', 'arrays', 'linked list', 'trees', 'graphs', 'hash table', 'heap', 'stack', 'queue'],
    'algorithms': ['algorithms', 'algorithm', 'sorting', 'searching', 'dynamic programming', 'recursion', 'complexity analysis'],
    
    # Data Science & ML
    'machine learning': ['machine learning', 'ml', 'deep learning', 'neural network', 'ai', 'artificial intelligence'],
    'tensorflow': ['tensorflow', 'tf'],
    'pytorch': ['pytorch', 'torch'],
    'pandas': ['pandas', 'dataframe'],
    'numpy': ['numpy', 'np'],
    'scikit-learn': ['scikit-learn', 'sklearn', 'scikit learn'],
    'statistics': ['statistics', 'statistical', 'statistical analysis', 'probability', 'hypothesis testing', 'regression'],
    'nlp': ['nlp', 'natural language processing', 'text mining', 'sentiment analysis', 'language model'],
    'computer vision': ['computer vision', 'cv', 'image processing', 'object detection', 'image recognition'],
    'deep learning': ['deep learning', 'neural networks', 'cnn', 'rnn', 'lstm', 'transformer'],
    'data analysis': ['data analysis', 'data analytics', 'analytics'],
    'data visualization': ['data visualization', 'tableau', 'power bi', 'matplotlib', 'seaborn', 'plotly'],
    
    # DevOps & Cloud
    'docker': ['docker', 'container', 'dockerfile'],
    'kubernetes': ['kubernetes', 'k8s'],
    'aws': ['aws', 'amazon web services', 'ec2', 's3', 'lambda'],
    'azure': ['azure', 'microsoft azure'],
    'gcp': ['gcp', 'google cloud', 'google cloud platform'],
    'linux': ['linux', 'ubuntu', 'centos', 'debian', 'unix'],
    'git': ['git', 'github', 'gitlab', 'bitbucket', 'version control'],
    'ci/cd': ['ci/cd', 'cicd', 'jenkins', 'github actions', 'gitlab ci', 'continuous integration'],
    'terraform': ['terraform', 'infrastructure as code', 'iac'],
    'bash': ['bash', 'shell script', 'shell scripting', 'bash script'],
    
    # Web Development
    'react': ['react', 'reactjs', 'react.js'],
    'angular': ['angular', 'angularjs'],
    'vue': ['vue', 'vuejs', 'vue.js'],
    'node.js': ['node', 'nodejs', 'node.js', 'express'],
    'rest api': ['rest', 'restful', 'api', 'rest api'],
    'mongodb': ['mongodb', 'mongo', 'nosql'],
    'responsive design': ['responsive design', 'responsive', 'mobile first', 'media queries', 'responsive web'],
    
    # Tools & Software
    'excel': ['excel', 'microsoft excel', 'spreadsheet', 'xlookup', 'pivot table', 'vlookup'],
    
    # Soft Skills
    'problem solving': ['problem solving', 'problem-solving', 'analytical', 'critical thinking'],
    'communication': ['communication', 'presentation', 'public speaking'],
    'teamwork': ['teamwork', 'team player', 'collaboration', 'collaborative'],
    'leadership': ['leadership', 'lead', 'managed', 'mentored'],
    'agile': ['agile', 'scrum', 'kanban', 'sprint'],
}

# ATS keywords that boost score
ATS_KEYWORDS = [
    'achieved', 'developed', 'implemented', 'designed', 'created', 'built',
    'improved', 'increased', 'reduced', 'optimized', 'managed', 'led',
    'collaborated', 'analyzed', 'automated', 'delivered', 'launched',
    'experience', 'skills', 'education', 'projects', 'certification',
    'proficient', 'expertise', 'responsible', 'contributed'
]

# Job roles with required skills
JOB_ROLES = {
    'software_engineer': {
        'title': 'Software Engineer',
        'skills': ['Python', 'Java', 'JavaScript', 'Git', 'SQL', 'REST API', 'Data Structures', 'Algorithms', 'Problem Solving', 'OOP'],
        'weight': {'Python': 2, 'Java': 2, 'Git': 1.5, 'SQL': 1.5}
    },
    'data_analyst': {
        'title': 'Data Analyst',
        'skills': ['Python', 'SQL', 'Excel', 'Tableau', 'Power BI', 'Statistics', 'Data Visualization', 'Pandas', 'NumPy', 'Machine Learning'],
        'weight': {'SQL': 2, 'Python': 2, 'Data Visualization': 1.5}
    },
    'web_developer': {
        'title': 'Web Developer',
        'skills': ['HTML', 'CSS', 'JavaScript', 'React', 'Node.js', 'Git', 'REST API', 'Responsive Design', 'TypeScript', 'MongoDB'],
        'weight': {'JavaScript': 2, 'HTML': 1.5, 'CSS': 1.5, 'React': 2}
    },
    'ml_engineer': {
        'title': 'ML Engineer',
        'skills': ['Python', 'TensorFlow', 'PyTorch', 'Machine Learning', 'Deep Learning', 'NLP', 'Computer Vision', 'Pandas', 'NumPy', 'Scikit-learn'],
        'weight': {'Python': 2, 'Machine Learning': 2, 'TensorFlow': 1.5, 'PyTorch': 1.5}
    },
    'devops_engineer': {
        'title': 'DevOps Engineer',
        'skills': ['Linux', 'Docker', 'Kubernetes', 'CI/CD', 'AWS', 'Azure', 'Terraform', 'Git', 'Python', 'Bash'],
        'weight': {'Docker': 2, 'Kubernetes': 2, 'AWS': 1.5, 'Linux': 1.5}
    }
}

# Interview tips and common questions for each job role
INTERVIEW_TIPS = {
    'software_engineer': {
        'tips': [
            'Practice coding problems on platforms like LeetCode, HackerRank, or CodeSignal',
            'Review data structures (arrays, linked lists, trees, graphs) and algorithms (sorting, searching, dynamic programming)',
            'Prepare to explain your past projects in detail - challenges faced, solutions implemented, and impact',
            'Be ready to discuss system design concepts for senior positions',
            'Understand time and space complexity (Big O notation)',
            'Practice whiteboard coding or live coding in your preferred language',
            'Research the company\'s tech stack and products before the interview',
            'Prepare questions to ask the interviewer about team culture, development processes, and growth opportunities'
        ],
        'questions': [
            'Explain the difference between object-oriented and functional programming',
            'What are the main principles of OOP? Explain with examples',
            'How do you optimize the performance of a slow application?',
            'Explain the concept of RESTful APIs and HTTP methods',
            'What is the difference between SQL and NoSQL databases?',
            'Describe a challenging bug you encountered and how you fixed it',
            'How do you handle version control conflicts in Git?',
            'Explain dependency injection and its benefits',
            'What are design patterns? Name a few you have used',
            'How would you reverse a linked list? Optimize for time complexity'
        ]
    },
    'data_analyst': {
        'tips': [
            'Be proficient in SQL - practice complex queries, joins, subqueries, and window functions',
            'Know your data visualization tools (Tableau, Power BI, Excel) inside out',
            'Understand statistical concepts: mean, median, mode, standard deviation, hypothesis testing',
            'Be prepared to discuss A/B testing and experimental design',
            'Practice explaining technical findings to non-technical stakeholders',
            'Prepare case studies where you derived actionable insights from data',
            'Review common metrics for the industry (e.g., CAC, LTV, churn rate for SaaS)',
            'Be ready to walk through your data analysis process from start to finish'
        ],
        'questions': [
            'Explain the difference between INNER JOIN, LEFT JOIN, and RIGHT JOIN',
            'How would you handle missing data in a dataset?',
            'What is the difference between correlation and causation?',
            'Describe your process for cleaning and preparing data for analysis',
            'How do you validate the results of your analysis?',
            'Explain p-value and statistical significance',
            'Walk me through an A/B test you designed and analyzed',
            'How would you detect outliers in a dataset?',
            'What metrics would you track for [specific business scenario]?',
            'Explain a time when your analysis led to a business decision'
        ]
    },
    'web_developer': {
        'tips': [
            'Build a strong portfolio with 3-5 impressive projects showcasing different skills',
            'Understand responsive design principles and mobile-first development',
            'Know the fundamentals: HTML5 semantic tags, CSS Grid/Flexbox, JavaScript ES6+',
            'Be proficient in at least one modern framework (React, Vue, or Angular)',
            'Understand browser APIs, async programming (Promises, async/await)',
            'Know website performance optimization techniques (lazy loading, code splitting, caching)',
            'Practice live coding challenges - build a component or feature from scratch',
            'Understand web accessibility (WCAG) and SEO best practices'
        ],
        'questions': [
            'Explain the box model in CSS',
            'What is the difference between var, let, and const in JavaScript?',
            'How does the event loop work in JavaScript?',
            'Explain the Virtual DOM and how React uses it',
            'What are CSS preprocessors? Have you used Sass or Less?',
            'How do you ensure your website is accessible?',
            'Explain Cross-Origin Resource Sharing (CORS)',
            'What is the difference between localStorage and sessionStorage?',
            'How would you optimize website loading time?',
            'Describe the lifecycle methods in React or your framework of choice'
        ]
    },
    'ml_engineer': {
        'tips': [
            'Understand the full ML pipeline: data collection, preprocessing, modeling, evaluation, deployment',
            'Be strong in Python and key libraries: NumPy, Pandas, Scikit-learn, TensorFlow/PyTorch',
            'Know when to use different algorithms (linear regression, decision trees, neural networks, etc.)',
            'Understand evaluation metrics: accuracy, precision, recall, F1-score, AUC-ROC',
            'Be prepared to discuss bias-variance tradeoff, overfitting, and regularization',
            'Have projects demonstrating end-to-end ML solutions (from data to deployment)',
            'Understand MLOps basics: model versioning, monitoring, CI/CD for ML',
            'Review recent ML papers or trends relevant to the company\'s domain'
        ],
        'questions': [
            'Explain the bias-variance tradeoff',
            'What is overfitting and how do you prevent it?',
            'Describe the difference between supervised and unsupervised learning',
            'How would you handle imbalanced datasets?',
            'Explain gradient descent and its variants (SGD, Adam, etc.)',
            'What is the difference between precision and recall?',
            'How do you select features for a machine learning model?',
            'Explain how neural networks learn through backpropagation',
            'What is regularization? Explain L1 vs L2 regularization',
            'Describe a machine learning project you built from scratch'
        ]
    },
    'devops_engineer': {
        'tips': [
            'Master containerization with Docker and orchestration with Kubernetes',
            'Understand CI/CD pipelines and tools (Jenkins, GitLab CI, GitHub Actions)',
            'Be proficient in at least one cloud platform (AWS, Azure, or GCP)',
            'Know Infrastructure as Code tools like Terraform, Ansible, or CloudFormation',
            'Understand monitoring and logging (Prometheus, Grafana, ELK stack)',
            'Be comfortable with Linux/Unix systems and shell scripting',
            'Know networking basics: DNS, load balancers, proxies, firewalls',
            'Prepare examples of infrastructure optimization or incident resolution'
        ],
        'questions': [
            'Explain the difference between containers and virtual machines',
            'How does Kubernetes orchestrate containers?',
            'Describe a CI/CD pipeline you have implemented',
            'What is Infrastructure as Code and why is it important?',
            'How would you handle a production outage?',
            'Explain blue-green deployment vs canary deployment',
            'What monitoring tools have you used and how do you set up alerts?',
            'How do you ensure security in a DevOps environment?',
            'Explain the concept of immutable infrastructure',
            'Describe how you would scale an application to handle increased traffic'
        ]
    }
}



def detect_skills_from_text(text: str) -> list:
    """Accurately detect skills from resume text with case-insensitive matching"""
    text_lower = text.lower()
    detected = set()
    
    for skill_name, keywords in SKILL_KEYWORDS.items():
        for keyword in keywords:
            # Use word boundaries for more accurate matching
            # This prevents matching 'java' in 'javascript'
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text_lower):
                # Capitalize skill names properly
                detected.add(skill_name.replace('_', ' ').title())
                break
    
    # Also check for common variations and acronyms
    # Check for specific patterns like "3+ years of Python"
    if re.search(r'\b\d+\+?\s*(years?|months?)\s*(of|in|with)\s+\w+', text_lower):
        # This indicates experience sections, helpful for skill detection
        pass
    
    return sorted(list(detected))


def calculate_ats_score(text: str, detected_skills: list) -> tuple:
    """Calculate accurate ATS score based on resume content"""
    text_lower = text.lower()
    score = 0
    feedback = []
    
    # Base score for having content
    word_count = len(text.split())
    if word_count >= 300:
        score += 15
    elif word_count >= 150:
        score += 10
        feedback.append("Resume could be more detailed")
    else:
        score += 5
        feedback.append("Resume is too short - add more content")
    
    # Section detection
    sections = {
        'education': ['education', 'degree', 'university', 'college', 'bachelor', 'master', 'b.tech', 'm.tech', 'bsc', 'msc'],
        'experience': ['experience', 'work history', 'employment', 'internship', 'worked at', 'worked as'],
        'skills': ['skills', 'technical skills', 'technologies', 'proficient in'],
        'projects': ['projects', 'portfolio', 'developed', 'built', 'created'],
        'contact': ['email', 'phone', 'linkedin', 'github', '@']
    }
    
    for section, keywords in sections.items():
        if any(kw in text_lower for kw in keywords):
            score += 8
        else:
            feedback.append(f"Add a clear {section.title()} section")
    
    # Action verbs and ATS keywords
    ats_found = sum(1 for kw in ATS_KEYWORDS if kw in text_lower)
    score += min(ats_found * 2, 20)
    
    if ats_found < 5:
        feedback.append("Use more action verbs (developed, implemented, achieved)")
    
    # Skills count bonus
    skill_bonus = min(len(detected_skills) * 3, 15)
    score += skill_bonus
    
    if len(detected_skills) < 5:
        feedback.append("Add more technical skills to your resume")
    
    # Quantifiable achievements
    has_numbers = bool(re.search(r'\d+%|\d+ years?|\d+ projects?|\d+ users?|\$\d+', text_lower))
    if has_numbers:
        score += 10
    else:
        feedback.append("Include quantifiable achievements (e.g., 'increased efficiency by 30%')")
    
    # Cap score at 100
    score = min(score, 100)
    
    if not feedback:
        feedback.append("Resume structure looks good!")
    
    return score, feedback[:5]


def find_grammar_issues(text: str) -> list:
    """Find common grammar and phrasing issues"""
    issues = []
    text_lower = text.lower()
    
    # Common weak phrases and their improvements
    weak_phrases = [
        ("responsible for", "Led", "Replace 'responsible for' with action verbs"),
        ("worked on", "Developed/Implemented", "Replace 'worked on' with specific actions"),
        ("helped with", "Contributed to/Assisted in", "Be more specific than 'helped with'"),
        ("i am", "Professional with", "Use third person in resumes"),
        ("i have", "[state directly]", "Avoid 'I have' - state skills directly"),
        ("good at", "Proficient in/Expertise in", "Replace 'good at' with professional terms"),
        ("knows", "Proficient in", "Use 'proficient in' instead of 'knows'"),
        ("did a project", "Developed a project", "Use action verbs for projects"),
        ("basic knowledge", "Foundational understanding", "Rephrase 'basic knowledge'"),
        ("hard worker", "Dedicated professional", "Use professional descriptors"),
    ]
    
    for weak, better, tip in weak_phrases:
        if weak in text_lower:
            # Find actual context
            idx = text_lower.find(weak)
            start = max(0, idx - 20)
            end = min(len(text), idx + len(weak) + 30)
            context = text[start:end].strip()
            
            # Clean up context
            if start > 0:
                context = "..." + context
            if end < len(text):
                context = context + "..."
            
            issues.append({
                'original': context,
                'corrected': f"Consider: {tip}. Use '{better}' instead.",
            })
    
    # Check for passive voice indicators
    passive_indicators = ['was created', 'was developed', 'was implemented', 'was designed']
    for passive in passive_indicators:
        if passive in text_lower:
            issues.append({
                'original': f"Found passive voice: '{passive}'",
                'corrected': f"Use active voice: '{passive.replace('was ', '').title()}' something"
            })
            break
    
    if not issues:
        issues.append({
            'original': "No major grammar issues detected",
            'corrected': "Your resume language is professional. Consider adding more accomplishment-focused statements."
        })
    
    return issues[:5]


def calculate_job_match(detected_skills: list, job_role: str) -> tuple:
    """Calculate accurate job match percentage"""
    role_info = JOB_ROLES.get(job_role, JOB_ROLES['software_engineer'])
    required_skills = role_info['skills']
    weights = role_info.get('weight', {})
    
    detected_lower = [s.lower() for s in detected_skills]
    
    matched = []
    missing = []
    total_weight = 0
    matched_weight = 0
    
    for skill in required_skills:
        skill_weight = weights.get(skill, 1)
        total_weight += skill_weight
        
        if skill.lower() in detected_lower:
            matched.append(skill)
            matched_weight += skill_weight
        else:
            missing.append(skill)
    
    # Calculate weighted percentage
    match_percent = int((matched_weight / total_weight) * 100) if total_weight > 0 else 0
    
    return match_percent, missing


def generate_suggestions(detected_skills: list, missing_skills: list, ats_score: int, text: str) -> list:
    """Generate actionable improvement suggestions"""
    suggestions = []
    text_lower = text.lower()
    
    # Based on missing skills
    if missing_skills:
        top_missing = missing_skills[:3]
        suggestions.append(f"Learn or highlight these skills: {', '.join(top_missing)}")
    
    # Based on ATS score
    if ats_score < 50:
        suggestions.append("Restructure resume with clear sections: Summary, Skills, Experience, Education, Projects")
    
    if ats_score < 70:
        suggestions.append("Add measurable achievements (e.g., 'Reduced load time by 40%')")
    
    # Check for common missing elements
    if 'github' not in text_lower and 'portfolio' not in text_lower:
        suggestions.append("Add links to your GitHub profile or portfolio website")
    
    if 'certification' not in text_lower and 'certified' not in text_lower:
        suggestions.append("Consider adding relevant certifications to stand out")
    
    if 'project' not in text_lower:
        suggestions.append("Add a dedicated Projects section with 2-3 detailed projects")
    
    if len(detected_skills) < 8:
        suggestions.append("Expand your Skills section with more relevant technologies")
    
    # Generic always-good suggestions
    suggestions.append("Tailor your resume keywords to match each job description")
    
    return suggestions[:6]


def get_analysis_prompt(resume_text: str, job_role: str) -> str:
    """Generate the ChatGPT prompt for comprehensive resume analysis"""
    role_info = JOB_ROLES.get(job_role, JOB_ROLES['software_engineer'])
    required_skills = ', '.join(role_info['skills'])
    
    return f"""You are an expert resume analyst and career coach. Analyze this resume THOROUGHLY and provide SPECIFIC, ACTIONABLE feedback.

RESUME TEXT:
{resume_text[:5000]}

TARGET JOB ROLE: {role_info['title']}
REQUIRED SKILLS: {required_skills}

CRITICAL INSTRUCTIONS FOR SKILL DETECTION:
1. DETECTED SKILLS: READ THE ENTIRE RESUME CAREFULLY. 
   - Look for EVERY mention of programming languages, frameworks, tools, platforms, and technologies
   - Check experience descriptions, project descriptions, skills sections, and education
   - Include variations (e.g., "JS" for JavaScript, "React.js" for React)
   - BE THOROUGH - don't miss any skills actually mentioned in the resume
   - List ONLY skills that are ACTUALLY PRESENT in the resume text
   - Examples: If resume says "Python, Java, React", you MUST detect these

2. MISSING SKILLS: Compare detected skills with required skills for {role_info['title']}.
   - List ONLY the required skills that were NOT found in the resume
   - If ALL required skills are present, return an EMPTY LIST [] or ["None - all required skills present!"]
   
3. ATS SCORE (0-100): Evaluate based on:
   - Presence of clear sections (Contact, Summary, Skills, Experience, Education, Projects)
   - Use of action verbs (developed, implemented, achieved, designed, led)
   - Quantifiable achievements (percentages, numbers, metrics)
   - Keyword density for the target role
   - Professional formatting and structure

4. ATS FEEDBACK: Provide 3-5 SPECIFIC recommendations to improve ATS score.

5. GRAMMAR ISSUES: Identify weak phrases like "responsible for", "worked on", "good at". Provide exact quotes from the resume and suggest professional alternatives.

6. JOB MATCH PERCENT (0-100): Calculate based on:
   - Skill overlap with required skills (weighted heavily)
   - Relevant experience mentioned
   - Project alignment with job role

7. SUGGESTIONS: Provide 4-6 ACTIONABLE improvements specific to this resume and job role.

8. SUMMARY: Write 2-3 sentences summarizing the resume's strengths and areas for improvement.

IMPORTANT:
- BE EXTREMELY THOROUGH in detecting skills - read every word
- Reference ACTUAL content from the resume
- Be SPECIFIC, not generic
- Provide ACTIONABLE advice
- Base scores on resume quality, not arbitrary numbers

Respond ONLY with valid JSON in this exact format:
{{
    "detected_skills": ["Python", "JavaScript", "React", "SQL", "Git"],
    "missing_skills": ["Docker", "Kubernetes"],
    "ats_score": 75,
    "ats_feedback": [
        "Add quantifiable metrics to work experience (e.g., 'Increased efficiency by 30%')",
        "Include a professional summary at the top",
        "Add more action verbs to project descriptions"
    ],
    "grammar_issues": [
        {{
            "original": "Responsible for developing web applications",
            "corrected": "Developed and deployed 5+ web applications using React and Node.js"
        }}
    ],
    "job_match_percent": 65,
    "suggestions": [
        "Add experience with Docker and Kubernetes for DevOps alignment",
        "Include GitHub portfolio link to showcase projects",
        "Expand technical skills section with specific frameworks"
    ],
    "summary": "Candidate shows strong technical foundation with Python and web development skills. To improve for {role_info['title']} role, focus on adding missing skills like {required_skills.split(',')[0]} and quantifying achievements."
}}"""


def get_accurate_mock_analysis(resume_text: str, job_role: str) -> dict:
    """Accurate mock analysis based on actual resume parsing"""
    role_info = JOB_ROLES.get(job_role, JOB_ROLES['software_engineer'])
    
    # Detect actual skills from text
    detected_skills = detect_skills_from_text(resume_text)
    
    # Calculate job match
    job_match, missing_skills = calculate_job_match(detected_skills, job_role)
    
    # Calculate ATS score
    ats_score, ats_feedback = calculate_ats_score(resume_text, detected_skills)
    
    # Find grammar issues
    grammar_issues = find_grammar_issues(resume_text)
    
    # Generate suggestions
    suggestions = generate_suggestions(detected_skills, missing_skills, ats_score, resume_text)
    
    # Generate summary
    skill_count = len(detected_skills)
    
    # Check if all required skills are present
    if not missing_skills or len(missing_skills) == 0:
        missing_skills = ["None - all required skills present! 🎉"]
        summary = f"Excellent! Resume contains all {skill_count} required skills for {role_info['title']}. "
        summary += "Strong skill alignment - focus on highlighting experience and achievements."
    else:
        summary = f"Resume shows {skill_count} relevant skills with {job_match}% match for {role_info['title']}. "
        if ats_score >= 70:
            summary += "Good ATS compatibility - focus on adding missing skills."
        elif ats_score >= 50:
            summary += "Moderate ATS score - improve structure and add quantifiable achievements."
        else:
            summary += "Needs improvement - restructure with clear sections and more keywords."
    
    return {
        'detected_skills': detected_skills if detected_skills else ['No specific skills detected - add a skills section'],
        'missing_skills': missing_skills,
        'ats_score': ats_score,
        'ats_feedback': ats_feedback,
        'grammar_issues': grammar_issues,
        'job_match_percent': job_match,
        'suggestions': suggestions,
        'summary': summary
    }


def analyze_resume_with_ai(resume_text: str, job_role: str) -> dict:
    """Comprehensive resume analysis - uses accurate parsing or ChatGPT"""
    if MOCK_AI:
        return get_accurate_mock_analysis(resume_text, job_role)
    
    # Try ChatGPT API with retry logic
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            client = OpenAI(
                api_key=os.getenv('OPENAI_API_KEY'),
                timeout=30.0  # 30 second timeout
            )
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert resume analyst. Provide accurate, specific analysis based on actual resume content. Always respond with valid JSON only."},
                    {"role": "user", "content": get_analysis_prompt(resume_text, job_role)}
                ],
                max_tokens=1200,
                temperature=0.5
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean up markdown code blocks if present
            if result_text.startswith('```'):
                result_text = result_text.split('```')[1]
                if result_text.startswith('json'):
                    result_text = result_text[4:]
                result_text = result_text.strip()
            
            # Parse and validate JSON
            analysis = json.loads(result_text)
            
            # Ensure all required fields are present
            required_fields = ['detected_skills', 'missing_skills', 'ats_score', 
                             'ats_feedback', 'grammar_issues', 'job_match_percent', 
                             'suggestions', 'summary']
            
            if all(field in analysis for field in required_fields):
                return analysis
            else:
                raise ValueError("Missing required fields in API response")
            
        except json.JSONDecodeError as e:
            print(f"JSON parsing error on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
                continue
                
        except Exception as e:
            error_msg = str(e)
            print(f"API error on attempt {attempt + 1}: {error_msg}")
            
            # Check for rate limit or temporary errors
            if "rate_limit" in error_msg.lower() or "timeout" in error_msg.lower():
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
            
            # For other errors, fall through to mock analysis
            break
    
    # Fallback to accurate mock analysis if all retries fail
    print("Falling back to mock analysis")
    analysis = get_accurate_mock_analysis(resume_text, job_role)
    analysis['summary'] += " (Using local analysis - API unavailable)"
    return analysis


def get_job_roles() -> list:
    """Return list of available job roles for dropdown"""
    return [{'id': key, 'title': value['title']} for key, value in JOB_ROLES.items()]


def get_interview_tips(job_role: str) -> dict:
    """Get interview tips and common questions for a specific job role"""
    return INTERVIEW_TIPS.get(job_role, INTERVIEW_TIPS['software_engineer'])

