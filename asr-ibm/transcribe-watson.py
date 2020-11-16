import json
import sys
import re
from os.path import join, dirname
from ibm_watson import SpeechToTextV1
from ibm_watson.websocket import RecognizeCallback, AudioSource
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Python script takes a path to a .wav audio file.
infile = sys.argv[1]
# The results are stored in 'outfile' - which is named based on the 'infile'.
filename_prep = re.search(r"(?<=data\/)(.*?)(?=\.wav)", infile).group(0)
outfile = "./results/" + filename_prep + ".txt"
with open(outfile, 'w') as of:
        print(filename_prep, file=of)

# IBM authentication - please add your key on the line below.
authenticator = IAMAuthenticator('your key')    ## Add your key
speech_to_text = SpeechToTextV1(
    authenticator=authenticator
)
# IBM authentication - please add your url on the line below.
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
        # Using 'audio/wav' as Switchboard contains .wav files.
        content_type='audio/wav',
        recognize_callback=myRecognizeCallback,
        # Using "en-US" for Switchboard.
        model='en-US_NarrowbandModel',
        # Return word timings!
        timestamps=True,
        # Return results incrementally!
        interim_results=True,
        # This setting only returns the top incremental result.
        # i.e. The one that the system believes is most likely.
        max_alternatives=0,
        profanity_filter=False)

