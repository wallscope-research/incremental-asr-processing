import json
import sys
import re
from os.path import join, dirname
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

infile = sys.argv[1]
filename_prep = re.search(r"(?<=data\/)(.*?)(?=\.wav)", infile).group(0)
outfile = "./results/" + filename_prep + ".txt"
with open(outfile, 'w') as of:
        print(filename_prep, file=of)

authenticator = IAMAuthenticator('your key')    ## Add your key
speech_to_text = SpeechToTextV1(
    authenticator=authenticator
)

speech_to_text.set_service_url('your url')      ## Add your url


class MyRecognizeCallback(RecognizeCallback):
    def __init__(self):
        RecognizeCallback.__init__(self)

    def on_data(self, data):
        with open(outfile, 'a') as of:
            print(json.dumps(data, indent=2), file=of)

    def on_error(self, error):
        print('Error received: {}'.format(error))

    def on_inactivity_timeout(self, error):
        print('Inactivity timeout: {}'.format(error))

myRecognizeCallback = MyRecognizeCallback()

with open(infile, 'rb') as audio_file:
    audio_source = AudioSource(audio_file)
    speech_to_text.recognize_using_websocket(
        audio=audio_source,
        content_type='audio/wav',
        recognize_callback=myRecognizeCallback,
        model='en-US_NarrowbandModel',
        timestamps=True,
        interim_results=True,
        max_alternatives=0,
        profanity_filter=False)

