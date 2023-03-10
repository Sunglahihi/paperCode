from __future__ import division
import re
import sys
from google.cloud import speech
import pyaudio
from six.moves import queue
import cv2
import serial
import pymysql
from multiprocessing import Process
from threading import Thread

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)
  
save_user = pymysql.connect(
    user='root', 
    passwd='0000', 
    host='127.0.0.1', 
    db='camuser', 
    charset='utf8'
)

index = 0
arduino = serial.Serial('COM3',9600)
cam = cv2.VideoCapture(0) 
cursor = save_user.cursor(pymysql.cursors.DictCursor)
sql = "SELECT name_kor FROM camuser.user"
cursor.execute(sql)
result = cursor.fetchall()
print(result)
name = []
for i in range(len(result)):
    a = list(result[i].values())
    name.append(a[0])

sql = "SELECT median FROM camuser.user"
cursor.execute(sql)
result = cursor.fetchall()
print(result)
angle = []

for i in range(len(result)):
    a = list(result[i].values())
    angle.append(a[0])

def listen_print_loop(responses):
    """Iterates through server responses and prints them.
    The responses passed is a generator that will block until a response
    is provided by the server.
    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.
    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()
            a= transcript.strip()
            print(a)
            if a in name:
                index = name.index(a)
                print(str(name[index])+'?????? ???????????????.')
            else: 
                print('???????????? ????????????.')
                continue   

            motor_angle = str(angle[index])
            if (motor_angle == '0'):
                print('???????????? ???????????? ???????????????.')
                continue
            tran_angle = motor_angle.encode('utf-8')
            arduino.write(tran_angle)
    

            key = cv2.waitKey(1) & 0xFF
            if key ==27:  
                num_chars_printed = 0
                break

            num_chars_printed = len(transcript)

def main():
    # See http://g.co/cloud/speech/docs/languages
    # for a list of supported languages.
    language_code = 'ko-KR'  # a BCP-47 language tag

    client = speech.SpeechClient()
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)
    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses)


def cam_detector():
    while(True):
        ret, frame = cam.read() 
        cv2.imshow('frame',frame) 
        key = cv2.waitKey(1) & 0xFF
        if key ==27:  
            break

    cam.release()  
    cv2.destroyAllWindows()  


if __name__ == "__main__":
   thread1 = Thread(target=main)
   thread1.start()

   thread2 = Thread(target=cam_detector)
   thread2.start()
    