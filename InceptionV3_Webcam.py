import argparse
import math
import numpy as np
from keras.models import Model
from keras.applications.inception_v3 import InceptionV3
from keras.preprocessing import image
from keras.applications.inception_v3 import preprocess_input, decode_predictions
from pythonosc import osc_message_builder
from pythonosc import udp_client
import cv2
import pyautogui
from pythonosc import dispatcher
from pythonosc import osc_server
import tensorflow as tf

print("I'm working...")
model = InceptionV3(weights='imagenet')
graph = tf.get_default_graph()

stringvalue=""

# Capture webcam:
video_capture = cv2.VideoCapture(0)

client = udp_client.SimpleUDPClient("127.0.0.1", 1234)

def send_osc_handler(unused_addr, args, message):
    print("unused: {}".format(unused_addr))
    print("args: {}".format(args))
    print("message: {}".format(message))    
    
    while(video_capture.isOpened()):
        
        ret, frame = video_capture.read()
        if ret==True:

            global graph
            with graph.as_default():

                # If key is pressed in Processing, the classification stops:
                if stringvalue == "keypress":
                    client.send_message("/stopped", "stopped")
                    setstringvalue() 
                    break        

                cv2.imwrite('webcam.png',frame)
                
                img_path = 'webcam.png'
                img = cv2.resize(cv2.imread(img_path), (299, 299)) # Specific for InceptionV3
                cv2.imwrite("cv_output.png", img)
                x = image.img_to_array(img)
                x = np.expand_dims(x, axis=0)
                x = preprocess_input(x)

                preds = model.predict(x)
                        
                out = decode_predictions(preds, top=int(message))[0]
                    
                print(out)
                output = str(out[0][1])
                cleaned = output.replace("_", " ")
                prob = str("{:.2%}".format(out[0][2]))
                print(cleaned)
                client.send_message("/isadora/1", "{}".format(cleaned))
                client.send_message("/isadora/2", "{}".format(prob))
        else:
            break

# Resetting the stringvalue after proces is stopped:
def setstringvalue():
    global stringvalue
    stringvalue=""

def stopsending(unused_addr, message1):
    print(message1)
    global stringvalue
    stringvalue = message1

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip",
      default="127.0.0.1", help="The ip to listen on")
  parser.add_argument("--port",
      type=int, default=5005, help="The port to listen on")
  args = parser.parse_args()

  dispatcher = dispatcher.Dispatcher()
  dispatcher.map("/miklo", send_osc_handler, "Miklo")
  dispatcher.map("/miklokey",stopsending)

  server = osc_server.ThreadingOSCUDPServer(
      (args.ip, args.port), dispatcher)
  print("Serving on {}".format(server.server_address))
  server.serve_forever()