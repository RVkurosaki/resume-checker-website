"""
Automated test script to debug session issues
"""
import requests
import os
import sys

# Log output to file as well as console
class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, 'w', encoding='utf-8')
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    
    def flush(self):
        self.terminal.flush()
        self.log.flush()

sys.stdout = Logger('test_results.log')

BASE_URL = "http://localhost:5000"

def test_login_and_upload():
    """Test the complete login and upload flow"""
    
    # Create a session to persist cookies
    session = requests.Session()
    
    print("=" * 60)
    print("STEP 1: Testing Login")
    print("=" * 60)
    
    # First, get the login page to see if we can connect
    try:
        response = session.get(f"{BASE_URL}/auth/login")
        print(f"✓ Login page accessible: {response.status_code}")
    except Exception as e:
        print(f"✗ Cannot connect to server: {e}")
        return
    
    # Attempt login
    login_data = {
        'username': 'testuser',  # Test user we just created
        'password': 'testpass123'
    }
    
    response = session.post(f"{BASE_URL}/auth/login", data=login_data, allow_redirects=False)
    print(f"Login response status: {response.status_code}")
    print(f"Login response headers: {dict(response.headers)}")
    print(f"Cookies after login: {session.cookies.get_dict()}")
    
    if response.status_code == 302:  # Redirect
        redirect_location = response.headers.get('Location', '')
        print(f"✓ Login redirected to: {redirect_location}")
        
        if 'dashboard' in redirect_location:
            print("✓ Login successful - redirecting to dashboard")
        else:
            print("✗ Login failed - not redirecting to dashboard")
            return
    else:
        print(f"✗ Unexpected response: {response.status_code}")
        return
    
    print("\n" + "=" * 60)
    print("STEP 2: Testing Dashboard Access")
    print("=" * 60)
    
    # Try to access dashboard
    response = session.get(f"{BASE_URL}/dashboard/", allow_redirects=False)
    print(f"Dashboard response status: {response.status_code}")
    print(f"Cookies: {session.cookies.get_dict()}")
    
    if response.status_code == 200:
        print("✓ Dashboard accessible - session is working!")
    elif response.status_code == 302:
        redirect_location = response.headers.get('Location', '')
        print(f"✗ Redirected to: {redirect_location}")
        if 'login' in redirect_location:
            print("✗ SESSION LOST - Being redirected back to login!")
        return
    
    print("\n" + "=" * 60)
    print("STEP 3: Testing File Upload")
    print("=" * 60)
    
    # Create a dummy PDF file for testing
    dummy_pdf_path = "test_resume.pdf"
    if not os.path.exists(dummy_pdf_path):
        # Create a minimal valid PDF
        with open(dummy_pdf_path, 'wb') as f:
            f.write(b'%PDF-1.4\n%Test PDF\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000015 00000 n\n0000000074 00000 n\n0000000133 00000 n\ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n210\n%%EOF')
        print(f"✓ Created test PDF: {dummy_pdf_path}")
    
    # Attempt file upload
    with open(dummy_pdf_path, 'rb') as f:
        files = {'resume': ('test_resume.pdf', f, 'application/pdf')}
        data = {'job_role': 'software_engineer'}
        
        print(f"Cookies before upload: {session.cookies.get_dict()}")
        response = session.post(f"{BASE_URL}/resume/upload", files=files, data=data, allow_redirects=False)
        
        print(f"Upload response status: {response.status_code}")
        print(f"Upload response headers: {dict(response.headers)}")
        print(f"Cookies after upload: {session.cookies.get_dict()}")
        
        if response.status_code == 302:
            redirect_location = response.headers.get('Location', '')
            print(f"Redirected to: {redirect_location}")
            
            if 'login' in redirect_location:
                print("✗ SESSION LOST DURING UPLOAD - Being redirected back to login!")
                print("\nThis confirms the session is being lost between dashboard and upload!")
            elif 'loading' in redirect_location:
                print("✓ Upload successful - redirecting to loading page")
                print("\nSession is working correctly!")
            else:
                print(f"✗ Unexpected redirect: {redirect_location}")
        else:
            print(f"✗ Unexpected response: {response.status_code}")
    
    # Cleanup
    if os.path.exists(dummy_pdf_path):
        os.remove(dummy_pdf_path)
        print(f"\n✓ Cleaned up test PDF")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    print("\n🔍 Starting automated session test...\n")
    print("NOTE: Update the username and password in the script if different\n")
    test_login_and_upload()
