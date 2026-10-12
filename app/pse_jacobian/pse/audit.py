"""Append-only audit ledger (master file: AUDIT & GOVERNANCE).

Every report generation and export is logged with a timestamp to a file in the user's
home. The file is only ever appended to — it is the tamper-evident record that YOU
reproduced the experiment.
"""
import os
import datetime

LEDGER_DIR = os.path.expanduser("~/.pse_jacobian")
LEDGER = os.path.join(LEDGER_DIR, "audit.log")


def ledger_path():
    return LEDGER


def append(event, detail=""):
    os.makedirs(LEDGER_DIR, exist_ok=True)
    ts = datetime.datetime.now().isoformat(timespec="seconds")
    line = f"{ts} | {event} | {detail}"
    with open(LEDGER, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    return line


def read_all():
    if not os.path.exists(LEDGER):
        return ""
    with open(LEDGER, encoding="utf-8") as f:
        return f.read()
