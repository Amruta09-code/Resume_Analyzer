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
    # Convert to lower for case-insensitive matching
    matched_keywords_lower = [k.lower() for k in matched_keywords]

    # Check for more specific domains first to ensure accuracy
    if any(word in matched_keywords_lower for word in ['android', 'kotlin', 'java', 'jetpack', 'sdk']):
        return "Android Development"
    if any(word in matched_keywords_lower for word in ['devops', 'ci/cd', 'jenkins', 'docker', 'kubernetes', 'ansible', 'terraform']):
        return "DevOps"
    if any(word in matched_keywords_lower for word in ['ui', 'ux', 'figma', 'sketch', 'adobe xd', 'wireframe', 'prototype']):
        return "UI/UX Design"
    if any(word in matched_keywords_lower for word in ['python', 'django', 'flask', 'api', 'rest', 'fastapi', 'node.js', 'javascript', 'react']):
        return "Web Development"
    if any(word in matched_keywords_lower for word in ['ml', 'ai', 'data', 'tensorflow', 'pytorch', 'scikit-learn']):
        return "Data Scientist"
    if any(word in matched_keywords_lower for word in ['public speaking', 'presentation', 'communication', 'toastmasters']):
        return "Public Speaking"
    if any(word in matched_keywords_lower for word in ['marketing', 'seo', 'analytics']):
        return "Digital Marketing"
        
    return "General"
