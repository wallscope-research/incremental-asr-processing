#!/usr/bin/env python
import sys
import re

# Streams transcription of the given audio file.
def transcribe_streaming(stream_file, result_file):
    import io
    import wave
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    with io.open(stream_file, 'rb') as audio_file:
        content = audio_file.read()

    stream = [content]

    requests = (types.StreamingRecognizeRequest(audio_content=chunk)
                for chunk in stream)

    # Using Google's "phone_call" model as Switchboard consists of dyadic phone calls.
    model = "phone_call"
    use_enhanced = False
    # Return word timings!
    enable_word_time_offsets = True
    # Return results incrementally!
    interim = True
    # Using "en-US" for Switchboard.
    language_code = "en-US"

    wf = wave.open(stream_file, mode="rb")
    
    # Setup config for audio files. Often using wf here to get the audio file's properties.
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=wf.getframerate(),
        model=model,
        use_enhanced=use_enhanced,
        enable_word_time_offsets=enable_word_time_offsets,
        language_code=language_code,
        audio_channel_count=wf.getnchannels()
    )

    # Setting up streaming config - activating incrementality here.
    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=interim
    )

    # streaming_recognize returns a generator.
    responses = client.streaming_recognize(streaming_config, requests)

    for response in responses:
        # Once the transcription has settled, the first result will contain the
        # is_final result. The other results will be for subsequent portions of
        # the audio.
        result = response.results[0]
        store('Finished: {}'.format(result.is_final), result_file)
        store('Stability: {}'.format(result.stability), result_file)
        store('Time: {}'.format(result.result_end_time.seconds + result.result_end_time.nanos*1e-9), result_file)
        # The alternatives are ordered from most likely to least.
        alternative = result.alternatives[0]
        # Storing results for later processing.
        store(u'Transcript: {}'.format(alternative.transcript), result_file)


def store(data, outfile_name):
    with open(outfile_name, 'a') as of:
        print(data, file=of)


if __name__ == '__main__':
    # Python script takes a path to a .wav audio file.
    infile = sys.argv[1]
    # The results are stored in 'outfile' - which is named based on the 'infile'.
    filename_prep = re.search(r"(?<=data\/)(.*?)(?=\.wav)", infile).group(0)
    outfile = "./results/" + filename_prep + ".txt"
    
    with open(outfile, 'w') as of:
        print(filename_prep, file=of)

    transcribe_streaming(infile, outfile)
