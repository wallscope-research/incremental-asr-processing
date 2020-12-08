# Incremental ASR Processing

This repository allows you to process speech audio, transcribing it incrementally. This was originally created for a [paper published at COLING 2020](https://www.aclweb.org/anthology/2020.coling-main.312.pdf). You can evaluate incremental ASR systems (using the transcriptions generated in this repository) with our [Incremental ASR Evaluation repository](https://github.com/wallscope-research/incremental-asr-evaluation).

This paper (by [Angus Addlesee](http://addlesee.co.uk/), [Yanchao Yu](https://www.researchgate.net/profile/Yanchao_Yu), and [Arash Eshghi](https://sites.google.com/site/araesh81/)) can be found [here](https://www.aclweb.org/anthology/2020.coling-main.312.pdf) and is titled: "A Comprehensive Evaluation of Incremental Speech Recognition and Diarization for Conversational AI".

If you use this repository in your work - please cite us:

Harvard:
```
Addlesee, A., Yu, Y. and Eshghi, A., 2020. A Comprehensive Evaluation of Incremental Speech Recognition and Diarization for Conversational AI. COLING 2020.
```

BibTeX:
```
@inproceedings{addlesee2020evaluation,
  title={A Comprehensive Evaluation of Incremental Speech Recognition and Diarization for Conversational AI},
  author={Addlesee, Angus and Yu, Yanchao and Eshghi, Arash},
  journal={COLING 2020},
  year={2020}
}
```

## Installation

We have created a setup script to prepare your system to process speech with the incremental speech recognition services from [Microsoft](https://azure.microsoft.com/en-gb/services/cognitive-services/speech-to-text/), [IBM](https://www.ibm.com/uk-en/cloud/watson-speech-to-text), and [Google](https://cloud.google.com/speech-to-text). This script will create a virtual Python environment, and install the required packages within it. You can clone this repository and run the setup with the following commands:

1. Run `git clone https://github.com/wallscope-research/incremental-asr-processing.git`
2. Run `cd incremental-asr-processing`
3. Run `./setup.sh`

You need to be within this virtual environment to run any processing. To enter and exit this environment, please use the relevant line:

- To enter the virtual environment, run `source venv/bin/activate`
- To exit the virtual environment, run `deactivate`

Note - you only need to run the setup script once, but it must have been run to use the above two commands.

## Processing Audio with a System

Within the repository, we have implemented three systems, the three that we evaluated in our COLING 2020 paper - Microsof, IBM, and Google. These can be found in the `asr-msoft`, `asr-ibm`, and `asr-google` directories respectively. Within these directories, you can find the system specific instructions.

### Where to Keep Audio

You should store the audio files that you would like to be transcribed in the `data` directory. We recommend you split these into batches if you are processing a large number of files. For example, we have added `./data/batch1`. With this structure, you can use each incremental ASR system to process your audio files in these batches - allowing you to rerun a single batch if something goes wrong.

## Switchboard Corpus

We use the [Switchboard Corpus](https://catalog.ldc.upenn.edu/LDC97S62) to evaluate incremental ASR systems - if you would like to recreate the experiments in our COLING 2020 paper, you can find the information in the `switchboard` directory. Within you will find our script to 'clean' disfluencies in the gold transcriptions, and find the script to format Switchboard with its timings into the several required formats.

## Acknowledgements

[Angus Addlesee](http://addlesee.co.uk/) is funded by [Wallscope](https://wallscope.co.uk/) and [The Data Lab](https://www.thedatalab.com/). [Yanchao Yu](https://www.researchgate.net/profile/Yanchao_Yu) is funded by the Horizon2020 [SPRING Project](https://spring-h2020.eu/). We thank them for their support.