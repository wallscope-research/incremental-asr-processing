# IBM Watson Instructions

Our implementation of incremental transcription using IBM's ASR is found in `transcribe-watson.py` but we have set up a run script to get you started quickly. The `run.sh` script may need a small edit before it will work. If you are not using `../data/batch1/` (that already exists) to store your audio files, you will need to replace `../data/batch1/` with the path to your batch of audio files (`*.wav` files) to process.

For authentication, please fill lines 18 and 23 of the `transcribe-watson.py` script with your API 'key' and 'url' from IBM.

If you have setup the virtual environment in the directory above, you should be able to run the following:

1. Edit `transcribe-watson.py` to include your API key and API URL.
2. Edit `run.sh` if you have a different path to your data.
3. Run `run.sh`.
