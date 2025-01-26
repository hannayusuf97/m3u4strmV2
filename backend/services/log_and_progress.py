from datetime import datetime

log_file = '../process.log'


def log_message(message, level='info'):
    with open(log_file, 'a', encoding='utf-8') as log:
        log.write(f"[{level.upper()}] {message}\n")
    print(f"[{level.upper()}] {message} {datetime.now()}")


def update_progress(current, total):
    percentage = (current / total) * 100
    log_message(f"Progress: {percentage:.2f}% ({current}/{total})", level='info')
