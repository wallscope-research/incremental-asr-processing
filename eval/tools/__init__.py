import os


class ProcessData:

    def __init__(self, dataset: str):
        self._dataset_path = os.path.join(os.getcwd().replace('/eval', '/data'), dataset)
        print("_dataset_path: {}".format(self._dataset_path))

        if os.path.exists(os.path.join(self._dataset_path, 'audios')):
            self.audio_samples = glob.glob(os.path.join(self._dataset_path, 'audios', '*.wav'))
            print("specif_user_samples: {}".format(self.audio_samples))