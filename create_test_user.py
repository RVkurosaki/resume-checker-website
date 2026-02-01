"""
Register a test user for automated testing
"""
import requests

BASE_URL = "http://localhost:5000"

# Create session
session = requests.Session()

# Register user
register_data = {
    'username': 'testuser',
    'password': 'testpass123'
}

print("Registering test user...")
response = session.post(f"{BASE_URL}/auth/register", data=register_data)
print(f"Registration status: {response.status_code}")

if response.status_code == 200 or 'successfully' in response.text.lower():
    print("✓ Test user registered successfully!")
else:
    print("Note: User might already exist (this is OK)")
