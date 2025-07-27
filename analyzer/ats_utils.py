import fitz  # PyMuPDF
import re
import os


def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    # remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text

def calculate_ats_score(text, keywords):
    score = 0
    matched = []
    for keyword in keywords:
        # prevent ReDOS
        keyword = re.escape(keyword)

        if re.search(rf'\b{keyword}\b', text, re.IGNORECASE):
            score += 10
            matched.append(keyword)
    return min(score, 100), matched

def get_domain_from_keywords(matched_keywords):
    if any(word in matched_keywords for word in ['python', 'django', 'flask']):
        return "Software Developer"
    if any(word in matched_keywords for word in ['ml', 'ai', 'data']):
        return "Data Scientist"
    if any(word in matched_keywords for word in ['marketing', 'seo']):
        return "Digital Marketing"
    return "General"
