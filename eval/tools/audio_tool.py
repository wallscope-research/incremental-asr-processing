import glob
import os

from pydub import AudioSegment


class AudioTool(object):

    def __init__(self, dataset: str):
        self._dataset_path = os.path.join(os.getcwd().replace('/eval/tools', '/data'), dataset)
        print("_dataset_path: {}".format(self._dataset_path))

        if os.path.exists(os.path.join(self._dataset_path, 'audios_copy')):
            self.audio_samples = glob.glob(os.path.join(self._dataset_path, 'audios_copy', '*.wav'))
            print("specif_user_samples: {}".format(self.audio_samples))

    def run(self):
        sample_names = [os.path.basename(x) for x in self.audio_samples]
        for sample_file, name in zip(self.audio_samples, sample_names):
            song = AudioSegment.from_wav(sample_file)
            song = song * 2
            # save the output
            _path_dir = os.path.join(self._dataset_path, 'audios')
            if not os.path.exists(_path_dir):
                os.makedirs(_path_dir)

            _path = os.path.join(_path_dir, name)
            song.export(_path, "wav")


if __name__ == '__main__':
    tool = AudioTool('avdiar')
    tool.run()


