# Microsoft Azure Instructions

Our implementation of incremental transcription using Microsoft's ASR is found in `transcribe-azure.py` but we have set up a run script to get you started quickly. The `run.sh` script may need a cuple of small edits before it will work. You will need to replace `/path/to/incremental-asr-evaluation/data/batch1/` with the path to your batch of audio files (`*.wav` files) to process. Similarly, you will need to change `/path/to/incremental-asr-evaluation/asr-msoft/results/batch1/` to tell the system where you want to store this batch pf results.

For authentication, please fill line 11 of `transcribe-azure.py` with your API 'key' from Microsoft.

You will need Docker installed to run our implementation of Microsoft's incremental ASR. This was done as `azure.cognitiveservices.speech` only worked with Python 3.7 at the time, whereas our system was running Python 3.8 to run the other two systems.

To begin, do the following:

1. Edit `transcribe-azure.py' to include your credentials (key and url).
2. Edit `run.sh` by modifying volume paths to your data and results.
3. Run `run.sh`.