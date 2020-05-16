#!/usr/bin/env python

import sys
import re


# [START speech_transcribe_streaming]
def transcribe_streaming(stream_file, result_file):
    """Streams transcription of the given audio file."""
    import io
    import wave
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    # [START speech_python_migration_streaming_request]
    with io.open(stream_file, 'rb') as audio_file:
        content = audio_file.read()

    stream = [content]

    requests = (types.StreamingRecognizeRequest(audio_content=chunk)
                for chunk in stream)

    model = "phone_call"
    use_enhanced = False
    enable_word_time_offsets = True
    interim = True
    language_code = "en-US"

    wf = wave.open(stream_file, mode="rb")
    
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=wf.getframerate(),
        model=model,
        use_enhanced=use_enhanced,
        enable_word_time_offsets=enable_word_time_offsets,
        language_code=language_code,
        audio_channel_count=wf.getnchannels()
    )

    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=interim
    )

    # streaming_recognize returns a generator.
    # [START speech_python_migration_streaming_response]
    responses = client.streaming_recognize(streaming_config, requests)
    # [END speech_python_migration_streaming_request]

    for response in responses:
        # Once the transcription has settled, the first result will contain the
        # is_final result. The other results will be for subsequent portions of
        # the audio.
        result = response.results[0]
        store('Finished: {}'.format(result.is_final), result_file)
        store('Stability: {}'.format(result.stability), result_file)
        store('Time: {}'.format(result.result_end_time.seconds + result.result_end_time.nanos*1e-9), result_file)
        alternative = result.alternatives[0]
        # The alternatives are ordered from most likely to least.
        # for alternative in alternatives:
        store(u'Transcript: {}'.format(alternative.transcript), result_file)
    # [END speech_python_migration_streaming_response]
# [END speech_transcribe_streaming]


def store(data, outfile_name):
    with open(outfile_name, 'a') as of:
        print(data, file=of)



if __name__ == '__main__':
    infile = sys.argv[1]
    filename_prep = re.search(r"(?<=data\/)(.*?)(?=\.wav)", infile).group(0)
    outfile = "./results/" + filename_prep + ".txt"
    
    with open(outfile, 'w') as of:
        print(filename_prep, file=of)

    transcribe_streaming(infile, outfile)
