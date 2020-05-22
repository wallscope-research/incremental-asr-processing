source ../venv/bin/activate
for file in ../data/batch1/*.wav; do python transcribe-watson.py $file; done
