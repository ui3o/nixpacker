import os.path
import os
import signal
import subprocess
import sys
import re
import threading
import nip.config as config

sshUri = "ssh://$OS_USER@host.containers.internal:1222"
ssh = f"ssh -t -o StrictHostKeyChecking=no -o LogLevel=QUIET {sshUri}"
lsof = "lsof -i -P -n"


def warn(msg: str):
    print(f"[WARN] {msg}")
    sys.stdout.flush()


def info(msg: str):
    print(f"[INFO] {msg}")
    sys.stdout.flush()


def lsofChecker(cmd: str, openedList: str) -> list[str]:
    result = {}
    portRegex = re.compile(r"(.*:)(.*)")
    try:
        out = (
            subprocess.check_output(
                cmd,
                shell=True,
            )
            .decode()
            .lower()
        )
        for line in out.splitlines():
            if line.endswith("(listen)"):
                p = int(portRegex.sub(r"\g<2>", line).split(" ")[0])
                # info(f"line is: {line}")
                if str(p) not in openedList:
                    for r in config.config["ports"]:
                        if "-" in r:
                            fromTo = r.split("-")
                            if len(fromTo[0]) == 0:
                                fromTo[0] = "0"
                            if len(fromTo[1]) == 0:
                                fromTo[1] = "65535"
                            if int(fromTo[0]) <= p <= int(fromTo[1]):
                                # info(f"result append range: {p}, {fromTo}")
                                result[p] = ""
                        else:
                            if int(r) == p:
                                # info(f"port append: {p}, {fromTo}")
                                result[p] = ""
    except subprocess.CalledProcessError:
        pass
    finally:
        # info(f"result is {result}")
        return list(result.keys())


def executeBackground(cmd: str) -> int:
    p = subprocess.Popen(cmd, shell=True)
    return p.pid


ExitEvent = threading.Event()


def openedPortList():
    containerList = ""
    hostList = ""
    pid = -1
    while not ExitEvent.is_set():
        _containerList = ""
        _hostList = ""
        for port in lsofChecker(lsof, hostList):
            _containerList += f"-R {port}:localhost:{port} "
            # pass
        for port in lsofChecker(f"{ssh} {lsof}", containerList):
            _hostList += f"-L {port}:localhost:{port} "
        if _containerList != containerList or _hostList != hostList:
            containerList = _containerList
            hostList = _hostList
            if pid != -1:
                info(f"kill last pid {pid}")
                os.kill(pid, signal.SIGKILL)
            info(f"> ssh -N {hostList} {containerList} {sshUri}")
            pid = executeBackground(f"ssh -N {hostList} {containerList} {sshUri}")

        ExitEvent.wait(0.1)


def threadCreator(targets=[]):
    for t in targets:
        th = threading.Thread(target=t)
        th.daemon = True
        th.start()


if config.config.get("ports"):
    try:
        threadCreator([openedPortList])
        while not ExitEvent.is_set():
            ExitEvent.wait()
    except KeyboardInterrupt:
        pass
    finally:
        pass
