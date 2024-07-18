npm run build

IMAGE=${REGISTRY}/${npm_package_name}

echo *** Building ${npm_package_name} Docker image ***

docker buildx build -t $IMAGE:$npm_package_version .
docker tag $IMAGE:${npm_package_version} $IMAGE:latest
