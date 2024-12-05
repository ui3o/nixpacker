import os.path
import subprocess
import sys
import re
import json
import hashlib

# print(sys.argv)
# print(f"NIP_INSTALL is {os.environ.get('NIP_INSTALL', None)}")

generationPath = ""


def warn(msg: str):
    print(f"[WARN] {msg}")
    sys.stdout.flush()


def info(msg: str):
    print(f"[INFO] {msg}")
    sys.stdout.flush()


def execute(cmd):
    # info(f"[RUN] {cmd}")
    subprocess.run(cmd, shell=True)


def pathNormalizer(name: str) -> str:
    return name.replace("+", "\\+")


def imagePull(tags: list[str]):
    # check if docker image was pulled
    podman = "/template/podman"
    for tag in tags:
        image = f"docker.io/ui3o/nixpacker:{tag}"
        if os.path.exists(os.path.expanduser(f"~/.nix/info/{tag}.info")) is False:
            info(f"pull and run docker image: {image}")
            execute(f"{podman} pull {image}")
            execute(f"{podman} run --privileged --rm -v $OS_HOME/.nix:/nix -it {image}")
        else:
            info(f"this docker image already pulled: {image}")


def createGeneration(
    tags: list[str], defaults: dict[str, str], osBindings: dict[str, str]
):
    global generationPath
    # check if docker image was pulled
    defToJson = json.dumps(tags) + json.dumps(defaults) + json.dumps(osBindings)
    osHome = os.environ.get("OS_HOME", None)
    md5sum = hashlib.md5(defToJson.encode("utf-8")).hexdigest()
    generationPath = os.path.expanduser(f"~/.nix/generations/{md5sum}")
    # create osBindings on host
    execute(f"ln -snf {osHome}/.nix/generations/{md5sum}/osBindings /root/.nix/bin")
    # create generation link in container
    execute(f"ln -snf {generationPath} /nix/store")

    if os.path.isdir(generationPath) is False:
        info("create generation")
        imagePull(tags)
        execute(f"mkdir -p {generationPath} && cp -r ~/.nix/store/* {generationPath}/")
        execute(f"touch {generationPath}/paths")
        for key, value in defaults.items():
            versionArray = value.split("||")
            endOfPath = ""
            version = versionArray[0]
            if len(versionArray) == 2:
                endOfPath = versionArray[1]
            allVersionRegex = re.compile(r".{32}-" + key + r"-.+" + f"{endOfPath}$")
            taggedVersionRegex = re.compile(
                r".{32}-" + f"{key}-{pathNormalizer(version)}{endOfPath}$"
            )
            taggedHashedPath = ""
            for item in os.listdir(generationPath):
                if taggedVersionRegex.match(item):
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
                if (
                    allVersionRegex.match(item)
                    and taggedVersionRegex.match(item) is None
                ):
                    if len(taggedHashedPath) > 0:
                        info(
                            f"set {key} version: {currentVersion} -> {version} ({item} -> {taggedHashedPath})"
                        )
                        execute(
                            f"ln -snf {pathNormalizer(taggedHashedPath)} /nix/store/{pathNormalizer(item)}"
                        )
                    else:
                        warn(
                            f"can not set {key} version: {currentVersion} -> {version} ({item} -> {taggedHashedPath})"
                        )
        # if the new generation create have to make new osBindings
        info("create osBindings into generation folder")
        execute(f"mkdir -p {generationPath}/osBindings")
        execute(f"cp /template/nip {generationPath}/osBindings")
        for key, value in osBindings.items():
            info(f"create program on host os: {key}")
            with open(f"{generationPath}/osBindings/{key}", "w") as f:
                f.write("#!/bin/bash\n")
                f.write(f"export NIP_BASENAME={value}\n")
                f.write("nip $@\n")
            execute(f"chmod ugo+x {generationPath}/osBindings/{key}")


def preCheck():
    if os.path.exists("/template/configs/config.py") is False:
        info("create required directories")
        execute(
            "mkdir -p ~/.nix/generations ~/.nix/warehouse ~/.nix/info ~/.nix/store ~/.config/nip"
        )
        info("copy typings into host config folder")
        execute("cp /template/configs_tmp/typings.py ~/.config/nip/typings.py")
        info("copy config.py into host config folder")
        execute("cp /template/configs_tmp/config.py ~/.config/nip")

    import configs.config as config

    # create link generation
    createGeneration(
        config.config["tags"], config.config["defaults"], config.config["osBindings"]
    )


if sys.argv[1] == "nip":
    preCheck()
    info(f"current generation is {generationPath.replace("/root", "~")}")
else:
    preCheck()

    # exit 78 means eval script from /script file
    with open("/script", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"export PATH=/template:{os.environ.get("PATH", None)}\n")
        f.write("source /nix/store/paths\n")
        # f.write("bash\n")
        f.write(" ".join(sys.argv[1:]) + "\n")
    os._exit(78)
