
# import os
# from flask import Flask, request, render_template, jsonify
# from dotenv import load_dotenv
# import json
# import requests
# from PIL import Image # Import Pillow for image processing
# import pytesseract # Import pytesseract for OCR

# # Load environment variables from .env file
# load_dotenv()

# app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'uploads'
# os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# # Path to the Tesseract executable (IMPORTANT: Update this if Tesseract is not in your PATH)
# pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
# # Example for Linux/macOS (if not in PATH): pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
# # If Tesseract is in your system's PATH, you might not need this line.
# # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Uncomment and set your path

# # Placeholder for API key. In a real application, you would manage this securely.
# # For Canvas environment, __api_key is automatically provided for Gemini API calls.
# # If you are running this locally, you would need to set GOOGLE_API_KEY in your .env file.
# GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# # --- Placeholder Functions for Core Logic (now with actual OCR) ---

# def translate_to_english(text, source_language="auto"):
#     """
#     Placeholder function to translate text from a source language to English.
#     In a real application, you'd use a translation library (e.g., Google Cloud Translation API, DeepL).
#     For this example, it just returns the input text, assuming it's already English or a simple pass-through.
#     """
#     print(f"Translating to English: '{text}' (from {source_language})")
#     return text # For demonstration, assume input is English or directly usable

# def translate_from_english(text, target_language="auto"):
#     """
#     Placeholder function to translate text from English to a target language.
#     In a real application, you'd use a translation library/API.
#     For this example, it just returns the input text.
#     """
#     print(f"Translating from English: '{text}' (to {target_language})")
#     return text # For demonstration, return English text

# def process_image_to_text(image_path):
#     """
#     Performs OCR on the given image file using pytesseract.
#     Requires Tesseract-OCR to be installed on the system.
#     """
#     print(f"Processing image for OCR from: {image_path}")
#     try:
#         # Open the image using Pillow
#         img = Image.open(image_path)
#         # Use pytesseract to extract text
#         text = pytesseract.image_to_string(img)
#         print(f"Extracted text: {text[:100]}...") # Print first 100 chars
#         return text
#     except pytesseract.TesseractNotFoundError:
#         print("Tesseract is not installed or not in your PATH. Please install it.")
#         return "Error: Tesseract OCR engine not found. Please install Tesseract-OCR."
#     except Exception as e:
#         print(f"Error during OCR processing: {e}")
#         return f"Error processing image: {e}"

# # --- Flask Routes ---

# @app.route('/')
# def index():
#     """Renders the main HTML page."""
#     return render_template('index.html')

# @app.route('/process_input', methods=['POST'])
# def process_input():
#     """
#     Handles input from the frontend, processes it, interacts with LLM,
#     and returns the result.
#     """
#     input_text = ""
#     source_input_type = ""
#     operation = request.form.get('operation') # 'summarize' or 'expand'

#     # Voice input is now handled client-side and sent as text_input
#     if 'text_input' in request.form and request.form['text_input']:
#         input_text = request.form['text_input']
#         # Determine if it came from voice based on a hidden field (set by JS)
#         if request.form.get('is_voice_input') == 'true':
#             source_input_type = "voice"
#         else:
#             source_input_type = "text"
#     elif 'image_input' in request.files:
#         image_file = request.files['image_input']
#         if image_file.filename != '':
#             filepath = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
#             image_file.save(filepath)
#             input_text = process_image_to_text(filepath) # Actual OCR
#             source_input_type = "image"
#         else:
#             return jsonify({"error": "No image file provided."}), 400
#     else:
#         return jsonify({"error": "No valid input provided (text, voice, or image)."}), 400

#     if not input_text:
#         return jsonify({"error": "Input text is empty after processing."}), 400

#     # Step 1: Translate source input to English (if not already English)
#     english_input = translate_to_english(input_text, source_language="auto")

#     # Step 2: Interact with LLM (Gemini API)
#     llm_output = call_gemini_api(english_input, operation)

