Run cmds

docker build --platform linux/amd64 -t challenge1a:mogus .
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none challenge1a:mogus