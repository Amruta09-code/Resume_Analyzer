from analyzer.ats_utils import calculate_ats_score
import io
import fitz  # PyMuPDF
import re

def analyze_resume_score(file_field):
    """
    Analyzes the resume file and returns an ATS score.
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
            return 50.0

        # Define a more comprehensive list of keywords
        # In a real app, this might be dynamic based on a job description
        keywords = [
            'python', 'django', 'flask', 'api', 'rest', 'fastapi',
            'javascript', 'react', 'vue', 'angular', 'node.js', 'typescript',
            'sql', 'postgresql', 'mysql', 'nosql', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'terraform', 'ci/cd',
            'git', 'agile', 'scrum', 'jira', 'problem solving', 'teamwork'
        ]
        
        score, matched_keywords = calculate_ats_score(text, keywords)
        return score

    except Exception as e:
        print(f"Error analyzing resume: {e}")
        return 0.0  # Return 0 in case of an error
