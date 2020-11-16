# Google Instructions

Our implementation of incremental transcription using Google's ASR is found in `transcribe-google.py` but we have set up a run script to get you started quickly. The `run.sh` script needs two small edits before it will work. Firstly, the path to your Google Cloud Credentials is required to replace `/path/to/google/cloud/credentials/creds.json`. Secondly, you need to replace `../data/batch1/` with the path to your batch of audio files (`*.wav` files) to process. To note, `../data/batch1/` already exists and ready to use.

If you have setup the virtual environment in the directory above, you should be able to run the following:

1. Edit `run.sh` by adding correct the path to your cloud credentials.
2. Edit `run.sh` if moving on to batch2 or data batch structure has changed.
3. Run `run.sh`