#     # Step 3: Translate LLM output back to original source language
#     final_output = translate_from_english(llm_output, target_language="auto")

#     return jsonify({
#         "original_input": input_text,
#         "llm_processed_english": llm_output,
#         "final_output": final_output,
#         "source_input_type": source_input_type,
#         "operation": operation
#     })

# def call_gemini_api(text, operation):
#     """
#     Calls the Gemini API to summarize or expand the given text.
#     """
#     prompt = ""
#     if operation == "summarize":
#         prompt = f"Summarize the following text concisely: {text}"
#     elif operation == "expand":
#         prompt = f"Expand the following text, adding more detail and context: {text}"
#     else:
#         return "Invalid operation specified for LLM."

#     chatHistory = []
#     chatHistory.append({ "role": "user", "parts": [{ "text": prompt }] })

#     api_key_to_use = GEMINI_API_KEY
#     if '__api_key' in globals():
#         api_key_to_use = globals()['__api_key']

#     payload = { "contents": chatHistory }
#     apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key_to_use}"

#     try:
#         headers = { 'Content-Type': 'application/json' }
#         response = requests.post(apiUrl, headers=headers, data=json.dumps(payload))
#         response.raise_for_status()
#         result = response.json()

#         if result.get("candidates") and result["candidates"][0].get("content") and \
#            result["candidates"][0]["content"].get("parts") and \
#            result["candidates"][0]["content"]["parts"][0].get("text"):
#             return result["candidates"][0]["content"]["parts"][0]["text"]
#         else:
#             print(f"LLM Response Error: {result}")
#             return "Error: Could not get a valid response from the LLM."
#     except requests.exceptions.RequestException as e:
#         print(f"Error calling Gemini API: {e}")
#         return f"Error: Failed to connect to LLM API: {e}"
#     except json.JSONDecodeError as e:
#         print(f"Error decoding JSON from Gemini API: {e}")
#         return f"Error: Invalid JSON response from LLM API: {e}"

# if __name__ == '__main__':
#     app.run(debug=True)
import os
from flask import Flask, request, render_template, jsonify
from dotenv import load_dotenv
import json
import requests
from PIL import Image # Import Pillow for image processing
import pytesseract # Import pytesseract for OCR

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Path to the Tesseract executable (IMPORTANT: Update this if Tesseract is not in your PATH)
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
# Example for Linux/macOS (if not in PATH): pytesseract.pytesseract.tesseract_cmd = r'/usr/local/bin/tesseract'
# If Tesseract is in your system's PATH, you might not need this line.
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # Uncomment and set your path

# Placeholder for API key. In a real application, you would manage this securely.
# For Canvas environment, __api_key is automatically provided for Gemini API calls.
# If you are running this locally, you would need to set GOOGLE_API_KEY in your .env file.
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# --- Placeholder Functions for Core Logic (now with actual OCR) ---

def translate_to_english(text, source_language="auto"):
    """
    Placeholder function to translate text from a source language to English.
    In a real application, you'd use a translation library (e.g., Google Cloud Translation API, DeepL).
    For this example, it just returns the input text, assuming it's already English or a simple pass-through.
    """
    print(f"Translating to English: '{text}' (from {source_language})")
    return text # For demonstration, assume input is English or directly usable

def translate_from_english(text, target_language="auto"):
    """
    Placeholder function to translate text from English to a target language.
    In a real application, you'd use a translation library/API.
    For this example, it just returns the input text.
    """
    print(f"Translating from English: '{text}' (to {target_language})")
    return text # For demonstration, return English text

