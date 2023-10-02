import os
import json
import time
from upload_download_files import S3Handler
import redis
import librosa
import moviepy.editor as mp

def asr(message, asr_class):

    start_time = time.time()

    # Create an instance of the S3Handler
    s3 = S3Handler(                            # Need to add specific values here!
        aws_access_key_id="",
        aws_secret_access_key="",
        bucket_name=""
    )

    # Create a folder for the current media
    media_id = message["id"]
    path = os.getcwd()+"/Data/" + str(media_id) + "/"
    os.makedirs(path, exist_ok=True)

    # Save the input json
    with open(path + "input.json", "w") as f:
        json.dump(message, f)

    if message["object_type"] != 'text':

        # Get media url
        media_url = message["object_path_or_text"]

        # --------------------------> Download file
		
        file_format=media_url.split('.')[-1]

        filename = str(media_id) +'.'+ file_format

        # Define path to save the derived
        ROOT_PATH_FOR_SENTIMENT_ANALYSIS = "subservices/sentiment_analysis/" + str(media_id)  # this is a static path

        print("[INFO] Downloading media file...")

        s3.download_file(
            object_name=media_url,
            output_file=path + filename
        )

        # convert file to sound if is video
        #......
        if message["object_type"] == 'video':        
            clip = mp.VideoFileClip(path+filename)
            filename = str(media_id) +'.wav'
            clip.audio.write_audiofile(path+filename)

        #......


        #call asr function like text=asr(file) to transform speech to text
        s,sr=librosa.load(path+filename,sr = 16000)
        text = asr_class.run_ASR(s, sr)
        #....
        #....

    else:
        text = message["object_path_or_text"]

    text_filename = str(media_id) + '_produced_text.txt'

    with open(path + text_filename, 'w', encoding='utf-8') as f:
        f.write(text)

    asr_info = {}
    asr_info["workspace"] = message["workspace"]
    asr_info["id"] = message["id"]
    asr_info["project_id"] = message["project_id"]
    #asr_info["text_id"] = path + text_filename
    asr_info["text_id"] = media_id
    asr_info["text"] = text
    asr_info["object_type"] = message["object_type"]
    asr_info["user_id"] = message["user_id"]
    asr_info["sender"] = "ASR"

    with open(path + 'asr_info_output.json', 'w') as outfile:
        json.dump(asr_info, outfile)

    print("[INFO] ASR info output was saved in ", path + 'asr_info_output.json')

    end_time = time.time()
    print("[INFO] ASR took {} seconds".format(end_time - start_time))

    # Send output json to 'completed-jobs' topic
    environment = 'completed-jobs'
    x = json.dumps(asr_info)

    try:
        client = redis.Redis(host="", port=, password="")   # Need to add specific values here!
        client.publish(environment, x)
        print("[INFO] ASR result was successfully sent!")
    except Exception as e:
        print(f"ERROR:  {e}")
