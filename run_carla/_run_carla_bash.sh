#!/usr/bin/env bash

VERSION=$1

xhost local:root

# pull docker image
docker pull carlasim/carla:"$VERSION"

# quality
if [ $(hostname) = "primus" ]; then
	QUALITY="Epic"
else
	QUALITY="Low"
fi
echo "Running with $QUALITY quality"

# try run command
CONT_ID=$(docker ps -aqf "name=^carla_docker_${VERSION//./}")
if [ "$CONT_ID" == "" ];
then
	echo "Starting fresh docker container"
	docker run -p 2000-2002:2000-2002\
	  --name carla_docker_"${VERSION//./}" \
	  --privileged \
	  --cpuset-cpus="0-5" \
	   --runtime=nvidia \
	    --gpus 'all,"capabilities=graphics,utility,display,video,compute"' \
	     -e DISPLAY=$DISPLAY \
	     -e XAUTHORITY=$XAUTHORITY \
	      -v /tmp/.X11-unix:/tmp/.X11-unix \
	        carlasim/carla:"$VERSION" \
		 ./CarlaUE4.sh -nosound -quality-level=$QUALITY &
else
	echo "Restarting docker container with ID: $CONT_ID"
	docker restart "$CONT_ID"
fi

exit 0
