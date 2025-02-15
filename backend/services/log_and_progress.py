from datetime import datetime

log_file = '../process.log'


def log_message(message, level='info'):
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f"[{level.upper()}] {message}\n")
    print(f"[{level.upper()}] {message} {datetime.now()}")


def update_progress(current, total):
    percentage = (current / total) * 100
    log_message(f"Progress: {percentage:.2f}% ({current}/{total})", level='info')


# progress_service.py
from typing import Dict, Optional
import threading

class ProgressTracker:
    def __init__(self):
        self._progress: Dict[str, Dict] = {}
        self._lock = threading.Lock()

    def create_task(self, task_id: str):
        with self._lock:
            self._progress[task_id] = {
                'parse_progress': 0,
                'strm_progress': 0,
                'json_progress': 0,
                'db_progress': 0,
                'current_stage': 'Initializing',
                'total_progress': 0,
                'is_complete': False,
                'error': None
            }

class ProgressTracker:
    def __init__(self):
        self.lock = threading.Lock()
        self.tasks = {}

    def create_task(self, task_id):
        with self.lock:
            self.tasks[task_id] = {
                "current_stage": "Initializing",
                "parse": 0,
                "strm": 0,
                "json": 0,
                "db": 0,
                "total_progress": 0,
                "is_complete": False,
                "error": None
            }

    def update_stage_progress(self, task_id, stage, progress):
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id][stage] = progress
                self.tasks[task_id]["total_progress"] = (
                    self.tasks[task_id]["parse"] * 0.25 +
                    self.tasks[task_id]["strm"] * 0.25 +
                    self.tasks[task_id]["json"] * 0.25 +
                    self.tasks[task_id]["db"] * 0.25
                )

    def update_status(self, task_id, status_message):
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]["current_stage"] = status_message

    def set_error(self, task_id, error_message):
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]["error"] = error_message
                self.tasks[task_id]["is_complete"] = True

    def complete_task(self, task_id):
        with self.lock:
            if task_id in self.tasks:
                self.tasks[task_id]["is_complete"] = True
                self.tasks[task_id]["total_progress"] = 100

    def get_progress(self, task_id):
        with self.lock:
            task = self.tasks.get(task_id)
            if not task:
                return None
            return {
                "current_stage": task["current_stage"],
                "total_progress": task["total_progress"],
                "is_complete": task["is_complete"],
                "error": task["error"]
            }

progress_tracker = ProgressTracker()
