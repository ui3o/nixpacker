import os.path
import subprocess
import sys
import re
import json
import hashlib

# print(sys.argv)
# print(f"NIP_INSTALL is {os.environ.get('NIP_INSTALL', None)}")


def info(msg: str):
    print(f"[INFO] {msg}")
    sys.stdout.flush()


def imagePull(tags: list[str]):
    # check if docker image was pulled
    podman = "/template/podman"
    for tag in tags:
        if os.path.exists(os.path.expanduser(f"~/.nix/info/{tag}.info")) is False:
            image = f"docker.io/ui3o/nixpacker:{tag}"
            info(f"pull and run docker image: {image}")
            subprocess.run(f"{podman} pull {image}", shell=True)
            subprocess.run(
                f"{podman} run --privileged --rm -v $OS_HOME/.nix:/nix -it {image}",
                shell=True,
            )


def createGeneration(
    tags: list[str], defaults: dict[str, str], osBindings: dict[str, str]
):
    # check if docker image was pulled
    defToJson = json.dumps(defaults) + json.dumps(osBindings)
    osHome = os.environ.get("OS_HOME", None)
    md5sum = hashlib.md5(defToJson.encode("utf-8")).hexdigest()
    generationPath = os.path.expanduser(f"~/.nix/generations/{md5sum}")
    if os.path.isdir(generationPath) is False:
        info("create generation")
        imagePull(tags)
        subprocess.run(
            f"mkdir -p {generationPath} && cp -r ~/.nix/store/* {generationPath}/",
            shell=True,
        )
        for key, value in defaults.items():
            versionArray = value.split("||")
            endOfPath = ""
            version = versionArray[0]
            if len(versionArray) == 2:
                endOfPath = versionArray[1]
            allVersionRegex = re.compile(r".{32}-" + key + r"-.+" + endOfPath)
            taggedVersionRegex = re.compile(r".{32}-" + key + "-" + version + endOfPath)
            taggedHashedPath = ""
            for item in os.listdir(generationPath):
                if allVersionRegex.match(item) and taggedVersionRegex.match(item):
                    taggedHashedPath = item
                    info(f"add to env file this hashed path: {taggedHashedPath}")
                    with open(f"{generationPath}/paths", "a") as f:
                        f.write(
                            f"export PATH=/nix/store/{taggedHashedPath}/bin:$PATH\n"
                        )

            for item in os.listdir(generationPath):
                currentVersion = "-".join(
                    item.replace(endOfPath, "").split("-")[1:]
                ).replace(f"{key}-", "")
                if allVersionRegex.match(item):
                    if taggedVersionRegex.match(item) is None:
                        info(
                            f"set {key} version: {currentVersion} -> {version} ({item} -> {taggedHashedPath})"
                        )
                        subprocess.run(
                            f"ln -sf {taggedHashedPath} /nix/store/{item}",
                            shell=True,
                        )
        # if the new generation create have to make new osBindings
        info("create osBindings into generation folder")
        subprocess.run(f"mkdir -p {generationPath}/osBindings", shell=True)
        subprocess.run(f"cp /template/nip {generationPath}/osBindings", shell=True)
        for key, value in osBindings.items():
            with open(f"{generationPath}/osBindings/{key}", "w") as f:
                f.write("#!/bin/bash\n")
                f.write(f"export NIP_BASENAME={value}\n")
                f.write("nip\n")
            subprocess.run(f"chmod ugo+x {generationPath}/osBindings/{key}", shell=True)

    # create osBindings on host
    subprocess.run(
        f"ln -sf {osHome}/.nix/generations/{md5sum}/osBindings /root/.nix/bin",
        shell=True,
    )
    # create generation link in container
    subprocess.run(f"ln -sf {generationPath} /nix/store", shell=True)


def preCheck():
    if os.path.exists("/template/configs/config.py") is False:
        info("create required directories")
        subprocess.run(
            "mkdir -p ~/.nix/generations ~/.nix/warehouse ~/.nix/info ~/.nix/store ~/.config/nip",
            shell=True,
        )
        info("copy typings into host config folder")
        subprocess.run("cp /template/configs_tmp/typings.py ~/.config/nip/typings.py", shell=True)
        info("copy config.py into host config folder")
        subprocess.run("cp /template/configs_tmp/config.py ~/.config/nip", shell=True)
    
    import configs.config as config

    # create link generation
    createGeneration(
        config.config["tags"], config.config["defaults"], config.config["osBindings"]
    )


if sys.argv[1] == "nip" or os.environ.get("NIP_INSTALL", None) is not None:
    preCheck()
else:
    preCheck()

    # exit 78 means eval script from /script file
    with open("/script", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"export PATH=/template:{os.environ.get("PATH", None)}\n")
        f.write("source /nix/store/paths\n")
        # TODO hello --version nem ment at
        f.write("bash\n")
        f.write(" ".join(sys.argv[1:]) + "\n")
    os._exit(78)
