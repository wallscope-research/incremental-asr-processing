import glob
import json
import os
import threading

from google.api_core.exceptions import OutOfRange
from ibm_watson.websocket import RecognizeCallback
from google_speech import GoogleCloud
from ibm_waston_speech import IBMCloud
from deep_service import DeepAffectsCloud

GOOGLE_CLOUD = 1
IBM_WATSON = 2
DEEP_AFFECTS = 3

template_line = "SPEAKER {filename} 1 {onset} {duration} <NA> <NA> {speaker_name} <NA>"

GET_FINAL_REUSLT = False
speaker_diar = []
speech_result = {}


class Eval(object):

    def __init__(self, dataset: str):
        self._dataset_path = os.path.join(os.getcwd().replace('/eval', '/data'), dataset)
        print("_dataset_path: {}".format(self._dataset_path))

        if os.path.exists(os.path.join(self._dataset_path, 'audios')):
            self.audio_samples = glob.glob(os.path.join(self._dataset_path, 'audios', '*.wav'))
            print("specif_user_samples: {}".format(self.audio_samples))

    def eval(self, asr_model: int):
        if asr_model == GOOGLE_CLOUD:
            thread_google = GoogleThread(GOOGLE_CLOUD, self._dataset_path, self.audio_samples)
            # Start new Threads
            thread_google.start()

        elif asr_model == IBM_WATSON:
            thread_watson = WatsonThread(IBM_WATSON, self._dataset_path, self.audio_samples)
            # Start new Threads
            thread_watson.start()

        elif asr_model == DEEP_AFFECTS:
            thread_affects = DeepAffectsThread(DEEP_AFFECTS, self._dataset_path, self.audio_samples)
            # Start new Threads
            thread_affects.start()


class GoogleThread(threading.Thread):

    def __init__(self, thread_id: int, predict_dir: str, sample_files: list):
        super().__init__()
        self.thread_id = thread_id

        self.predict_dir = os.path.join(predict_dir, 'predicts', 'google')
        print('predict directory: {}'.format(self.predict_dir))
        if not os.path.exists(self.predict_dir):
            os.makedirs(self.predict_dir)
        print('is predict file existing? {}'.format(not os.path.exists(self.predict_dir)))

        self.completed_predict_dir = os.path.join(predict_dir, 'predicts', 'ibm')
        if os.path.exists(self.completed_predict_dir):
            print('sample_files: {}'.format(sample_files))
            print('BEFORE reduction: {}'.format(len(sample_files)))
            processed_files = [os.path.splitext(os.path.basename(x))[0] for x in
                               glob.glob(os.path.join(self.completed_predict_dir, '*-mono.rttm'))]
            print('processed_files: {}'.format(processed_files))
            self.sample_files = [x for x in sample_files if
                                 os.path.splitext(os.path.basename(x))[0] in processed_files]


            old_processed_files = [os.path.splitext(os.path.basename(x))[0] for x in
                                   glob.glob(os.path.join(self.predict_dir, '*-mono.rttm'))]
            self.sample_files = [x for x in sample_files if
                                 os.path.splitext(os.path.basename(x))[0] not in old_processed_files and
                                 os.path.splitext(os.path.basename(x))[0] in processed_files]

            print('AFTER reduction: {}'.format(len(self.sample_files)))
            print('self.sample_files: {}'.format(self.sample_files))
        else:
            self.sample_files = sample_files

        self._google_service = GoogleCloud()

    def run(self) -> None:
        print('starting thread {ID}'.format(ID=self.thread_id))

        sample_names = [os.path.basename(x) for x in self.sample_files]
        for index, sample_file, name in zip(range(1, len(sample_names)), self.sample_files, sample_names):
            print('run the process with the {}-th file: {}'.format(index, name))

            try:
                _responses = self._google_service.transcribe_streaming(sample_file)
                end_timestamp = 0
                speaker_diar_results = {}
                for res in _responses:
                    if not res.results:
                        continue
                    for result in res.results:
                        if result.is_final:
                            # First alternative has words tagged with speakers
                            alternative = result.alternatives[0]

                            results, end_timestamp = self._process(os.path.splitext(name)[0],
                                                                   alternative.words,
                                                                   end_timestamp)
                            # print('speaker_diar_results: {}'.format(speaker_diar_results))
                            # print('results: {}'.format(results))
                            speaker_diar_results = {**speaker_diar_results, **results}

                sorted_speaker_results = dict(sorted(speaker_diar_results.items()))
                write_to_file(self.predict_dir, os.path.splitext(name)[0], 'rttm',
                              '\n'.join(list(sorted_speaker_results.values())))

            except OutOfRange as e:
                print('Error: {}'.format(e.message))

    def _process(self, _filename: str, words, last_end_time: float):
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
                    # print('add speaker into the dict: {}'.format(speaker_diar_dict))

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

            # print('add speaker into the dict: {}'.format(speaker_diar_dict))

        return dict(sorted(speaker_diar_dict.items())), final_end_timestamp


