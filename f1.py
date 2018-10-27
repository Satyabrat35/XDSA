from flask import Flask, render_template, Response, jsonify
from camera import VideoCamera
import os
import random

app = Flask(__name__)

@app.route('/')
def home():
    #os.system("python3 script.py")
    return render_template('home.html')

@app.route('/hosted')
def hosting():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen(VideoCamera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/audio')
def listen():
    lst = ['hjd','sdsd','asas']
    words = {}
    words['choice'] = random.choice(lst)
    print("success")
    return "jbsdj"


if __name__ == "__main__":
    app.run(debug=True)