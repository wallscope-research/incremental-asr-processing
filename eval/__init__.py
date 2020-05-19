import glob
import os
import threading

from ibm_watson.websocket import RecognizeCallback
from google_speech import GoogleCloud
from ibm_waston_speech import IBMCloud

ALL = 0
GOOGLE_CLOUD = 1
IBM_WATSON = 2
MICROSOFT_AZURE = 3

template_line = "SPEAKER {filename} 1 {onset} {duration} <NA> <NA> {speaker_name} <NA>"


class Eval(object):

    def __init__(self, dataset: str):
        self._dataset_path = os.path.join(os.getcwd().replace('/eval', '/data'), dataset)
        print("_dataset_path: {}".format(self._dataset_path))

        if os.path.exists(os.path.join(self._dataset_path, 'audios')):
            self.audio_samples = glob.glob(os.path.join(self._dataset_path, 'audios', '*.wav'))
            print("specif_user_samples: {}".format(self.audio_samples))

    def eval(self, asr_model: int):
        if asr_model == ALL:
            thread_google = GoogleThread(GOOGLE_CLOUD, self._dataset_path, self.audio_samples)
            thread_watson = WatsonThread(IBM_WATSON, self._dataset_path, self.audio_samples)
            thread_azure = AzureThread(MICROSOFT_AZURE, self._dataset_path, self.audio_samples)

            # Start new Threads
            thread_google.start()
            thread_watson.start()
            thread_azure.start()

            # Add into multi-thread pool
            thread_google.join()
            thread_watson.join()
            thread_azure.join()

        elif asr_model == GOOGLE_CLOUD:
            thread_google = GoogleThread(GOOGLE_CLOUD, self._dataset_path, self.audio_samples)
            # Start new Threads
            thread_google.start()

        elif asr_model == IBM_WATSON:
            thread_watson = WatsonThread(IBM_WATSON, self._dataset_path, self.audio_samples)
            # Start new Threads
            thread_watson.start()

        elif asr_model == MICROSOFT_AZURE:
            thread_azure = AzureThread(MICROSOFT_AZURE, self._dataset_path, self.audio_samples)
            # Start new Threads
            thread_azure.start()


class GoogleThread(threading.Thread):

    def __init__(self, thread_id: int, predict_dir: str, sample_files: list):
        super().__init__()
        self.thread_id = thread_id

        self.predict_dir = os.path.join(predict_dir, 'predicts', 'google')
        print('predict directory: {}'.format(self.predict_dir))
        if not os.path.exists(self.predict_dir):
            os.makedirs(self.predict_dir)

        self.sample_files = sample_files

        self._google_service = GoogleCloud()

    def run(self) -> None:
        print('starting thread {ID}'.format(ID=self.thread_id))

        sample_names = [os.path.basename(x) for x in self.sample_files]
        for sample_file, name in zip(self.sample_files, sample_names):
            response = self._google_service.listen(sample_file)
            print('response: {} \r\n'.format(response))
            response_line = template_line.format(filename=os.path.splitext(name)[0],
                                                 onset="<NA>",
                                                 duration="<NA>",
                                                 speaker_name="PER-{}".format('1'))
            write_to_file(self.predict_dir, os.path.splitext(name)[0], 'rttm', response_line)

    def process(self, response: dict):
        pass


class WatsonThread(threading.Thread):

    def __init__(self, thread_id: int, predict_dir: str, sample_files: list):
        super().__init__()
        self.thread_id = thread_id

        self.predict_dir = os.path.join(predict_dir, 'predicts', 'ibm')
        print('predict directory: {}'.format(self.predict_dir))
        if not os.path.exists(self.predict_dir):
            os.makedirs(self.predict_dir)

        self.sample_files = sample_files
        self._ibm_service = IBMCloud()

    def run(self) -> None:
        print('starting thread {ID}'.format(ID=self.thread_id))

        sample_names = [os.path.basename(x) for x in self.sample_files]
        for sample_file, name in zip(self.sample_files, sample_names):
            self._ibm_service.listen(sample_file,
                                     IBMRecognizeCallback(self.predict_dir,
                                                          os.path.splitext(name)[0]))


class AzureThread(threading.Thread):

    def __init__(self, thread_id: int, predict_dir: str, sample_files: list):
        super().__init__()
        self.thread_id = thread_id

        self.predict_dir = os.path.join(predict_dir, 'predicts', 'msoft')
        print('predict directory: {}'.format(self.predict_dir))
        if not os.path.exists(self.predict_dir):
            os.makedirs(self.predict_dir)

        self.sample_files = sample_files

    def run(self) -> None:
        print('starting thread {ID}'.format(ID=self.thread_id))

        sample_names = [os.path.basename(x) for x in self.sample_files]
        for sample_file, name in zip(self.sample_files, sample_names):
            # response = transcribe_google.transcribe_streaming(sample_file)
            response_line = template_line.format(filename=os.path.splitext(name)[0],
                                                 onset="<NA>",
                                                 duration="<NA>",
                                                 speaker_name="PER-{}".format('1'))
            write_to_file(self.predict_dir, os.path.splitext(name)[0], 'rttm', response_line)

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
                if result and result.get('final'):
                    print('get final results...')
                    speech_result = result['alternatives'][0]
                    GET_FINAL_REUSLT = True
            elif GET_FINAL_REUSLT and data.get('speaker_labels'):
                speaker_labels = data.get('speaker_labels')
                print('speaker_labels: {}'.format(speaker_labels))

            print('response: {} \r\n'.format(data))
            response_line = template_line.format(filename=self.filename,
                                                 onset="<NA>",
                                                 duration="<NA>",
                                                 speaker_name="PER-{}".format('1'))
            write_to_file(self.predict_dir, self.filename, 'rttm', response_line)

    def process(self, response: dict):
        pass

    
def write_to_file(predict_dir: str, filename: str, extension: str, textline: str):
    with open(os.path.join(predict_dir, "{file}.{ext}".format(file=filename, ext=extension)), "a") as myfile:
        myfile.write(textline + "\n")


if __name__ == '__main__':
    evaluator = Eval('avdiar')
    evaluator.eval(GOOGLE_CLOUD)
