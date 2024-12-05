docker stop python_tts_test
docker rm python_tts_test

docker build -t python_tts_test .
docker run --name python_tts_test -p 2024:2020 \
-d python_tts_test


