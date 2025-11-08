import argparse
import json
import time
import threading
import queue
import os
from filelock import FileLock
QUEUE_FILE = "queue.json"
STOP_FILE="stop.flag"
PROCESSED_FILE="processed.json"
FAILED_FILE="failed.json"
stop_event = threading.Event()
job_queue = queue.Queue()
MAX_RETRIES=3
lock=FileLock("queue.json.lock")
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
    return succcess

def worker_thread(worker_id):
    print(f"Worker-{worker_id} started.")
    while not stop_event.is_set():
        if os.path.exists(STOP_FILE):
            break
        with lock:
            jobs = load_jobs(QUEUE_FILE)
            if jobs:
                job = jobs.pop(0)
                save_jobs(QUEUE_FILE,jobs)
            else:
                job = None  # no jobs available

        if job is None:
            time.sleep(1)
            continue
            
        jo_id=job.get("id")
        retry_count=job.get("retries",0)


        print(f"Worker-{worker_id} executing: {job.get('command')}")
        success=job_exec_simulation(job)
        if success:
            print(f"worker-{worker_id} finished: {job_id}")
        time.sleep(2)  # simulate work
        print(f"Worker-{worker_id} finished: {job.get('id')}")
        processed=load_jobs(PROCESSED_FILE)
        processed.append(job)
        save_jobs(PROCESSED_FILE,processed)
    print(f"Worker-{worker_id} stopped gracefully.")

def start_workers(count: int):
    if os.path.exists(STOP_FILE):
        os.remove(STOP_FILE)
    threads = []
    for i in range(count):
        t = threading.Thread(target=worker_thread, args=(i + 1,), daemon=True)
        t.start()
        threads.append(t)

    print(f"Started {count} worker(s). Press Ctrl+C to stop.")
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
    print("All workers stopped gracefully.")
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
    worker_state = "Running" if not os.path.exists(STOP_FILE) else "Stopped"

    print("\n📊 Queue Status Summary")
    print("-" * 35)
    print(f"🕐 Pending Jobs   : {len(pending)}")
    print(f"✅ Processed Jobs : {len(processed)}")
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
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
