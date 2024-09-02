import json
import os
import subprocess
    
VERSION_FILE = os.environ["VERSION_FILE"]
FLAKE_FILE = os.environ["FLAKE_FILE"]

# Open and read the versions.json file
with open(VERSION_FILE, "r") as file:
    data = json.load(file)

arch = "x86_64"
uname_output = subprocess.getoutput("uname -a")
if uname_output.find("x86_64")==-1:
    arch = "darwin"

tag = ""
for k in data:
    if k.startswith(os.environ["GIT_TAG"]) and k.endswith(f"--{arch}"):
        tag = k

sw = tag.split("--")[0]
version = tag.split("--")[1]
date = tag.split("--")[2]
hash = data[tag]

# Read in the file
with open(FLAKE_FILE, "r") as file:
    filedata = file.read()

# Replace the target string
filedata = filedata.replace("__ref__", hash)
filedata = filedata.replace("__pack__", sw)

# Write the file out again
with open(FLAKE_FILE, "w") as file:
    file.write(filedata)

# Write the file out again
with open(f"{tag}.info", "w") as file:
    file.write("")
