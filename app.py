import os
import base64
import requests
import json
import re
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from flask_cors import CORS

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("Please set GEMINI_API_KEY in your .env file.")

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = '/tmp'
app.config['MAX_CONTENT_LENGTH'] = 15 * 1024 * 1024

def clean_json(text_output):
    # Remove markdown code fences like ```json  ``` or ```JSON  ```
    cleaned = re.sub(r"```(?:json|JSON)?", "", text_output).strip()
    cleaned = cleaned.replace("```", "").strip()

    # Extract JSON object only
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError("No valid JSON object found.")
    
    json_str = match.group()

    # Return the JSON string for later parsing
    return json_str

def identify_lab_equipment_from_bytes(image_bytes, mime_type="image/jpeg"):
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": PROMPT},
                    {"inline_data": {"mime_type": mime_type, "data": image_base64}}
                ]
            }
        ]
    }

    r = requests.post(
        f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
        headers=headers,
        json=payload,
        timeout=60
    )
    print(f"req. response code {r.status_code}")

    if r.status_code != 200:
        return {"error": f"{r.status_code}: {r.text}"}

    result = r.json()
    try:
        text_output = result["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return {"error": "Unexpected response format from model.", "raw": result}

    print("converting the content into JSON.....")
    cleansed_json_str = clean_json(text_output)
    print(cleansed_json_str)
    try:
        data = json.loads(cleansed_json_str)
        print(f"data type of the json is {type(data)}")
        print(data)
        return data
    except Exception:
        return {"error": "Unexpected response format from model: JSON conversion failed." }

PROMPT = (
    "You must analyze the provided image of a room and output ONLY valid JSON in the following structure: "
    "{\"sustainability_score\": <number_1_to_10>, "
    "\"items\": [{\"name\": \"<item_name>\", \"description\": \"<brief_description_max_10_words>\"}], "
    "\"greener_alternatives\": [{\"name\": \"<item_name>\", \"alternative\": \"<alternative_suggestion_max_15_words>\"}], "
    "\"temperature_regulation_suggestions\": [\"<suggestion_max_20_words>\"]}. "
    "Tasks: 1) Identify all items in the room and describe each briefly (max 10 words). "
    "2) Provide a sustainability score (1–10). "
    "3) Suggest greener alternatives for each item (max 15 words per alternative). "
    "4) Provide ways to improve temperature regulation (max 20 words per suggestion). "
    "Output strictly valid JSON—no explanations, no extra text. Keep all responses very concise."
)


@app.route('/')
def index():
    return render_template('index.html')

@app.post("/api/identify")
def identify_api():
    if 'images' not in request.files:
        return jsonify({"error": "No images provided. Use field name 'images'."}), 400

    files = request.files.getlist('images')
    results = []

    for idx, f in enumerate(files):
        filename = secure_filename(f.filename or f"image_{idx}.jpg")
        if not filename:
            results.append({"index": idx, "filename": None, "error": "Empty filename."})
            continue

        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "jpg"
        mime = "image/jpeg"
        if ext in ("png",): mime = "image/png"
        if ext in ("webp",): mime = "image/webp"

        try:
            image_bytes = f.read()
            if not image_bytes:
                results.append({"index": idx, "filename": filename, "error": "Empty file."})
                continue

            out = identify_lab_equipment_from_bytes(image_bytes, mime)
            out.update({"index": idx, "filename": filename})
            results.append(out)
        except Exception as e:
            results.append({"index": idx, "filename": filename, "error": str(e)})

    return jsonify({"results": results})

if __name__ == "__main__":
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    print("Starting Flask server on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
