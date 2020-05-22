source ../venv/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/google/cloud/credentials/creds.json"
for file in ../data/batch1/*.wav; do python transcribe-google.py $file; done
