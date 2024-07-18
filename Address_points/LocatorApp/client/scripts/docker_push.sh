echo "*** Publishing ${npm_package_name} Docker image ***"

IMAGE=${REGISTRY}/${npm_package_name}

docker push $IMAGE:${npm_package_version}
docker push $IMAGE:latest

echo ""
docker images | grep $IMAGE
