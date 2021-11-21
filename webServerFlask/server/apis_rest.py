import os
import random
from datetime import datetime

import yaml
from azure.storage.blob import ContainerClient
from flask import request
from flask_restful import Resource

# loads the configuration file
with open("../config/config.yaml", "r") as yamlfile:
    configuration = yaml.load(yamlfile, Loader=yaml.FullLoader)

# creates a container client in azure storage
container_client = ContainerClient.from_connection_string(
    configuration["azure_storage_connectionstring"],
    configuration["azure_storage_container"],
)


# API for video saving
class Audio(Resource):
    def post(self):
        filename = datetime.now()
        filename = filename.strftime("%d%m%Y%H%M%S%f")
        audio = request.files['audio_data'].read()
        text_id = request.form['text_id']

        if configuration["use_azure"]:
            # saves the audio as a blob in azure storage
            blob_client = container_client.get_blob_client(f"{text_id}_{filename}.mp3")
            blob_client.upload_blob(audio)
        else:
            os.makedirs("../audio", exist_ok=True)
            # saves the audio combining text id and the current date/time to make it unic
            with open(f"../audio/{text_id}_{filename}.mp3", 'wb') as f:
                f.write(audio)


# API for text handling
class Text(Resource):
    def get(self):
        # get random string from sentences file
        with open("../sentences/sentences.txt", 'r') as txt:
            strings = txt.read().split('\n')

        sample = random.sample(strings, 1)[0]
        sent_to_send = sample.split(sep=' ', maxsplit=1)

        # send the sentence id and the sentence to the application
        return {'id': sent_to_send[0], 'sentence': sent_to_send[1]}
