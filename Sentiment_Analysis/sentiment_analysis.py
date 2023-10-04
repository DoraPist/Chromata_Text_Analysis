import redis
import json
import time
import os
from sentiment_analysis_class import *
from upload_download_files import S3Handler

def sentiment_analysis(message, sentiment_class):
    print(message)

    start_time = time.time()
    media_id = message["id"]
    path = os.getcwd() + "/Data/" + str(media_id) + "/"
    os.makedirs(path, exist_ok=True)   
    text_path = "C:/Chromata/Services_v1/ASR2/Data/" + str(message['text_id']) + "/" + str(
        message['text_id']) + "_produced_text.txt"

    # New!!! ---------------------------------
    # Create an instance of the S3Handler
    s3 = S3Handler(            # Need to add specific values here!
        aws_access_key_id="",
        aws_secret_access_key="",
        bucket_name=""
    )

    print("[INFO] Downloading text file...")

    with open(text_path, mode='r', encoding='utf-8') as f:
        text = f.read()

    # run sentiment analysis    
    sentiment_results = sentiment_class.run_sentiment_analysis(text, clean_text = True)
    
    # ...
    # ...
    # --------------------------> Create output JSON with sentiment information

    sentiment_info = {}
    sentiment_info["workspace"] = message["workspace"]
    sentiment_info["id"] = message["id"]
    sentiment_info["text_id"]=message["id"]
    sentiment_info["project_id"] = message["project_id"]
    sentiment_info["object_type"] = message["object_type"]
    sentiment_info["user_id"] = message["user_id"]
    sentiment_info["sender"] = "sentiment-analysis"
    sentiment_info["subjectivity"] = 1.0    
   
    sentiment_info["anger"] = sentiment_results["anger"]
    sentiment_info["disgust"] = sentiment_results["disgust"]
    sentiment_info["fear"] = sentiment_results["fear"]
    sentiment_info["happiness"] = sentiment_results["happiness"]
    sentiment_info["sadness"] = sentiment_results["sadness"]
    sentiment_info["surprise"] = sentiment_results["surprise"]
    sentiment_info["negative"] = sentiment_results["negative"]
    sentiment_info["positive"] = sentiment_results["positive"]

    with open(path + 'sentiment_info_output.json', 'w', encoding='utf8') as outfile:
        json.dump(sentiment_info, outfile, ensure_ascii=False)

  print("[INFO] Sentiment info output was saved in " + path + 'sentiment_info_output.json')

    end_time = time.time()
    print("[INFO] Sentiment-analysis took {} seconds".format(end_time - start_time))

    # Send output json to 'completed-jobs' topic
    environment = 'completed-jobs'
    x = json.dumps(sentiment_info)

    try:
        client = redis.Redis(host="", port=, password="")  # Need to add specific values here!
        client.publish(environment, x)
        print("[INFO] Sentiment-analysis result was successfully sent!")
    except Exception as e:
        print(f"ERROR:  {e}")

