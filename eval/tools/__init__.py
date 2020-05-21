import glob
import os


def _write_to_file(filename: str, textline: str):
    with open(filename, "w") as myfile:
        myfile.write(textline + "\n")


class ProcessData:

    def __init__(self, dataset: str):
        self._dataset_path = os.path.join(os.getcwd().replace('/eval/tools', '/data'), dataset)
        print("_dataset_path: {}".format(self._dataset_path))

        if os.path.exists(os.path.join(self._dataset_path, 'annotated')):
            self.sample_files = glob.glob(os.path.join(self._dataset_path, 'annotated', '*.rttm'))
            print("specif_user_samples: {}".format(self.sample_files))

    def run(self):
        for sample_file in self.sample_files:
            print('processing file {}...'.format(os.path.basename(sample_file)))
            with open(sample_file, 'rb') as file:
                data_dict = {}
                for line in file:
                    text = line.decode("utf-8")
                    items = text.split(' ')
                    print('key is {}'.format(items[3]))
                    data_dict[float(items[3])] = text

                sorted_data_dict = dict(sorted(data_dict.items()))
                _write_to_file(sample_file, ''.join(list(sorted_data_dict.values())))


if __name__ == '__main__':
    processor = ProcessData('avdiar')
    processor.run()