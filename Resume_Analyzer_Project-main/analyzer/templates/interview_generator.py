import google.generativeai as genai
from django.conf import settings

def generate_interview_questions(domain):
    # Safely get the Gemini API key from Django settings
    api_key = getattr(settings, "GOOGLE_API_KEY", None)

    if not api_key:
        return ["Google Gemini API key not found. Please check your settings."]

    try:
        # Configure the Gemini API
        genai.configure(api_key=api_key)

        # Create a Gemini model instance
        model = genai.GenerativeModel("gemini-pro")

        # Prepare a prompt for the model
        prompt = f"Generate 5 interview questions for a candidate in the domain of {domain}."

        # Generate content from the model
        response = model.generate_content(prompt)

        # Return the list of questions
        if hasattr(response, "text"):
            return [q for q in response.text.split("\n") if q.strip()]
        else:
            return ["No response text from Gemini."]
    except Exception as e:
        return [f"Error generating questions: {str(e)}"]
