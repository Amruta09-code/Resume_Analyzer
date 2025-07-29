import os
import google.generativeai as genai
import re
from django.conf import settings

# Configure the client at import time if the key is available
if settings.GOOGLE_API_KEY:
    genai.configure(api_key=settings.GOOGLE_API_KEY)

def generate_interview_questions(domain, count=5):
    # Before making an API call, ensure the key was actually loaded
    if not settings.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY is not configured. Please add it to your .env file.")

    prompt = f"Generate {count} interview questions for the domain: {domain}."
    # Use a current, recommended model like gemini-1.5-flash-latest
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
    response = model.generate_content(prompt)
    questions = response.text.strip().split('\n')
    
    # More robustly clean the output from the model
    cleaned_questions = []
    for q in questions:
        # Remove leading numbers, periods, asterisks, and hyphens
        cleaned_q = re.sub(r'^\s*\d+\.\s*|^\s*[\*\-]\s*', '', q.strip())
        if cleaned_q:
            cleaned_questions.append(cleaned_q)
    return cleaned_questions
