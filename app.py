from flask import Flask, request, jsonify, make_response, send_from_directory

import librosa
import soundfile as sf
import os
import numpy as np
from flask_cors import CORS
from gtts import gTTS

# from IPython.display import Audio
# from IPython.display import display
# from pydub import AudioSegment

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

            # Menjalankan dan menampilkan audio player
            # play_suara = Audio(generated_speech, autoplay=True)
            # display(play_suara)
            res = {"fileName": generated_speech, "message": "Succes generated"}
            return make_response(jsonify(res)), 200
        except Exception as err:
            error_message = "An error occurred: " + str(err)
            return make_response(jsonify({"error": error_message}), 500)
