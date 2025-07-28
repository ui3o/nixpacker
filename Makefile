nip:
	cd nip && podman build --platform=linux/amd64 --tag nip:nip .
hello--2.12.2--Mi4xMi4y:
	podman build --env GIT_TAG="$@" --tag local-nixpacker:$@ .

