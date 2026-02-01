"""
Quick diagnostic test to understand the job match calculation issue
"""
from analysis import detect_skills_from_text, calculate_job_match, JOB_ROLES

# Test resume text
test_resume = """
John Doe
Software Engineer

Skills:
- Python programming with Django and Flask
- JavaScript, React, and Node.js
- SQL databases (PostgreSQL, MySQL)
- Git version control
- RESTful API development
- Data structures and algorithms
- Object-oriented programming

Experience:
Developed web applications using Python and JavaScript.
Implemented REST APIs with proper authentication.
Problem-solving and algorithm optimization.
"""

# Test for software engineer role
job_role = 'software_engineer'

print("=" * 60)
print("JOB MATCH DIAGNOSTIC TEST")
print("=" * 60)

# Step 1: Detect skills
detected_skills = detect_skills_from_text(test_resume)
print(f"\n1. DETECTED SKILLS ({len(detected_skills)}):")
for i, skill in enumerate(detected_skills, 1):
    print(f"   {i}. '{skill}'")

# Step 2: Get required skills for the role
role_info = JOB_ROLES[job_role]
required_skills = role_info['skills']
print(f"\n2. REQUIRED SKILLS for {role_info['title']} ({len(required_skills)}):")
for i, skill in enumerate(required_skills, 1):
    print(f"   {i}. '{skill}'")

# Step 3: Calculate match
match_percent, missing_skills = calculate_job_match(detected_skills, job_role)
print(f"\n3. JOB MATCH RESULT:")
print(f"   Match Percentage: {match_percent}%")
print(f"   Missing Skills ({len(missing_skills)}):")
for i, skill in enumerate(missing_skills, 1):
    print(f"   {i}. '{skill}'")

# Step 4: Detailed comparison
print(f"\n4. DETAILED SKILL COMPARISON:")
detected_lower = [s.lower() for s in detected_skills]
print(f"   Detected (lowercase): {detected_lower}")
print()

for skill in required_skills:
    is_found = skill.lower() in detected_lower
    status = "✓ FOUND" if is_found else "✗ MISSING"
    print(f"   {status}: '{skill}' (checking '{skill.lower()}')")

print("\n" + "=" * 60)
