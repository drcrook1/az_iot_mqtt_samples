docker stop mqttleaf
docker rm mqttleaf
docker build -t mqttleaf .
docker run -p 8883:8883 --name mqttleaf --env-file ./dev.env mqttleaf