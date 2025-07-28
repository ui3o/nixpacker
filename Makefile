.PHONY: nip

nip:
	cd nip && podman build --tag nip:nip .
hello--2.12.2--Mi4xMi4y:
	podman build --env GIT_TAG="$@" --tag local-nixpacker:$@ .

