# import re
# import requests
# import whisper
# from Levenshtein import distance
#
# # Load the pre-trained Whisper model
# model = whisper.load_model("small")  # Choose model size based on your hardware. Options: "tiny", "base", "small", "medium", "large"
#
# # Load and transcribe audio
# audio_path = "1.mp3"
# result = model.transcribe(audio_path, language="ar")  # 'language="ar"' specifies Arabic transcription
#
# # Get the transcription text
# transcription = result["text"]
#
# # Remove diacritical marks and non-Arabic characters
# def clean_arabic_text(text):
#     # Remove diacritical marks
#     text = re.sub(r"[\u064B-\u0652]", "", text)
#     # Remove non-Arabic characters (digits, English letters, punctuation, etc.)
#     text = re.sub(r"[^\u0600-\u06FF\s]", "", text)
#     return text
#
# cleaned_transcription = clean_arabic_text(transcription)
# print("Cleaned Transcription:", cleaned_transcription)
#
# # Specify the Surah and Ayah number
# surah_number = 1  # Al-Fatihah
# ayah_number = 1   # First verse
#
# # API endpoint
# url = f"https://api.alquran.cloud/v1/ayah/{surah_number}:{ayah_number}"
#
# # Make the request
# response = requests.get(url)
#
# # Check if the request was successful
# if response.status_code == 200:
#     data = response.json()
#     # Access the Ayah text
#     ayah_text = data['data']['text']
#     cleaned_ayah_text = clean_arabic_text(ayah_text)
#     print(f"Ayah Text: {cleaned_ayah_text}")
#
#     # Calculate the Levenshtein distance and similarity percentage
#     def calculate_similarity(transcribed, original):
#         lev_distance = distance(transcribed, original)
#         max_length = max(len(transcribed), len(original))
#         accuracy = ((max_length - lev_distance) / max_length) * 100
#         return accuracy
#
#     accuracy_percentage = calculate_similarity(cleaned_transcription, cleaned_ayah_text)
#     print(f"Accuracy Percentage: {accuracy_percentage:.2f}%")
# else:
#     print("Failed to retrieve the Ayah")


from flask import Flask, request, jsonify

import re
import requests
import whisper
from Levenshtein import distance

# Initialize Flask app
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load the Whisper model
model = whisper.load_model("small")  # Choose the appropriate size based on your hardware

# Function to clean Arabic text
# Function to clean Arabic text
# Function to clean Arabic text
# Function to clean Arabic text
def clean_arabic_text(text):
    # Remove all diacritical marks, including Arabic glyph decorations
    text = re.sub(r"[\u064B-\u065F\u0670\u06D6-\u06ED]", "", text)
    # Remove non-Arabic characters (digits, English letters, punctuation, etc.)
    text = re.sub(r"[^\u0600-\u06FF\s]", "", text)
    # Remove extra spaces and newline characters
    text = re.sub(r"\s+", " ", text).strip()
    return text



# Function to calculate similarity
def calculate_similarity(transcribed, original):
    lev_distance = distance(transcribed, original)
    max_length = max(len(transcribed), len(original))
    accuracy = ((max_length - lev_distance) / max_length) * 100
    return accuracy

# API endpoint
@app.route('/transcribe', methods=['POST'])
def transcribe():
    try:
        # Get request arguments
        audio_file = request.files.get('audio')
        surah_number = request.form.get('surah_number', type=int)
        ayah_number = request.form.get('ayah_number', type=int)

        if not audio_file or surah_number is None or ayah_number is None:
            return jsonify({"error": "Missing required parameters"}), 400

        # Save audio file temporarily
        audio_path = "temp_audio.mp3"
        audio_file.save(audio_path)

        # Transcribe audio
        result = model.transcribe(audio_path, language="ar")
        transcription = result["text"]
        cleaned_transcription = clean_arabic_text(transcription)

        # Fetch Ayah text
        url = f"https://api.alquran.cloud/v1/ayah/{surah_number}:{ayah_number}"
        response = requests.get(url)

        if response.status_code != 200:
            return jsonify({"error": "Failed to retrieve Ayah"}), 500

        data = response.json()
        ayah_text = data['data']['text']
        cleaned_ayah_text = clean_arabic_text(ayah_text)

        # Calculate accuracy
        accuracy_percentage = calculate_similarity(cleaned_transcription, cleaned_ayah_text)

        # Return results
        return jsonify({
            "transcription": cleaned_transcription,
            "original_text": cleaned_ayah_text,
            "accuracy": f"{accuracy_percentage:.2f}%"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
