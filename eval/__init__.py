import glob
import os
import threading

from asr_google import transcribe_google
# from asr_ibm import transcribe_watson
# from asr_msoft import transcribe_azure

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
        if os.path.exists(self.predict_dir):
            os.makedirs(self.predict_dir)

        self.sample_files = sample_files

    def run(self) -> None:
        print('starting thread {ID}'.format(ID=self.thread_id))

        sample_names = [os.path.basename(x) for x in self.sample_files]
        for sample_file, name in zip(self.sample_files, sample_names):
            # response = transcribe_google.transcribe_streaming(sample_file)
            print('sample_file: {} \r\n'.format(sample_file))


class WatsonThread(threading.Thread):

    def __init__(self, thread_id: int, predict_dir: str, sample_files: list):
        super().__init__()
        self.thread_id = thread_id

        self.predict_dir = os.path.join(predict_dir, 'predicts', 'ibm')
        print('predict directory: {}'.format(self.predict_dir))
        if os.path.exists(self.predict_dir):
            os.makedirs(self.predict_dir)

        self.sample_files = sample_files

    def run(self) -> None:
        print('starting thread {ID}'.format(ID=self.thread_id))

        sample_names = [os.path.basename(x) for x in self.sample_files]
        for sample_file, name in zip(self.sample_files, sample_names):
            response = transcribe_google.transcribe_streaming(sample_file)


class AzureThread(threading.Thread):

    def __init__(self, thread_id: int, predict_dir: str, sample_files: list):
        super().__init__()
        self.thread_id = thread_id

        self.predict_dir = os.path.join(predict_dir, 'predicts', 'msoft')
        print('predict directory: {}'.format(self.predict_dir))
        if os.path.exists(self.predict_dir):
            os.makedirs(self.predict_dir)

        self.sample_files = sample_files

    def run(self) -> None:
        print('starting thread {ID}'.format(ID=self.thread_id))

        sample_names = [os.path.basename(x) for x in self.sample_files]
        for sample_file, name in zip(self.sample_files, sample_names):
            response = transcribe_google.transcribe_streaming(sample_file)


def write_to_file(predict_dir: str, filename: str, extension: str, textline: str):
    with open(os.path.join(predict_dir, "{file}.{ext}".format(file=filename, ext=extension)), "a") as myfile:
        myfile.write(textline)


if __name__ == '__main__':
    evaluator = Eval('avdiar')
    evaluator.eval(GOOGLE_CLOUD)
