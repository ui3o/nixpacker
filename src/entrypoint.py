import os
import subprocess

# copy all /.nix packages into /nix/warehouse
subprocess.run("mkdir -p /nix/warehouse /nix/info /nix/bin /nix/store", shell=True)
subprocess.run("cp -rfv /.nix/store/. /nix/warehouse", shell=True)
subprocess.run("cp -rfv /.nix/*.info /nix/info", shell=True)

# generate symlinks to /nix/store
packs = [ f.name for f in os.scandir("/nix/warehouse/") if f.is_dir() ]
links = [ f.name for f in os.scandir("/nix/store/") if f.is_dir() ]
for dirname in list(packs):
    print(dirname)
    if dirname not in links:
        print("[INFO] generate symlink for: ", dirname)
        subprocess.run(["ln", "-s", f"/nix/warehouse/{dirname}", f"/nix/store/{dirname}"])
    else:
        print("[SKIP] generate symlink for: ", dirname)
