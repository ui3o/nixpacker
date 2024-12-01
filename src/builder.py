import os
import sys
import re
import subprocess
import urllib.request
import json


def info(msg: str):
    print(msg)
    sys.stdout.flush()


def execute(cmd):
    info(f"[RUN] {cmd}")
    subprocess.run(cmd, shell=True)


FLAKE_FILE = os.environ["FLAKE_FILE"]

contents: str = (
    urllib.request.urlopen("https://lazamar.co.uk/nix-versions/").read().decode("utf-8")
)
darwin_latest_channel = contents.split("option value=")[1].split('"')[1]


channel = "nixpkgs-unstable"
uname_output = subprocess.getoutput("uname -a")
if uname_output.find("x86_64") == -1:
    channel = darwin_latest_channel


tag = os.environ["GIT_TAG"]
info("[INFO] check GITHUB_RELEASE environment var")
if os.environ.get("GITHUB_RELEASE", None) is not None:
    with urllib.request.urlopen(
        f"https://api.github.com/repos/ui3o/nixpacker/releases/tags/{tag}"
    ) as url:
        data = json.load(url)
        tag = data["name"]
        info(f"[INFO] collect tag from github {tag}")
info(f"[INFO] tag is {tag}")
package = tag.split("--")[0]
version = tag.split("--")[1]
date = ""
keyName = ""
hash = ""

info(f"[INFO] collect data for {package} {version}")
contents: str = (
    urllib.request.urlopen(
        f"https://lazamar.co.uk/nix-versions/?channel={channel}&package={package}"
    )
    .read()
    .decode("utf-8")
)

if contents.find("<p>No results found</p>") > -1:
    info(f"[ERROR] No package found on {channel} channel!")
    os._exit(1)
else:
    list = contents.split("<tbody>")[1].split("</tbody>")[0].split("<tr")[1:]
    try:
        el = [x for x in list if x.find(f"<td>{version}</td>") > -1][0]
        info(el)
        hash = el.split("revision=")[1].split("&amp;")[0]
        keyName = el.split("keyName=")[1].split("&amp;")[0]
        date = el.split("</a></td><td>")[1].split("</td></tr>")[0]
        info(f"[INFO] meta found on {channel} channel: {keyName} {date} {hash}")
    except IndexError:
        info(f"[ERROR] No package {version} version found on {channel} channel!")
        os._exit(1)

# Read in the file
with open(FLAKE_FILE, "r") as file:
    filedata = file.read()

# Replace the target string
filedata = filedata.replace("__ref__", hash)
filedata = filedata.replace("__pack__", keyName)

# Write the file out again
with open(FLAKE_FILE, "w") as file:
    file.write(filedata)

# Write the file out again
with open(f"{package}--{version}.info", "w") as file:
    file.write(f"{package}, {version}, {keyName}, {date}, {hash}, {channel}\n")

execute(
    f"/root/.nix-profile/bin/nix-channel --add https://nixos.org/channels/{channel} nixpkgs"
)
execute("/root/.nix-profile/bin/nix-channel --update")
execute("/root/.nix-profile/bin/nix-env -iA nixpkgs.dpkg")
# find /tmp/nix/store/ -depth 2 -name bin
execute(
    "/root/.nix-profile/bin/nix bundle --bundler github:NixOS/bundlers#toDEB -o debpack /root/flake.nix"
)
execute("/root/.nix-profile/bin/dpkg -x /root/debpack/*.deb /tmp")

rootDir = "/tmp/nix/store/"
regex = re.compile("/tmp/nix/store/.{33}" + package + "$")

for item in os.listdir(rootDir):
    d = os.path.join(rootDir, item)
    if os.path.isdir(d) and regex.match(d):
        execute(f"rm -rf {d}")
