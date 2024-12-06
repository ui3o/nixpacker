import os
import sys
import re
import subprocess
from typing import Callable
import urllib.request
import base64


def info(msg: str):
    print(msg)
    sys.stdout.flush()


def execute(cmd):
    info(f"[RUN] {cmd}")
    subprocess.run(cmd, shell=True)


tag = os.environ.get("GIT_TAG", "gradle--1.8--MS44")
package = tag.split("--")[0]
dockerVersion = tag.split("--")[1]
nixVersion = base64.b64decode(tag.split("--")[2]).decode("utf-8")
info(
    f"[INFO] tag is {tag} and package is {package} with version {nixVersion}/{dockerVersion}"
)
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
                    el = [x for x in list if x.find(f"<td>{nixVersion}</td>") > -1][0]
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
                        f"[ERROR] No {package} package with {nixVersion} version found on {chName} channel!"
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
    info(f"[ERROR] No {package} package found with {nixVersion} version!")
    os._exit(1)
else:
    info(f"[INFO] meta found on {channel} channel: {keyName} {date} {hash}")


# Write the file out again
with open(f"{package}--{dockerVersion}.info", "w") as file:
    file.write(f"{package}, {nixVersion}, {keyName}, {date}, {hash}, {channel}\n")

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
