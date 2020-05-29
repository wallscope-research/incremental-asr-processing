from __future__ import division

import io
import os
import wave

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

import yaml
from google.cloud import speech
from google.cloud.speech import types
from google.cloud.speech import enums
from google.oauth2 import service_account


class GoogleCloud:

    def __init__(self):
        data_path = os.path.join(os.getcwd().replace('/eval', '/data').replace('/asr_google', '/data'), 'config')
        _google_cloud_speech_credentials = os.path.join(data_path, 'google_credentials.json')
        credentials = service_account.Credentials.from_service_account_file(_google_cloud_speech_credentials)

        with open(os.path.join(data_path, 'google_config.yaml')) as config_yaml:
            self._google_config = yaml.load(config_yaml, Loader=yaml.FullLoader)
        self._google_config['config']['encoding'] = enums.RecognitionConfig.AudioEncoding.FLAC
        self._client = speech.SpeechClient(credentials=credentials)

    def transcribe_streaming(self, stream_file: str):
        """Streams transcription of the given audio file."""

        # [START speech_python_migration_streaming_request]
        with io.open(stream_file, 'rb') as audio_file:
            content = audio_file.read()

        stream = [content]

        requests = (types.StreamingRecognizeRequest(audio_content=chunk)
                    for chunk in stream)

        wf = wave.open(stream_file, mode="rb")

        diarization_config = types.SpeakerDiarizationConfig(
            enable_speaker_diarization=self._google_config.get('config').get('diarization_config').get('enable_speaker_diarization'),
            max_speaker_count=self._google_config.get('config').get('diarization_config').get('max_speaker_count'),
            min_speaker_count=self._google_config.get('config').get('diarization_config').get('min_speaker_count')
        )

        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=wf.getframerate(),
            model=self._google_config.get('config').get('model'),
            use_enhanced=self._google_config.get('config').get('use_enhanced'),
            enable_word_time_offsets=self._google_config.get('config').get('enable_word_time_offsets'),
            language_code=self._google_config.get('config').get('language_code'),
            diarization_config=diarization_config,
            audio_channel_count=wf.getnchannels()
        )

        streaming_config = types.StreamingRecognitionConfig(
            config=config,
            interim_results=self._google_config.get('interim_results')
        )

        responses = self._client.streaming_recognize(streaming_config, requests)
        return responses


template_line = "SPEAKER {filename} 1 {onset} {duration} <NA> <NA> {speaker_name} <NA>"


def _process(_filename: str, words, last_end_time: float):
    speaker_diar_dict = {}
    prev_time_stamp = {}
    prev_speaker = ""
    final_end_timestamp = 0

    for word_info in words:
        start_time = word_info.start_time.seconds + word_info.start_time.nanos * 1e-9 if word_info.start_time else 0
        end_time = word_info.end_time.seconds + word_info.end_time.nanos * 1e-9
        final_end_timestamp = end_time

        if start_time < last_end_time:
            continue

        if prev_speaker == word_info.speaker_tag:
            # print('prev_speaker: {}'.format(prev_speaker))
            prev_time_stamp['to'] = end_time
        else:
            if prev_speaker and prev_time_stamp:
                speaker_diar_dict[prev_time_stamp.get('from')] = template_line.format(filename=_filename,
                                                                                      onset="{:.3f}".format(
                                                                                          prev_time_stamp.get(
                                                                                              'from')),
                                                                                      duration="{:.3f}".format(
                                                                                          prev_time_stamp.get('to')
                                                                                          - prev_time_stamp
                                                                                          .get('from')),
                                                                                      speaker_name='PER-{}'.format(
                                                                                          prev_speaker))
                print('add speaker into the dict: {}'.format(speaker_diar_dict))

            prev_time_stamp = {'from': start_time, 'to': end_time}
            prev_speaker = word_info.speaker_tag

    if prev_speaker and prev_time_stamp:
        speaker_diar_dict[prev_time_stamp.get('from')] = template_line.format(filename=_filename,
                                                                              onset="{:.3f}".format(prev_time_stamp
                                                                                                    .get('from')),
                                                                              duration="{:.3f}".format(
                                                                                  prev_time_stamp.get(
                                                                                      'to') - prev_time_stamp.get(
                                                                                      'from')),
                                                                              speaker_name='PER-{}'.format(
                                                                                  prev_speaker))

        print('add speaker into the dict: {}'.format(speaker_diar_dict))

    return dict(sorted(speaker_diar_dict.items())), final_end_timestamp


if __name__ == '__main__':
    google_recogniser = GoogleCloud()
    _responses = google_recogniser.transcribe_streaming('/Users/yy165/Yanchao_Yu/Job/HW/SPRING/Code/incremental-asr-evaluation/data/SWB/audios/sw02657-mono.wav')

    end_timestamp = 0
    for res in _responses:
        if not res.results:
            continue
        for result in res.results:
            if result.is_final:
                # First alternative has words tagged with speakers
                alternative = result.alternatives[0]

                words = alternative.words
                print('------------- words: {} ------------- '.format(words))

                results, end_timestamp = _process('sw02657-mono', alternative.words, end_timestamp)
                print('results: {}'.format(results))

