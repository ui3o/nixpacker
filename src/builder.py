import os
import sys
import re
import subprocess
from typing import Callable
import urllib.request


def info(msg: str):
    print(msg)
    sys.stdout.flush()


def execute(cmd):
    info(f"[RUN] {cmd}")
    subprocess.run(cmd, shell=True)


tag = os.environ.get("GIT_TAG", "openjdk--11.0.23.9")
package = tag.split("--")[0]
dockerVersion = tag.split("--")[1]
nixVersion = ""
info(f"[INFO] tag is {tag} and package is {package} with version {dockerVersion}")
date = ""
keyName = ""
hash = ""
channel = ""


def chFinder(criteria: Callable[[str], bool]):
    global hash, keyName, date, channel, nixVersion
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
                for el in list:
                    r = re.compile(dockerVersion)
                    v = el.split("</td><td>")
                    # info(v[1])
                    if r.fullmatch(v[1]) is not None:
                        # info(el)
                        nixVersion = v[1]
                        hash = el.split("revision=")[1].split("&amp;")[0]
                        keyName = el.split("keyName=")[1].split("&amp;")[0]
                        date = el.split("</a></td><td>")[1].split("</td></tr>")[0]
                        channel = chName
                        info(
                            f"[INFO] meta found on {chName} channel: {keyName} {nixVersion} {date} {hash}"
                        )
                        return
                if len(hash) == 0:
                    info(
                        f"[ERROR] No {package} package with {dockerVersion} version found on {chName} channel!"
                    )
                    return


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
    info(
        f"[ERROR] No {package} package found with {dockerVersion}/{nixVersion} version!"
    )
    os._exit(1)
else:
    info(f"[INFO] meta found on {channel} channel: {keyName} {date} {hash}")


# Write the file out again
with open(f"{package}--{dockerVersion}.info", "w") as file:
    file.write(
        f"{package}, {nixVersion}, {dockerVersion}, {keyName}, {date}, {hash}, {channel}\n"
    )

execute(
    f"nix bundle --bundler github:NixOS/bundlers#toDEB -o debpack -f https://github.com/NixOS/nixpkgs/archive/{hash}.tar.gz {keyName}"
)
execute("/root/.nix-profile/bin/dpkg -x /root/debpack/*.deb /tmp")

rootDir = "/tmp/nix/store/"
regex = re.compile("/tmp/nix/store/.{33}" + package + "$")

for item in os.listdir(rootDir):
    d = os.path.join(rootDir, item)
    if os.path.isdir(d) and regex.match(d):
        execute(f"rm -rf {d}")
