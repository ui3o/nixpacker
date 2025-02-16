import os.path
import subprocess
import sys
import re
import json
import hashlib

# print(sys.argv)
# print(f"NIP_INSTALL is {os.environ.get('NIP_INSTALL', None)}")

generationPath = ""
homeFolder = os.environ.get("HOME", "")
defaultsMap: dict[str, str] = {}


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


def genOsProgram(generationPath: str, osName: str, containerName: str):
    info(f"create program on host os: {osName}")
    with open(f"{generationPath}/osBindings/{osName}", "w") as f:
        f.write("#!/bin/bash\n")
        f.write('ARGS=""\n')
        f.write("for v in \"$@\" ;do ARGS+=$v && ARGS+='____';done\n")
        f.write("export NIP_PROGRAM_ARGS=$ARGS\n")
        f.write(f"export NIP_BASENAME={containerName}\n")
        f.write("nip $@\n")
    execute(f"chmod ugo+x {generationPath}/osBindings/{osName}")


def imagePull(tags: list[str]):
    # check if docker image was pulled
    podman = "/template/podman"
    for tag in tags:
        image = f"docker.io/ui3o/nixpacker:{tag}"
        if os.path.exists(os.path.expanduser(f"~/.nix/info/{tag}.info")) is False:
            info(f"pull and run docker image: {image}")
            execute(
                f"{podman} run --pull=always --privileged --rm -v $HOME/.nix:/nix -it {image}"
            )
        else:
            info(f"this docker image already pulled: {image}")


def createGeneration(
    tags: list[str],
    defaults: dict[str, str],
    osBindings: dict[str, str],
    ports: list[str],
):
    global generationPath, homeFolder
    # check if docker image was pulled
    defToJson = (
        json.dumps(tags)
        + json.dumps(defaults)
        + json.dumps(osBindings)
        + json.dumps(ports)
    )
    md5sum = hashlib.md5(defToJson.encode("utf-8")).hexdigest()
    generationPath = os.path.expanduser(f"~/.nix/generations/{md5sum}")
    # create osBindings on host
    execute(
        f"ln -snf {homeFolder}/.nix/generations/{md5sum}/osBindings {homeFolder}/.nix/bin"
    )
    execute(
        f"ln -snf {homeFolder}/.nix/generations/{md5sum}/osLibs {homeFolder}/.nix/osLibs"
    )
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
                    defaultsMap[key] = f"/nix/warehouse/{taggedHashedPath}"
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
        execute(f"cp /template/nip.sh {generationPath}/osBindings/nip")
        for key, value in osBindings.items():
            if value == "@":
                defProgram = defaultsMap.get(key)
                if defProgram is not None:
                    ln = defProgram.replace(
                        "/nix", f"{generationPath.split('/.nix')[0]}/.nix"
                    )
                    libPath = f"{generationPath}/osLibs/{key}-{defaults.get(key)}"
                    execute(f"mkdir -p {libPath}")
                    for defItem in os.listdir(defProgram):
                        info(f"osLib link create for: {libPath}/{defItem}")
                        if defItem != "bin":
                            info(f"ln -snf {ln}/{defItem} {libPath}/{defItem}")
                            execute(f"ln -snf {ln} {libPath}/{defItem}")
                    execute(f"ln -snf {generationPath}/osBindings {libPath}/bin")

                    for binItem in os.listdir(f"{defProgram}/bin"):
                        genOsProgram(generationPath, binItem, binItem)
                else:
                    warn(f"in the config defaults has no key: {key}")
            else:
                genOsProgram(generationPath, key, value)


def preCheck():
    if os.path.exists("/template/nip/config.py") is False:
        info("create required directories")
        execute(
            "mkdir -p ~/.nix/generations ~/.nix/warehouse ~/.nix/info ~/.nix/store ~/.config/nip"
        )
        info("copy typings into host config folder")
        execute("cp /template/nip_tmp/typings.py ~/.config/nip/typings.py")
        info("copy config.py into host config folder")
        execute("cp /template/nip_tmp/config.py ~/.config/nip")

    import nip.config as config

    # create link generation
    createGeneration(
        config.config["tags"],
        config.config["defaults"],
        config.config["osBindings"],
        config.config["ports"],
    )


if sys.argv[1].startswith("nip"):
    preCheck()
    info(f"current generation is {generationPath}")
else:
    preCheck()

    # TODO cwd resolve
    cwd = os.environ.get("PWD", "None")
    if cwd.find(homeFolder) == -1:
        warn(
            "only home folder mount supported! for tmp work use ~/tmp or other folder..."
        )

    # exit 78 means eval script from /script file
    with open("/script", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"export PATH=/template:{os.environ.get('PATH', None)}\n")
        f.write("source /nix/store/paths\n")
        f.write("$NIP_BASENAME ")
        # f.write("echo ")
        args = os.environ.get("NIP_PROGRAM_ARGS", "").split("____")
        for a in args:
            if len(a) == 0:
                f.write("\n")
            else:
                f.write(f'"{a}" ')
        # f.write("bash")
    os._exit(78)