class WatsonThread(threading.Thread):

    def __init__(self, thread_id: int, predict_dir: str, sample_files: list):
        super().__init__()
        self.thread_id = thread_id
        self.predict_dir = os.path.join(predict_dir, 'predicts', 'ibm')
        print('predict directory: {}'.format(self.predict_dir))

        if os.path.exists(self.predict_dir):
            print('sample_files: {}'.format(sample_files))
            print('BEFORE reduction: {}'.format(len(sample_files)))
            processed_files = [os.path.splitext(os.path.basename(x))[0] for x in glob.glob(os.path.join(self.predict_dir, '*-mono.rttm'))]
            print('processed_files: {}'.format(processed_files))
            processed_files.append('sw02729-mono')
            processed_files.append('sw04619-mono')
            self.sample_files = [x for x in sample_files if os.path.splitext(os.path.basename(x))[0] not in processed_files]
            print('AFTER reduction: {}'.format(len(self.sample_files)))
        else:
            self.sample_files = sample_files
            os.makedirs(self.predict_dir)

        self._ibm_service = IBMCloud()

    def run(self) -> None:
        print('starting thread {ID}'.format(ID=self.thread_id))

        global speaker_diar
        sample_names = [os.path.basename(x) for x in self.sample_files]
        last_file = ""
        for index, sample_file, name in zip(range(1, len(sample_names)), self.sample_files, sample_names):
            if speaker_diar and last_file:
                speaker_diar_dict = self._process(os.path.splitext(last_file)[0], speaker_diar)
                write_to_file(self.predict_dir, os.path.splitext(last_file)[0], 'rttm',
                              '\n'.join(list(speaker_diar_dict.values())))
                speaker_diar.clear()
            print('run the process with the {}-th file: {}'.format(index, name))
            last_file = name

            self._ibm_service.listen(sample_file,
                                     IBMRecognizeCallback(self.predict_dir,
                                                          os.path.splitext(name)[0]))
        if speaker_diar:
            speaker_diar_dict = self._process(os.path.splitext(last_file)[0], speaker_diar)
            write_to_file(self.predict_dir, os.path.splitext(last_file)[0], 'rttm',
                          '\n'.join(list(speaker_diar_dict.values())))
            speaker_diar.clear()

    def _process(self, _filename: str, diar_results: list):
        speaker_diar_dict = {}
        prev_time_stamp = {}
        prev_speaker = ""
        for item in diar_results:
            print('item: {}'.format(item))

            if prev_speaker == item.get('speaker') + 1:
                print('prev_speaker: {}'.format(prev_speaker))
                prev_time_stamp['to'] = item.get('to')
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

                prev_time_stamp = {'from': item.get('from'), 'to': item.get('to')}
                prev_speaker = item.get('speaker') + 1

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

        return dict(sorted(speaker_diar_dict.items()))


