import os
import shutil
import json


def logWrite(input, suffix, time, date):
    formed_path = f"Logs/{date}/{time}.txt"
    if os.path.exists("Logs/"+date):
        if os.path.exists(formed_path):
            file = open(formed_path, 'a')
            file.writelines(f"\n{suffix}: {input}")
            file.close()

def logWriteNew(messages, time, date):
    formed_path = f"Logs/{date}/{time}.txt"
    if os.path.exists("Logs/"+date):
        with open(formed_path, 'w') as file:
            json.dump(messages, file, indent=2)


def logRead(time, date):
    formed_path = f"Logs/{date}/{time}.txt"
    if not os.path.exists(f"Logs/{date}"):
        os.mkdir(f"Logs/{date}")

    if os.path.exists(formed_path):
        with open(formed_path, 'r') as file:
            logs = json.load(file)
        return logs
    else:
        _ = open(f"Logs/{date}/{time}.txt", "x")
        _.close()
        return None

def markLog(time, date, reason="Misc"):
    formed_path = f"Logs/{date}/{time}.txt"
    marked_path = f"MarkedLogs/{reason}/{date}.{time}.txt"
    if os.path.exists(formed_path):
        if not os.path.exists(marked_path[:marked_path.rfind("/")]):
            os.mkdir(f"MarkedLogs/{reason}")
        newFile = shutil.copy(formed_path, marked_path)
        if newFile is not None:
            return "Log has been marked successfully"
        else:
            return "Log has not been marked due to error"
    return "Log has not been marked due to error"

def postMarkLogWrite(messages, reason, time, date):
    logWriteNew(messages, time, date)

    formed_path = f"MarkedLogs/{reason}/{date}.{time}.txt"
    if os.path.exists(formed_path):
        with open(formed_path, 'w') as file:
            json.dump(messages, file, indent=2)
