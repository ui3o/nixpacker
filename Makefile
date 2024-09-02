build-amd64:
	podman build --platform=linux/amd64 --build-arg=ARCH=amd64 --tag local-nixpacker .
build-arm64:
	podman build --env GIT_TAG="hello--2.10" --build-arg=CERTS="$(CERTS)" --platform=linux/arm64 --build-arg=ARCH=arm64 --tag local-debtonix .

