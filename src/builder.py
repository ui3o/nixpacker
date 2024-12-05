import os
import sys
import re
import subprocess
from typing import Callable
import urllib.request
import json


def info(msg: str):
    print(msg)
    sys.stdout.flush()


def execute(cmd):
    info(f"[RUN] {cmd}")
    subprocess.run(cmd, shell=True)


tag = os.environ.get("GIT_TAG", "gradle--1.8")
info("[INFO] check GITHUB_RELEASE environment var")
if os.environ.get("GITHUB_RELEASE", None) is not None:
    with urllib.request.urlopen(
        f"https://api.github.com/repos/ui3o/nixpacker/releases/tags/{tag}"
    ) as url:
        data = json.load(url)
        tag = data["name"]
        info(f"[INFO] collect tag from github {tag}")
package = tag.split("--")[0]
version = tag.split("--")[1]
info(f"[INFO] tag is {tag} and package is {package} with version {version}")
date = ""
keyName = ""
hash = ""
channel = ""


def chFinder(criteria: Callable[[str], bool]):
    global hash, keyName, date, channel
    contents: str = (
        urllib.request.urlopen("https://lazamar.co.uk/nix-versions/")
        .read()
        .decode("utf-8")
    )
    for ch in contents.split("option value=")[1:]:
        chName = ch.split('"')[1]
        if (
            chName.endswith("-unstable") is False
            and len(hash) == 0
            and criteria(chName)
        ):
            lookup: str = (
                urllib.request.urlopen(
                    f"https://lazamar.co.uk/nix-versions/?channel={chName}&package={package}"
                )
                .read()
                .decode("utf-8")
            )

            if lookup.find("<p>No results found</p>") > -1:
                info(f"[ERROR] No {package} package found on {chName} channel!")
            else:
                list = lookup.split("<tbody>")[1].split("</tbody>")[0].split("<tr")[1:]
                try:
                    el = [x for x in list if x.find(f"<td>{version}</td>") > -1][0]
                    # info(el)
                    hash = el.split("revision=")[1].split("&amp;")[0]
                    keyName = el.split("keyName=")[1].split("&amp;")[0]
                    date = el.split("</a></td><td>")[1].split("</td></tr>")[0]
                    channel = chName
                    info(
                        f"[INFO] meta found on {chName} channel: {keyName} {date} {hash}"
                    )
                except IndexError:
                    info(
                        f"[ERROR] No {package} package with {version} version found on {chName} channel!"
                    )


def armChNameChecker(ch: str) -> bool:
    if ch.endswith("-darwin"):
        return True
    return False


def x64ChNameChecker(ch: str) -> bool:
    if ch.startswith("nixos-"):
        return True
    return False


uname_output = subprocess.getoutput("uname -a")
if uname_output.find("x86_64") > -1:
    chFinder(x64ChNameChecker)
else:
    chFinder(armChNameChecker)


if len(hash) == 0:
    info(f"[ERROR] No {package} package found with {version} version!")
    os._exit(1)
else:
    info(f"[INFO] meta found on {channel} channel: {keyName} {date} {hash}")


# Write the file out again
with open(f"{package}--{version}.info", "w") as file:
    file.write(f"{package}, {version}, {keyName}, {date}, {hash}, {channel}\n")

execute(
    f"nix bundle --bundler github:NixOS/bundlers#toDEB -o debpack -f https://github.com/NixOS/nixpkgs/archive/{hash}.tar.gz {package}"
)
execute("/root/.nix-profile/bin/dpkg -x /root/debpack/*.deb /tmp")

rootDir = "/tmp/nix/store/"
regex = re.compile("/tmp/nix/store/.{33}" + package + "$")

for item in os.listdir(rootDir):
    d = os.path.join(rootDir, item)
    if os.path.isdir(d) and regex.match(d):
        execute(f"rm -rf {d}")
