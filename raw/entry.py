import os
import sys
import subprocess

if getattr(sys, "frozen", False):
    HERE = os.path.dirname(sys.executable)
else:
    HERE = os.path.abspath(os.path.dirname(__file__))

LUCID = os.path.join(HERE, "gui.py")

subprocess.Popen(["py", LUCID], creationflags=subprocess.CREATE_NO_WINDOW)
sys.exit()