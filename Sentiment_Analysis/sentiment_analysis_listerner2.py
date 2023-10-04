import pymongo
from bson.json_util import dumps
import time
import json
from sentiment_analysis_class import *
from sentiment_analysis import sentiment_analysis

# This code listens to changes in the MongoDB collection and triggers the sentiment analysis code.

# Connect to MongoDB
client = pymongo.MongoClient('')  # Need to add specific value here!
print("[INFO] Connected to MongoDB!")

##Load Sentiment-Analysis Model

sentiment_class = Sentiment_Analysis('lighteternal/stsb-xlm-r-greek-transfer', ["χαρά", "έκπληξη", "λύπη", "φόβος", "θυμός", "απέχθεια", "θετικό", "αρνητικό"], pretrained = True)

print("[INFO] ******* Sentiment-analysis listener is ready!")

# Listen to changes in InputQueue collection
change_stream = client.ImagesDB.Chromata_InputQueue_SA.watch()  # May need adaptation.

for change in change_stream:

    request = dumps(change)
    json_request = json.loads(request)

    json_keys = json_request.keys()
    print(json_keys)

    if "fullDocument" in json_keys:
        print("\n\n [INFO] ******* Received a new request: \n")
        print(json_request["fullDocument"])

        sentiment_analysis(json_request["fullDocument"], sentiment_class)

    print("\n[INFO] ******* Sentiment-analysis listener is ready!")
