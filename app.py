from flask import Flask, request, jsonify, make_response,send_file
import requests
from google import genai
from google.genai import types
import httpx
import os
import json
import sys
site_packages = os.path.join(os.path.dirname(__file__), 'venv', 'lib', 'python3.11', 'site-packages')
if site_packages not in sys.path:
    sys.path.insert(0, site_packages)

GEMINI_KEY = os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
app = Flask(__name__)
gemini_client = genai.Client(api_key = GEMINI_KEY)

@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/generate', methods=['POST'])
def generate_questions():
    
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['pdf']
    prompt = f"""
        Analyze the PDF file and generate 20 questions comprising of easy, medium, and hard questions.
        The questions should be based on the content of the PDF file.
        The number of easy questions should be higher than the number of medium and hard questions. Keep a maximum of 3 hard questions.
        The questions should be relevant to the content of the PDF file.
        Include atleast 3 true/false questions.
        Include one or two problems that require calculations. But the total time for calculation should not exceed more than 20 seconds. The problems for calculation must be easy.
        The questions should be in the following format:
        Question: <question>
        Options:
        a) <option1>
        b) <option2>
        c) <option3>
        d) <option4>
        Answer:<correct option>
        Next Question...
        
        Return the questions as an array of JSON objects. Where each object consists of a question field, an options field, and an answer field.
        The options field should be an array of options.
        The answer field should be the correct option.
        The questions should be in English.
        The questions must not be out of syllabus compared to the file.
        Return the option letter in lowercase in the answer field.
        Do not repeat the same question.
        Do not include any other text in the response.
        Do not include any markdown code block markers in the response.
    """
    
    try:
        
        response = gemini_client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[
            types.Part.from_bytes(
                data=file.read(),
                mime_type='application/pdf',
            ),
            prompt])
        print(response.text)

        print(file.filename)
    except:
        return jsonify({'error': 'Failed to generate questions'}), 500
        
    try:
        cleaned_text = response.text.strip()
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]  
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]  
        cleaned_text = cleaned_text.strip()
        
        response_json = json.loads(cleaned_text)
        return jsonify(response_json)
    except json.JSONDecodeError as e:
        return jsonify({'error': f'Failed to parse response as JSON: {str(e)}'}), 500