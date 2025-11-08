import argparse
import json
import time
import threading
import queue
import os
import random
from filelock import FileLock
QUEUE_FILE = "queue.json"
CONFIG_FILE = "config.json"
STOP_FILE="stop.flag"
PROCESSED_FILE="processed.json"
FAILED_FILE="failed.json"
stop_event = threading.Event()
job_queue = queue.Queue()
MAX_RETRIES=3
DEFAULT_CONFIG = {
    "max_retries": 3,
    "backoff_base": 2,
    "failure_rate": 0.4  # for simulation (30% jobs fail)
}
lock=FileLock("queue.json.lock")
def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
def load_jobs(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_jobs(file_path,jobs):
    with open(file_path, "w") as f:
        json.dump(jobs, f, indent=2)

def job_exec_simulation(job):
    success=random.random()>0.2
    time.sleep(1)
    return success

def worker_thread(worker_id, config):
    print(f"Worker-{worker_id} started.")
    while not stop_event.is_set():
        if os.path.exists(STOP_FILE):
            break

        with lock:
            jobs = load_jobs(QUEUE_FILE)
            if jobs:
                job = jobs.pop(0)
                save_jobs(QUEUE_FILE, jobs)
            else:
                job = None  # no jobs available

        if job is None:
            time.sleep(1)
            continue

        job_id = job.get("id")
        retry_count = job.get("retries", 0)

        # 🔥 read from config
        max_retries = config.get("max_retries", 3)
        backoff_base = config.get("backoff_base", 2)
        failure_rate = config.get("failure_rate", 0.3)

        print(f"Worker-{worker_id} executing: {job.get('command')} (attempt {retry_count + 1})")
        success = random.random() > failure_rate

        if success:
            print(f"✅ Worker-{worker_id} finished: {job_id}")
            processed = load_jobs(PROCESSED_FILE)
            processed.append(job)
            save_jobs(PROCESSED_FILE, processed)
        else:
            retry_count += 1
            job["retries"] = retry_count
            if retry_count < max_retries:
                backoff = backoff_base ** retry_count
                print(f"⚠️ Job {job_id} failed. Retrying in {backoff}s ({retry_count}/{max_retries})")
                time.sleep(backoff)
                with lock:
                    jobs = load_jobs(QUEUE_FILE)
                    jobs.append(job)
                    save_jobs(QUEUE_FILE, jobs)
            else:
                print(f"❌ Job {job_id} moved to DLQ after {max_retries} failures.")
                with lock:
                    failed = load_jobs(FAILED_FILE)
                    failed.append(job)
                    save_jobs(FAILED_FILE, failed)

    print(f"Worker-{worker_id} stopped gracefully.")

def start_workers(count: int):
    # 🔥 load config at start
    config = load_config()

    if os.path.exists(STOP_FILE):
        os.remove(STOP_FILE)

    threads = []
    for i in range(count):
        t = threading.Thread(target=worker_thread, args=(i + 1, config), daemon=True)
        t.start()
        threads.append(t)

    print(f"✅ Started {count} worker(s). Run 'queuectl worker stop' to stop them.")
    try:
        while True:
            if os.path.exists(STOP_FILE):
                break
            time.sleep(1)
    except KeyboardInterrupt:
        pass

    stop_event.set()
    for t in threads:
        t.join()

    if os.path.exists(STOP_FILE):
        os.remove(STOP_FILE)
    print("👋 All workers stopped gracefully.")

def stop_workers():
    with open(STOP_FILE, "w") as f:
        f.write("stop")
    print("stop signal sent, workers will stop within a second.")
    time.sleep(1)
    if os.path.exists(STOP_FILE):
        os.remove(STOP_FILE)

def status_workers():
    pending=load_jobs(QUEUE_FILE)
    processed=load_jobs(PROCESSED_FILE)
    failed=load_jobs(FAILED_FILE)
    worker_state = "Running" if not os.path.exists(STOP_FILE) else "Stopped"

    print("\n📊 Queue Status Summary")
    print("-" * 35)
    print(f"🕐 Pending Jobs   : {len(pending)}")
    print(f"✅ Processed Jobs : {len(processed)}")
    print(f"Failed Jobs : {len(failed}}")
    print(f"⚙️  Worker State  : {worker_state}")
    print("-" * 35)
    if pending:
        print("🔸 Pending Job Details:")
        for job in pending:
            print(f"   • {job.get('id')} → {job.get('command')}")
    print("-" * 35)
def list_jobs(state):
    if state=='pending':
        jobs=load_jobs(QUEUE_FILE)
    elif state=='processed':
        jobs=load_jobs(PROCESSED_FILE)
    elif state=='failed':
        jobs=load_jobs(FAILED_FILE)
    else:
        print(f"Unknown state:{state}")
        return 
    print(f"\n📋 Jobs ({state.upper()})")
    print("-" * 40)
    if not jobs:
        print("No jobs found.")
    else:
        for job in jobs:
            print(f"• ID: {job.get('id')} | CMD: {job.get('command')}")
    print("-" * 40)

def dlq_list():
    jobs=load_jobs(FAILED_FILE)
    print("\n Dead letter queue")
    print("-"*40)
    if not jobs:
        print("No jobs in DLQ")
    else:
        for job in jobs:
            print(f"ID:{job.get('id')}|CMD:{job.get('command')}|Retires:{job.get('retries')}")
    print("-"*40)

def dlq_retry(job_id):
    with lock:
        failed=load_jobs(FAILED_FILE)
        job_to_retry=next((job for job in failed if job.get("id")==job_id),None)
        if not job_to_retry:
            print(f"❌ Job '{job_id}' not found in DLQ.")
            return
        failed = [job for job in failed if job.get("id") != job_id]
        save_jobs(FAILED_FILE, failed)

        job_to_retry["retries"] = 0
        jobs = load_jobs(QUEUE_FILE)
        jobs.append(job_to_retry)
        save_jobs(QUEUE_FILE, jobs)
        print(f"🔁 Job '{job_id}' moved back to queue for retry.")


def config_show():
    config = load_config()
    print("\n⚙️  Current Configuration")
    print("-" * 40)
    for k, v in config.items():
        print(f"{k}: {v}")
    print("-" * 40)

def config_set(key, value):
    config = load_config()
    if key not in config:
        print(f"❌ Unknown config key: {key}")
        print(f"Available keys: {', '.join(config.keys())}")
        return
    try:
        value = float(value) if '.' in value else int(value)
    except ValueError:
        pass
    config[key] = value
    save_config(config)
    print(f"✅ Config updated: {key} = {value}")

def config_get(key):
    config = load_config()
    if key in config:
        print(f"{key}: {config[key]}")
    else:
        print(f"❌ Unknown config key: {key}")
def main():
    parser = argparse.ArgumentParser(description="QueueCLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # enqueue
    enqueue_parser = subparsers.add_parser("enqueue", help="Add a job to the queue")
    enqueue_parser.add_argument("--json", help="Job data in JSON format")

    # worker
    worker_parser = subparsers.add_parser("worker", help="Worker management")
    worker_sub = worker_parser.add_subparsers(dest="worker_cmd", help="Worker subcommands")

    start_parser = worker_sub.add_parser("start", help="Start one or more workers")
    start_parser.add_argument("--count", type=int, default=1, help="Number of workers to start")

    worker_sub.add_parser("stop", help="Stop running workers")
    subparsers.add_parser("status", help="Show summary of job states & active workers")
    
    list_parser=subparsers.add_parser("list",help="list jobs by state")
    list_parser.add_argument("--state",required=True, help="State to list")

    dlq_parser=subparsers.add_parser("dlq",help="dead letter queue operations")
    dlq_sub=dlq_parser.add_subparsers(dest="dlq_cmd",help="DLQ subcommands")

    dlq_sub.add_parser("list",help="list jobs in DLQ")
    retry_parser=dlq_sub.add_parser("retry",help="retry a DLQ job")
    retry_parser.add_argument("job_id",help="job ID to retry")

    # config
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_sub = config_parser.add_subparsers(dest="config_cmd", help="Config subcommands")

    config_show_parser = config_sub.add_parser("show", help="Show current configuration")
    config_set_parser = config_sub.add_parser("set", help="Set configuration value")
    config_set_parser.add_argument("key", help="Config key")
    config_set_parser.add_argument("value", help="Value")
    config_get_parser = config_sub.add_parser("get", help="Get configuration value")
    config_get_parser.add_argument("key", help="Config key")
    args = parser.parse_args()

    if args.command == "enqueue":
        job_data = args.json or input("Paste JSON job:\n> ")
        try:
            job = json.loads(job_data)
            jobs = load_jobs(QUEUE_FILE)
            jobs.append(job)
            save_jobs(QUEUE_FILE,jobs)
            print(f"Enqueued job: {job.get('id')}")
        except json.JSONDecodeError as e:
            print(f"Invalid JSON input: {e}")

    elif args.command == "worker":
        if args.worker_cmd == "start":
            start_workers(args.count)
        elif args.worker_cmd == "stop":
            stop_workers()
        else:
            worker_parser.print_help()
    elif args.command=="status":
        status_workers()
    elif args.command=="list":
        list_jobs(args.state.lower())
    elif args.command == "dlq":
        if args.dlq_cmd == "list":
            dlq_list()
        elif args.dlq_cmd == "retry":
            dlq_retry(args.job_id)
        else:
            dlq_parser.print_help()
    elif args.command == "config":
        if args.config_cmd == "show":
            config_show()
        elif args.config_cmd == "set":
            config_set(args.key, args.value)
        elif args.config_cmd == "get":
            config_get(args.key)
        else:
            config_parser.print_help()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
