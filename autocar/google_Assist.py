# scp soda@192.168.0.34:/usr/local/lib/python3.6/dist-packages/popAssist.py ./pop/popAssist.py

from pop.popAssist import *

stream = create_conversation_stream()
ga = GAssistant(stream)

print("Taking about ...")
ga.assist()

print("Bye...")
stream.close()
