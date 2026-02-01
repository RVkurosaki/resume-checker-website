"""Test job match with simpler output"""
from analysis import detect_skills_from_text, calculate_job_match, JOB_ROLES

test_resume = """
Python, JavaScript, React, Node.js, SQL, Git, REST API development,
Data structures, Algorithms, Problem solving, OOP
"""

job_role = 'software_engineer'

# Detect skills
detected = detect_skills_from_text(test_resume)

# Get required
required = JOB_ROLES[job_role]['skills']

# Calculate match
match_percent, missing = calculate_job_match(detected, job_role)

print(f"Detected: {detected}")
print(f"Required: {required}")
print(f"Match: {match_percent}%")
print(f"Missing: {missing}")

# Manual check
detected_lower = set(s.lower() for s in detected)
print(f"\nDetected (lower): {detected_lower}")

for skill in required:
    found = skill.lower() in detected_lower
    print(f"  {skill}: {found}")