class DeepAffectsThread(threading.Thread):

    def __init__(self, thread_id: int, predict_dir: str, sample_files: list):
        super().__init__()
        self.thread_id = thread_id

        self.predict_dir = os.path.join(predict_dir, 'predicts', 'deep_affects')
        print('predict directory: {}'.format(self.predict_dir))
        if not os.path.exists(self.predict_dir):
            os.makedirs(self.predict_dir)

        self.sample_files = sample_files

        self._deep_service = DeepAffectsCloud()

    def run(self) -> None:
        print('starting thread {ID}'.format(ID=self.thread_id))

        sample_names = [os.path.basename(x) for x in self.sample_files]
        for index, sample_file, name in zip(range(1, len(sample_names)), self.sample_files, sample_names):
            global speaker_diar
            speaker_diar.clear()
            print('run the process with the {}-th file: {}'.format(index, name))

            responses = self._deep_service.listen(sample_file)
            for response in responses:
                if not response.results:
                    continue
                for result in response.results:
                    if result.is_final:
                        # First alternative has words tagged with speakers
                        alternative = result.alternatives[0]

                        for word in alternative.words:
                            print(u"Word: {}".format(word))
                            write_to_file(self.predict_dir, os.path.splitext(name)[0], 'txt', word)

    def process(self, response: dict):
        pass


class IBMRecognizeCallback(RecognizeCallback):
    """
    define callback for the speech to text service
    """

    def __init__(self, predict_dir: str, filename: str):
        RecognizeCallback.__init__(self)
        self.predict_dir = predict_dir
        self.filename = filename

    def on_data(self, data):
        global GET_FINAL_REUSLT, speech_result
        if data:
            if data.get('results'):
                result = data.get('results')[0]
                # print('result: {}'.format(result))
                if result and result.get('final'):
                    speech_result = result['alternatives'][0]
                    print('speech_result: {}'.format(speech_result))
                    GET_FINAL_REUSLT = True
            elif GET_FINAL_REUSLT and data.get('speaker_labels'):
                speaker_labels = data.get('speaker_labels')
                print('speaker_labels: {}'.format(speaker_labels))
                words = speech_result.get('timestamps')
                start_times = [word[1] for word in words]
                print('start_times: {}'.format(start_times))
                labels = [item for item in speaker_labels if item['from'] in start_times]
                print('speaker_labels: {}'.format(labels))
                result = {"start_time": words[0][1], "speaker_labels": speaker_labels}
                speaker_diar.extend(labels)
                GET_FINAL_REUSLT = False


def write_to_file(predict_dir: str, filename: str, extension: str, textline: str):
    with open(os.path.join(predict_dir, "{file}.{ext}".format(file=filename, ext=extension)), "a") as myfile:
        myfile.write(textline + "\n")


def process(_filename: str, diar_results: list):
    speaker_diar_dict = {}
    prev_time_stamp = {}
    prev_speaker = ""
    for item in diar_results:
        print('item: {}'.format(item))

        if prev_speaker == item.get('speaker') + 1:
            print('prev_speaker: {}'.format(prev_speaker))
            prev_time_stamp['to'] = item.get('to')
        else:
            if prev_speaker and prev_time_stamp:
                speaker_diar_dict[prev_time_stamp.get('from')] = template_line.format(filename=_filename,
                                                                                      onset="{:.3f}".format(
                                                                                          prev_time_stamp.get('from')),
                                                                                      duration="{:.3f}".format(
                                                                                          prev_time_stamp.get('to')
                                                                                          - prev_time_stamp
                                                                                          .get('from')),
                                                                                      speaker_name='PER-{}'.format(
                                                                                          prev_speaker))
                print('add speaker into the dict: {}'.format(speaker_diar_dict))

            prev_time_stamp = {'from': item.get('from'), 'to': item.get('to')}
            prev_speaker = item.get('speaker') + 1

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

    return dict(sorted(speaker_diar_dict.items()))


if __name__ == '__main__':
    evaluator = Eval('avdiar')
    # evaluator.eval(IBM_WATSON)
    evaluator.eval(GOOGLE_CLOUD)
