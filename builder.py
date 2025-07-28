import os
import sys
import re
import base64
import subprocess
from typing import Callable
import urllib.request


def info(msg: str):
    print(msg)
    sys.stdout.flush()


def execute(cmd):
    info(f"[RUN] {cmd}")
    subprocess.run(cmd, shell=True)


def decode_base64(data: str) -> bytes:
    # Add padding if needed
    missing_padding = len(data) % 4
    if missing_padding:
        data += "=" * (4 - missing_padding)
    return base64.b64decode(data)


tag = os.environ.get(
    "GIT_TAG", "openjdk--17.0.1.12.minimal.jre--MTcuMC4xKzEyLW1pbmltYWwtanJl"
)
package = tag.split("--")[0]
dockerVersion = tag.split("--")[1]
nixPackageVersion = decode_base64(tag.split("--")[2]).decode("utf-8")
info(
    f"[INFO] tag is '{tag}' and package is '{package}' with version '{dockerVersion}' and nix package version '{nixPackageVersion}'"
)
date = ""
keyName = ""
hash = ""
channel = ""


def chFinder(criteria: Callable[[str], bool]):
    global hash, keyName, date, channel, nixPackageVersion
    contents: str = (
        urllib.request.urlopen("https://lazamar.co.uk/nix-versions/")
        .read()
        .decode("utf-8")
    )
    for ch in contents.split("option value=")[1:]:
        chName = ch.split('"')[1]
        if len(hash) == 0 and criteria(chName):
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
                    v = el.split("</td><td>")
                    # info(v[1])
                    if nixPackageVersion == v[1]:
                        # info(el)
                        hash = el.split("revision=")[1].split("&amp;")[0]
                        keyName = el.split("keyName=")[1].split("&amp;")[0]
                        date = el.split("</a></td><td>")[1].split("</td></tr>")[0]
                        channel = chName
                        info(
                            f"[INFO] meta found on {chName} channel: {keyName} {nixPackageVersion} {date} {hash}"
                        )
                        return
                if len(hash) == 0:
                    info(
                        f"[ERROR] No {package} package with {dockerVersion} version found on {chName} channel!"
                    )
                    return


def x64ChNameChecker(ch: str) -> bool:
    if ch.startswith("nixos-"):
        return True
    return False


chFinder(x64ChNameChecker)


if len(hash) == 0:
    info(
        f"[ERROR] No {package} package found with {dockerVersion}/{nixPackageVersion} version!"
    )
    os._exit(1)
else:
    info(f"[INFO] meta found on {channel} channel: {keyName} {date} {hash}")


# Write the file out again
with open(f"{tag}.info", "w") as file:
    file.write(
        f"{package}, {nixPackageVersion}, {dockerVersion}, {keyName}, {date}, {hash}, {channel}\n"
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
