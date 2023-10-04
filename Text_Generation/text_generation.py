import redis
import json
import time
import os
from text_gen import *

def text_generation(message):

    print(message)

    start_time = time.time()
    media_id = message["id"]
    path = os.getcwd() + "/Data/" + str(media_id) + "/"
    print('paaath:', path)
    os.makedirs(path, exist_ok=True)
    text_path = "C:/Chromata/Services_v1/ASR2/Data/"+str(message['text_id'])+"/"+str(message['text_id'])+"_produced_text.txt"
    with open(text_path, mode="r", encoding="utf-8") as f:
        text = f.read()
    
    
    #run text generation
    text = text_gen(text)
    
    # --------------------------> Create output JSON with textgen information

    textgen_info = {}
    textgen_info["workspace"] = message["workspace"]
    textgen_info["id"] = message["id"]
    textgen_info["text_id"] = message["id"]
    textgen_info["project_id"] = message["project_id"]
    textgen_info["object_type"] = message["object_type"]
    textgen_info["text"] = text
    textgen_info["user_id"] = message["user_id"]
    textgen_info["sender"] = "text-generation"

    with open(path+'textgen_info_output.json', 'w', encoding='utf8') as outfile:
        json.dump(textgen_info, outfile, ensure_ascii=False)

    print("[INFO] Text-generation info output was saved in " + path + 'textgen_info_output.json')

    end_time = time.time()
    print("[INFO] Text-generation took {} seconds".format(end_time - start_time))

    # Send output json to 'completed-jobs' topic
    environment = 'completed-jobs'
    # action = outfile
    x = json.dumps(textgen_info)

    try:
        client = redis.Redis(host="", port=, password="")   # Need to add specific values here!!
        client.publish(environment, x)
        print("[INFO] Text-generation result was successfully sent!")
    except Exception as e:
        print(f"ERROR:  {e}")
