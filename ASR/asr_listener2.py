import pymongo
from bson.json_util import dumps
import time
import json
from asr_class import *
from asr import asr

# This code listens to changes in the MongoDB collection and triggers the ASR code.

# Connect to MongoDB
client = pymongo.MongoClient('')   # Need to add a specific value here.
print("[INFO] Connected to MongoDB!")

# Load Model
asr_class0 = ASR(do_vad=True, do_diarization=False)

print("[INFO] ******* ASR listener is ready!")

# Listen to changes in InputQueue collection
change_stream = client.ImagesDB.Chromata_InputQueue_ASR.watch()  # May need adaptation!
for change in change_stream:

    request = dumps(change)
    json_request = json.loads(request)

    json_keys = json_request.keys()
    print(json_keys)

    if "fullDocument" in json_keys:
        print(json_request["fullDocument"])

        # Call asr function
        asr(json_request["fullDocument"], asr_class0)

    print("\n[INFO] ******* ASR listener is ready!")

