import glob
import os

filter = ['[noise]', '[vocalized-noise]', '[laughter]', '[silence]', '[noise]']
template_line = "SPEAKER {filename} 1 {onset} {duration} <NA> <NA> {speaker_name} <NA>"


def _write_to_file(predict_dir: str, filename: str, extension: str, textline: str):
    with open(os.path.join(predict_dir, "{file}.{ext}".format(file=filename, ext=extension)), "a") as myfile:
        myfile.write(textline + "\n")


class ProcessData:

    def __init__(self, dataset: str):
        self._dataset_path = os.path.join(os.getcwd().replace('/eval/tools', '/data'), dataset)
        print("_dataset_path: {}".format(self._dataset_path))

        self.annotated = os.path.join(self._dataset_path, 'annotated')
        print('annotated directory: {}'.format(self.annotated))
        if not os.path.exists(self.annotated):
            os.makedirs(self.annotated)

    def run(self):
        dirs = glob.glob(os.path.join(self._dataset_path, 'gold-transcriptions', '*/'))
        # print('sub_dir: {}'.format(dirs))

        for _dir in dirs:
            sub_dirs = glob.glob(os.path.join(_dir, '*/'))
            for sub_dir in sub_dirs:
                user_files = glob.glob(os.path.join(sub_dir, '*-a-trans.text'))
                user_files = sorted(user_files)
                # print('user_files: {}'.format(user_files))
                sample_file_name = os.path.basename(user_files[0])[:6]
                # print('sample_file_name: {}'.format(sample_file_name))
                self._combine_speakers(sample_file_name, user_files)

    def _combine_speakers(self, sample_file_name: str, transcript_files: list):
        user_data = {}
        for index, filename in zip(range(1, len(transcript_files) + 1), transcript_files):
            data = []
            with open(filename, 'rb') as data_file:
                for line in data_file.readlines():
                    items = line.decode("utf-8").split(' ')
                    start_time = float(items[1])
                    duration = float(items[2]) - start_time
                    filtered_utt = ' '.join([word for word in items[4:] if word not in filter])
                    if filtered_utt.strip():
                        # print('filtered utterance: {}'.format(filtered_utt))
                        data.append({"onset": start_time, "duration": duration})
                        # data[start_time] = template_line.format(filename=sample_file_name,
                        #                                         onset="{:.3f}".format(start_time),
                        #                                         duration="{:.3f}".format(duration),
                        #                                         speaker_name='PER-{}'.format(index))

            sorted_data = sorted(data, key=lambda k: k['onset'])
            # print('sorted_data: {}'.format(sorted_data))
            user_data[index] = {"fist_time": sorted_data[0]['onset'], "data": sorted_data}
        # print('user_data: {}'.format(user_data))

        # sort the user data based on the first time speaking, the user speaking first is the user one,
        # otherwise the user two
        sorted_user_data = sorted(list(user_data.values()), key=lambda k: k['fist_time'])

        self.formalise_data_structure(sample_file_name, sorted_user_data)

    def formalise_data_structure(self, sample_file_name: str, sorted_user_data: list):
        uttered_data = {}
        for index in range(1, len(sorted_user_data) + 1):
            _data = sorted_user_data[index - 1].get('data')
            for item in _data:
                uttered_data[item.get('onset')] = template_line.format(filename=sample_file_name,
                                                                       onset="{:.3f}".format(item.get('onset')),
                                                                       duration="{:.3f}".format(item.get('duration')),
                                                                       speaker_name='PER-{}'.format(index))
        print('uttered_data: {}'.format(uttered_data.keys()))
        sorted_uttered_data = dict(sorted(uttered_data.items()))
        print('uttered_data: {}'.format(sorted_uttered_data.keys()))
        _write_to_file(self.annotated, sample_file_name, 'rttm',
                       '\n'.join(list(sorted_uttered_data.values())))


if __name__ == '__main__':
    processor = ProcessData('SWB')
    processor.run()