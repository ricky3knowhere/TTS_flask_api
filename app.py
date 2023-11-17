from flask import Flask, request, jsonify, make_response, send_from_directory

import librosa
import soundfile as sf
import os
import io
import wave
import numpy as np
import speech_recognition as sr
from flask_cors import CORS
from gtts import gTTS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)


@app.route("/api/text-to-speech/<fileName>", methods=["GET"])
def get_audio(fileName):
    # Appending app path to upload folder path within app root folder
    uploads = app.root_path
    # Returning file from appended path
    return send_from_directory(uploads, fileName, as_attachment=True)


@app.route("/api/text-to-speech", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        try:
            url = "http://127.0.0.1:5000/api/text-to-speech/generated-speech.wav"
            return make_response(jsonify({"url": url})), 200

        except Exception as err:
            error_message = "An error occurred: " + str(err)
            return make_response(jsonify({"error": error_message}), 500)
    else:
        try:
            dir_name = "./"
            test = os.listdir(dir_name)

            for item in test:
                if item.endswith(".wav"):
                    os.remove(os.path.join(dir_name, item))

            text_data = request.get_json()["textData"]
            random = round(np.random.rand() * 100000)
            generated_speech = f"generated-speech-{random}.wav"
            print("text_data", text_data)
            # Mengkonversi teks menjadi suara menggunakan Google Text-to-Speech
            # Parameter lang: kode bahasa
            tts = gTTS(text_data, lang="id")

            # Menyimpan file suara
            tts.save(generated_speech)  # Save hasil suara menggunakan TTS

            y, sr = librosa.load(generated_speech)
            sf.write(
                generated_speech, y, sr
            )  # Hasil save dari TTS, dibuka dan ditulis ulang oleh librosa

            res = {"fileName": generated_speech, "message": "Succes generated"}
            return make_response(jsonify(res)), 200
        except Exception as err:
            error_message = "An error occurred: " + str(err)
            return make_response(jsonify({"error": error_message}), 500)

@app.route("/api/speech-to-text", methods=["POST"])
def speech_to_text():
    recognizer = sr.Recognizer()
    audio_file = request.files["audio"].read()
    # print(audio_file)
    # audio_file = request.files['name']
    # print('audio_file ==>>', audio_file)
    # audio_file = io.BytesIO(audio_file)
    # print("audio_file ==>>", audio_file)
    # # Save the audio Blob as a file in the uploads folder
    # filename = secure_filename("uploaded_audio.wav")
    # file_path = os.path.join("./temp/", filename)
    file_path = "./temp/tmp.wav"
    try:
        with open(file_path, "wb") as f:
            f.write(audio_file)
        print(10*'<<===='+'Done')
    except Exception as err:
        print("Error =======>>> ", err)

    try:
        x, _ = librosa.load(file_path, sr=16000)
        sf.write(file_path, x, 16000)
        wave.open(file_path, "r")
        print('audio file =====>>> loaded')
    except Exception as err:
        print("Error =======>> ", err)

    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio_data, language="id-ID")
        return jsonify({"text": text})
    except sr.UnknownValueError:
        print(7 * "=======#" + "Speech Recognition could not understand audio")
        return jsonify({"error": "Speech Recognition could not understand the audio"}), 400
    except sr.RequestError as e:
        print(7 * "=======#" + e)
        return jsonify({"error": f"Speech Recognition request failed: {e}"}), 500
    except Exception as err:
        print("Error ========> ", err)
