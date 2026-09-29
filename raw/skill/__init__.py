import os
import duckdunk
import requests
import subprocess
import shlex

def safe(workspace: str, path: str) -> bool:
    workspace = os.path.realpath(workspace)
    target = os.path.realpath(os.path.join(workspace, path))
    try:
        return os.path.commonpath([workspace, target]) == workspace
    except ValueError:
        return False

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(HERE, "attatchments")

def readfile(filename: str, workspace: str|None) -> dict:
    if workspace is None:
        FILE = os.path.join(HERE, filename)
        if not safe(HERE, filename):
            return {"status": "failed", "reason": "Given path outisde of attatchments"}
    else:
        FILE = os.path.join(workspace, filename)
        if not safe(workspace, filename):
            return {"status": "failed", "reason": "Given path outisde of directory"}
    if not os.path.exists(FILE):
        return {"status": "failed", "reason": "File not found"}
    if os.path.isdir(FILE):
        return {"status": "failed", "reason": "The requested path is a directory"}
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return {"status": "success", "content": f.read()}
    except Exception as e:
        return {"status": "failed", "reason": str(e)}

def makefile(filename: str, workspace: str|None) -> dict:
    if workspace is None:
        return {"status": "failed", "reason": "No workspace found"}
    FILE = os.path.join(workspace, filename)
    if not safe(workspace, filename):
        return {"status": "failed", "reason": "Path outside of directory"}
    if os.path.exists(FILE):
        return {"status": "failed", "reason": "File already exists"}
    with open(FILE, "w"):
        pass
    return {"status": "success"}

def writefile(filename: str, content: str, workspace: str|None) -> dict:
    if workspace is None:
        return {"status": "failed", "reason": "No workspace found"}
    FILE = os.path.join(workspace, filename)
    if not safe(workspace, filename):
        return {"status": "failed", "reason": "Given path outisde of directory"}
    if not os.path.exists(FILE):
        return {"status": "failed", "reason": "File does not exist"}
    try:
        with open(FILE, "w", encoding="utf-8") as f:
            f.write(content)
            return {"status": "success"}
    except Exception as e:
        return {"status": "failed", "reason": str(e)}

def searchweb(query: str) -> dict:
    try:
        requests.get("https://www.google.com/generate_204", timeout=3)
    except Exception as e:
        return {"status": "failed", "reason": str(e)}
    results = duckdunk.web_search(query, delay=0)
    if not results:
        return {"status": "failed", "reason": "No results"}
    output = []
    for result in results[:5]:
        output.append(f"Title: {result.title}\nURL: {result.url}\nContent: {result.text()[:2000]}")
    return {"status": "success", "content": "\n\n---\n\n".join(output)}

def readattatchment(filename: str) -> dict:
    file = os.path.join(HERE, filename)
    if not safe(HERE, filename):
        return {"status": "failed", "reason": "Given path outisde of attatchments"}
    if not os.path.exists(file):
        return {"status": "failed", "reason": "No such attatchment"}
    try:
        with open(file, "r", encoding="utf-8") as f:
            return {"status": "success", "content": f.read()}
    except Exception as e:
        return {"status": "failed", "reason": str(e)}

import shlex
import subprocess

def runcommand(command: str, workspace: str|None) -> dict:
    if workspace is None:
        return {"status": "failed", "reason": "No workspace found"}
    try:
        args = shlex.split(command)
        if not args:
            return {"status": "failed", "reason": "Empty command"}
        r = subprocess.run(args, cwd=workspace, capture_output=True, text=True, timeout=30)
        return {"status": "success", "returncode": r.returncode,
                "stdout": r.stdout[-4000:], "stderr": r.stderr[-4000:]}
    except subprocess.TimeoutExpired:
        return {"status": "failed", "reason": "Command timed out after 30s"}
    except FileNotFoundError:
        return {"status": "failed", "reason": f"Command not found: {args[0]}"}
    except Exception as e:
        return {"status": "failed", "reason": str(e)}
    