import azure.cognitiveservices.speech as speechsdk
import sys
import re
import io


def transcribe_streaming(stream_file, result_file):
    """Streams transcription of the given audio file."""
    import time
    
    speech_key, service_region = "your key", "uksouth"      ## Add your key 
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.request_word_level_timestamps()

    audio_input = speechsdk.AudioConfig(filename=stream_file)

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_input)

    done = False

    def stop_cb(evt):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        store('CLOSING on {}'.format(evt), result_file)
        nonlocal done
        done = True

    speech_recognizer.recognizing.connect(lambda evt: store('RECOGNIZING: {}'.format(evt.result.json), result_file))
    speech_recognizer.recognized.connect(lambda evt: store('JSON: {}'.format(evt.result.json), result_file))
    speech_recognizer.session_started.connect(lambda evt: store('SESSION STARTED: {}'.format(evt), result_file))
    speech_recognizer.session_stopped.connect(lambda evt: store('SESSION STOPPED {}'.format(evt), result_file))
    speech_recognizer.canceled.connect(lambda evt: store('CANCELED {}'.format(evt), result_file))
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start continuous speech recognition
    speech_recognizer.start_continuous_recognition()
    while not done:
        time.sleep(.05)

    speech_recognizer.stop_continuous_recognition()


def store(data, outfile_name):
    with open(outfile_name, 'a') as of:
        print(data, file=of)


if __name__ == '__main__':
    infile = sys.argv[1]
    print("NOTICE I:   " + infile)
    filename_prep = re.search(r"(?<=data\/)(.*?)(?=\.wav)", infile).group(0)
    outfile = "/results/" + filename_prep + ".txt"
    
    with open(outfile, 'w') as of:
        print(filename_prep, file=of)

    transcribe_streaming(infile, outfile)