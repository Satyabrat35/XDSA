# Low latency Video Conferencing APP over LAN

## Idea
#### The basic idea was to build a conferencing app in python with TCP/IP using the power of sockets and multithreading and the high link speed of LAN to provide real time video calling and conferencing experience. 
The video frame acquisition is done through the openCV library of python. The video frames are encoded and compressed and sent over LAN to the recipients. At the other end the video frames are decoded and displayed. This backend is integrated with flask and resulting recieved frames are displayed on the browser.



## Tools
### 
- Python
- Sockets
- Multithreading
- FLask
- OpenCV
- PyAudio
- dlib
- Bootstrap

## Instructions to run the script
1. Make sure all the dependencies are installed beforehand
2. Open ```cmd``` and navigate to the project directory and execute ```python f1.py```
3. From your favourite browser navigate to ```127.0.0.1:5000``` in the url bar
4. Now you can either host the conference by pressing ```Host``` or join by pressing ```Connect```
5. Voila!

## Future scope
Right now we have implemented attractive filters to a video feed and we trying to integrate it with the rest of the code. After that, we aim to make a standalone software of the same which can be deployed in various colleges with LAN connectivity. We are also trying to improve our latency.

