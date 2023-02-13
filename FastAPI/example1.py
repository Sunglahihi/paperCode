import cv2

def getCameraStream():
    cam = cv2.VideoCapture(0)

    while True:
        ret, mat = cam.read()
        if not ret:
            break

        ret, jpgI = cv2.imencode('.jpg', mat)

        jpgB = bytearray(jpgI.tobytes())

        yield (b'--PNPframe\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            jpgB + b'\r\n')