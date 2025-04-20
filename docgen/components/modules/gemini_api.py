from google import genai
import os

# Replace with your actual Gemini API key
client = genai.Client(api_key="AIzaSyCpnKIRxaHb1bH9IdDhl7qrrypJVD4Ytf4")

def generate_report_sections(topic, context):
    prompt = f"""
    Generate a professional IT report on the topic: '{topic}'.
    Context: {context}
    Divide the content into the following sections:
    1. Introduction
    2. Background
    3. Methodology
    4. Findings
    5. Conclusion
    Return it as a dictionary with keys as section titles.
    """
    response = client.models.generate_content(
    model="gemini-2.0-flash", contents=prompt
)
    text = response.text

    # Basic parser
    sections = {}
    current_section = None
    for line in text.split('\n'):
        if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
            current_section = line.strip().split('.', 1)[1].strip()
            sections[current_section] = ''
        elif current_section:
            sections[current_section] += line.strip() + ' '

    return sections