def process_image_to_text(image_path, languages='eng'):
    """
    Performs OCR on the given image file using pytesseract.
    Requires Tesseract-OCR and specified language packs to be installed on the system.
    'languages' should be a string like 'eng+kan+hin' for multiple languages.
    """
    print(f"Processing image for OCR from: {image_path} with languages: {languages}")
    try:
        # Open the image using Pillow
        img = Image.open(image_path)
        # Use pytesseract to extract text with specified languages
        text = pytesseract.image_to_string(img, lang=languages)
        print(f"Extracted text: {text[:100]}...") # Print first 100 chars
        return text
    except pytesseract.TesseractNotFoundError:
        print("Tesseract is not installed or not in your PATH. Please install it.")
        return "Error: Tesseract OCR engine not found. Please install Tesseract-OCR."
    except Exception as e:
        print(f"Error during OCR processing: {e}")
        return f"Error processing image: {e}"

# --- Flask Routes ---

@app.route('/')
def index():
    """Renders the main HTML page."""
    return render_template('index.html')

@app.route('/process_input', methods=['POST'])
def process_input():
    """
    Handles input from the frontend, processes it, interacts with LLM,
    and returns the result.
    """
    input_text = ""
    source_input_type = ""
    operation = request.form.get('operation') # 'summarize' or 'expand'
    ocr_languages = request.form.getlist('ocr_languages') # Get list of selected OCR languages

    # Default OCR language if none selected or for non-image inputs
    tesseract_lang_string = '+'.join(ocr_languages) if ocr_languages else 'eng'

    # Voice input is now handled client-side and sent as text_input
    if 'text_input' in request.form and request.form['text_input']:
        input_text = request.form['text_input']
        # Determine if it came from voice based on a hidden field (set by JS)
        if request.form.get('is_voice_input') == 'true':
            source_input_type = "voice"
        else:
            source_input_type = "text"
    elif 'image_input' in request.files:
        image_file = request.files['image_input']
        if image_file.filename != '':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
            image_file.save(filepath)
            # Pass the selected OCR languages to the OCR function
            input_text = process_image_to_text(filepath, languages=tesseract_lang_string)
            source_input_type = "image"
        else:
            return jsonify({"error": "No image file provided."}), 400
    else:
        return jsonify({"error": "No valid input provided (text, voice, or image)."}), 400

    if not input_text:
        return jsonify({"error": "Input text is empty after processing."}), 400

    # Step 1: Translate source input to English (if not already English)
    english_input = translate_to_english(input_text, source_language="auto")

    # Step 2: Interact with LLM (Gemini API)
    llm_output = call_gemini_api(english_input, operation)

    # Step 3: Translate LLM output back to original source language
    final_output = translate_from_english(llm_output, target_language="auto")

    return jsonify({
        "original_input": input_text,
        "llm_processed_english": llm_output,
        "final_output": final_output,
        "source_input_type": source_input_type,
        "operation": operation
    })

def call_gemini_api(text, operation):
    """
    Calls the Gemini API to summarize or expand the given text.
    """
    prompt = ""
    if operation == "summarize":
        prompt = f"Summarize the following text concisely: {text}"
    elif operation == "expand":
        prompt = f"Expand the following text, adding more detail and context: {text}"
    else:
        return "Invalid operation specified for LLM."

    chatHistory = []
    chatHistory.append({ "role": "user", "parts": [{ "text": prompt }] })

    api_key_to_use = GEMINI_API_KEY
    if '__api_key' in globals():
        api_key_to_use = globals()['__api_key']

    payload = { "contents": chatHistory }
    apiUrl = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key_to_use}"

    try:
        headers = { 'Content-Type': 'application/json' }
        response = requests.post(apiUrl, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()

        if result.get("candidates") and result["candidates"][0].get("content") and \
           result["candidates"][0]["content"].get("parts") and \
           result["candidates"][0]["content"]["parts"][0].get("text"):
            return result["candidates"][0]["content"]["parts"][0]["text"]
        else:
            print(f"LLM Response Error: {result}")
            return "Error: Could not get a valid response from the LLM."
    except requests.exceptions.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return f"Error: Failed to connect to LLM API: {e}"
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from Gemini API: {e}")
        return f"Error: Invalid JSON response from LLM API: {e}"

if __name__ == '__main__':
    app.run(debug=True)