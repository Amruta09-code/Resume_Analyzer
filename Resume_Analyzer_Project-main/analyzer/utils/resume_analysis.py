from analyzer.ats_utils import calculate_ats_score, get_domain_from_keywords
import io
import fitz  # PyMuPDF
import re

def analyze_resume_score(file_field):
    """
    Analyzes the resume file and returns an ATS score and the detected domain.
    """
    try:
        # Determine file type and extract text
        file_extension = file_field.name.split('.')[-1].lower()
        if file_extension == 'pdf':
            # Read the file content directly. This is more robust and works for both
            # in-memory and temporary files without needing a temporary file path.
            pdf_stream = io.BytesIO(file_field.read())
            text = ""
            with fitz.open(stream=pdf_stream, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text()
            # Clean up whitespace, similar to the original utility function
            text = re.sub(r'\s+', ' ', text)
        else:
            # Handle other file types (e.g., docx, txt) if needed
            # For now, return a default score
            return 50.0, "General"

        # Define a more comprehensive list of keywords
        # In a real app, this might be dynamic based on a job description
        keywords = [
            # Web & Software Dev
            'python', 'django', 'flask', 'api', 'rest', 'fastapi', 'node.js',
            'javascript', 'react', 'vue', 'angular', 'typescript', 'html', 'css',
            # Data Science
            'sql', 'postgresql', 'mysql', 'nosql', 'mongodb', 'redis', 'machine learning', 
            'ml', 'ai', 'data science', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy',
            # DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ci/cd', 'jenkins', 'ansible',
            # Android
            'android', 'kotlin', 'java', 'jetpack', 'sdk',
            # UI/UX
            'ui', 'ux', 'figma', 'sketch', 'adobe xd', 'wireframe', 'prototype', 'user research',
            # General/Soft Skills
            'git', 'agile', 'scrum', 'jira', 'problem solving', 'teamwork',
            'public speaking', 'presentation', 'communication', 'toastmasters'
        ]
        
        score, matched_keywords = calculate_ats_score(text, keywords)
        domain = get_domain_from_keywords(matched_keywords)
        return score, domain

    except Exception as e:
        print(f"Error analyzing resume: {e}")
        return 0.0, "General"  # Return 0 and a default domain in case of an error
