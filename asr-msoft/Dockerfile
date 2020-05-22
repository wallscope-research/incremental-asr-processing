FROM python:3.7-stretch

WORKDIR /

COPY ./transcribe-azure.py /

RUN apt-get update && apt-get install -y \
    libssl1.0.2 \
    libasound2 \
    zsh

RUN pip install --upgrade pip && \
    pip install --upgrade azure-cognitiveservices-speech

CMD ["/bin/zsh", "-c", "for file in /data/*.wav; do python asr-m.py $file; done"]
