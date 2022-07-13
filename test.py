from threading import *
import time
from queue import Queue

def updateInput(messages):
    text= "haha" #"This is just a test"
    messages.put(text)
    #anothertext= "haha" #"This is just a test"
    #messages.put(anothertext)


def handleInput(messages):
    try:
        while True: # Optional, you can loop to, continuously, print the data in the queue
            if not messages.empty():
                text= messages.get()
                print(text)

            clientInput = input("\r>")
    except KeyboardInterrupt:
        print("Done reading! Interrupted!")

if __name__ == "__main__":
    messages = Queue()
    writer = Thread(target=updateInput, args=(messages,))
    worker = Thread(target=handleInput, args=(messages,))

    writer.start()
    worker.start()

    writer.join()
    worker.join()