import os.path
import subprocess
import sys

# print(sys.argv)
# print(f"NIP_INSTALL is {os.environ.get('NIP_INSTALL', None)}")

if sys.argv[1] == "nip" or os.environ.get("NIP_INSTALL", None) is not None:
    subprocess.run(
        "mkdir -p ~/.nix/warehouse ~/.nix/info ~/.nix/store ~/.nix/bin ~/.config/nip",
        shell=True,
    )
    subprocess.run("cp /template/nip ~/.nix/bin", shell=True)
    subprocess.run("cp /template/typings.py ~/.config/nip/typings.py", shell=True)

    if os.path.exists(os.path.expanduser("~/.config/nip/config.py")) is False:
        subprocess.run("cp /template/config.py ~/.config/nip", shell=True)

    sys.path.append(os.path.expanduser("~/.config/nip"))
    import config

    # create host os binding == TODO
    for tag in config.config["tags"]:
        if os.path.exists(os.path.expanduser(f"~/.nix/info/{tag}.info")) is False:
            subprocess.run(
                f"/template/podman run --rm -v $HOME/.nix:/nix -it docker.io/ui3o/nixpacker:{tag}",
                shell=True,
            )


else:
    sys.path.append(os.path.expanduser("~/.config/nip"))
    import config

    subprocess.run("ln -sf /root/.nix/warehouse /warehouse", shell=True)
    subprocess.run("mkdir -p /nix && cp -r /root/.nix/store /nix", shell=True)

    # check if docker image was pulled
    for tag in config.config["tags"]:
        if os.path.exists(os.path.expanduser(f"~/.nix/info/{tag}.info")) is False:
            subprocess.run(
                f"/template/podman run --rm -v $HOME/.nix:/nix -it docker.io/ui3o/nixpacker:{tag}",
                shell=True,
            )

    # check docker image was pulled == TODO
    for tag in config.config["tags"]:
        if os.path.exists(os.path.expanduser(f"~/.nix/info/{tag}.info")) is False:
            subprocess.run(
                f"/template/podman run --rm -v $HOME/.nix:/nix -it docker.io/ui3o/nixpacker:{tag}",
                shell=True,
            )

    # exit 78 means eval script from /script file
    with open("/script", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"export PATH=/template:{os.environ.get("PATH", None)}\n")
        f.write(" ".join(sys.argv[1:]) + "\n")
    os._exit(78)
