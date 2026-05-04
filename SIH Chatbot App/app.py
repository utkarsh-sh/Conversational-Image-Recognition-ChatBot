# app.py - The Backend Server

import os
import io
import base64
import torch
from flask import Flask, request, jsonify, render_template
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

# --- 1. Initialize the Flask App ---
app = Flask(__name__)

# --- 2. Load Your Fine-Tuned Model ---
# This path now correctly points one directory up to find the model folder.
MODEL_PATH = "my_finetuned_blip_model"

print("Loading fine-tuned model... This may take a moment.")
processor = BlipProcessor.from_pretrained(MODEL_PATH)
model = BlipForConditionalGeneration.from_pretrained(MODEL_PATH)
device = "cpu"
model.to(device)
print(f"Model loaded successfully on device: {device}")


# --- 3. Define the Routes (The "Doors" to your Application) ---

# This is the main door: it serves the user interface.
@app.route('/')
def home():
    # Flask will look inside the 'templates' folder for this file.
    return render_template('index.html')


# This is the AI door: it handles the prediction logic.
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    try:
        # Decode the image sent from the frontend
        image_data = base64.b64decode(data['image'])
        image = Image.open(io.BytesIO(image_data)).convert('RGB')
        question = data['question']

        # Use the AI model to get an answer
        inputs = processor(image, question, return_tensors="pt").to(device)
        out = model.generate(**inputs, max_length=50)
        answer = processor.decode(out[0], skip_special_tokens=True)

        # Send the answer back to the frontend
        return jsonify({'answer': answer})

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': 'An internal error occurred.'}), 500


# --- 4. Run the Application ---
if __name__ == '__main__':
    # This starts the web server.
    app.run(host='0.0.0.0', port=5000)

