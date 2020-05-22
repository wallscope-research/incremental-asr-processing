docker rm $(docker ps -a -q)
docker build -t asr/msoft .
docker run --name azure -v /path/to/incremental-asr-evaluation/data/batch1/:/data -v /path/to/incremental-asr-evaluation/asr-msoft/results/batch1/:/results asr/msoft
