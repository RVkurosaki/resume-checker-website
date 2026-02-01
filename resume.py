import os
import re
from flask import Blueprint, request, flash, redirect, url_for, session, current_app
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from dotenv import load_dotenv

load_dotenv()

resume_bp = Blueprint('resume', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def extract_text_from_pdf(file_path):
    """Extract and clean text from PDF"""
    reader = PdfReader(file_path)
    text = ''
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + '\n'
    return preprocess_text(text)

def preprocess_text(text: str) -> str:
    """Clean and normalize extracted text for better AI analysis"""
    if not text:
        return text
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Normalize line breaks
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove multiple consecutive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split('\n')]
    text = '\n'.join(line for line in lines if line)
    
    # Fix common PDF extraction issues
    text = text.replace('•', '-')  # Replace bullet points
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between camelCase
    
    return text.strip()

@resume_bp.route('/upload', methods=['POST'])
def upload_resume():
    print(f"\n{'='*60}")
    print(f"DEBUG /upload: Request received")
    print(f"DEBUG /upload: Session data BEFORE check: {dict(session)}")
    print(f"DEBUG /upload: Session object: {session}")
    print(f"DEBUG /upload: 'user_id' in session: {'user_id' in session}")
    print(f"DEBUG /upload: Session.permanent: {session.permanent}")
    print(f"{'='*60}\n")
    
    if 'user_id' not in session:
        print("DEBUG /upload: NO USER_ID FOUND - Redirecting to login")
        return redirect(url_for('auth.login'))
    
    if 'resume' not in request.files:
        flash('No file selected.')
        return redirect(url_for('dashboard.dashboard'))
    
    file = request.files['resume']
    job_role = request.form.get('job_role', 'software_engineer')
    
    if file.filename == '' or not allowed_file(file.filename):
        flash('Invalid file. Please upload a PDF.')
        return redirect(url_for('dashboard.dashboard'))
    
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    # Ensure upload folder exists
    os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    file.save(file_path)
    
    try:
        text = extract_text_from_pdf(file_path)
    except Exception as e:
        os.remove(file_path)  # Clean up
        flash(f'Error reading PDF: {str(e)}. Please try a different file or convert your PDF to a simpler format.')
        return redirect(url_for('dashboard.dashboard'))
    finally:
        # Always clean up the file
        if os.path.exists(file_path):
            os.remove(file_path)
    
    if not text or not text.strip():
        flash('Could not extract text from PDF. The PDF might be scanned/image-based. Please use a text-based PDF or convert your document.')
        return redirect(url_for('dashboard.dashboard'))
    
    # Store in session for analysis
    session['resume_text'] = text
    session['job_role'] = job_role
    print(f"DEBUG /upload: Stored resume_text ({len(text)} chars) and job_role ({job_role}) in session")  # Debug log
    print(f"DEBUG /upload: Session data: {dict(session)}")  # Debug log
    
    return redirect(url_for('dashboard.loading'))