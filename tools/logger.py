import os
from datetime import datetime

import sys

class TeeLogger:
    def __init__(self, filepath):
        self.file = open(filepath, "a")
        self.terminal = sys.stdout

    def write(self, message):
        self.terminal.write(message)
        self.file.write(message)

    def flush(self):
        self.terminal.flush()
        self.file.flush()

    def close(self):
        self.file.close()
        
class CrewLogger:
    def __init__(self, log_file="../flask-todo-generated/crew_log.txt"):
        self.log_file = os.path.abspath(log_file)
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        self._write(f"\n\n🕓 Run started: {datetime.now()}\n{'='*60}")

    def log(self, content: str):
        self._write(content)

    def _write(self, content):
        with open(self.log_file, "a") as f:
            f.write(content + "\n")
