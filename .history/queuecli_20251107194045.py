import argparse
import json
import time
import threading
import queue
import os
from filelock import FileLock
QUEUE_FILE = "queue.json"
STOP_FILE="stop.flag"
stop_event = threading.Event()
job_queue = queue.Queue()
lock=FileLock("queue.json.lock")
def load_jobs():
    if not os.path.exists(QUEUE_FILE):
        return []
    with open(QUEUE_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_jobs(jobs):
    with open(QUEUE_FILE, "w") as f:
        json.dump(jobs, f, indent=2)


def worker_thread(worker_id):
    print(f"Worker-{worker_id} started.")
    while not stop_event.is_set():
        with lock:
            jobs = load_jobs()
            if jobs:
                job = jobs.pop(0)
                save_jobs(jobs)
            else:
                job = None  # no jobs available

        if job is None:
            time.sleep(1)
            continue

        print(f"Worker-{worker_id} executing: {job.get('command')}")
        time.sleep(2)  # simulate work
        print(f"Worker-{worker_id} finished: {job.get('id')}")
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

def 

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

    args = parser.parse_args()

    if args.command == "enqueue":
        job_data = args.json or input("Paste JSON job:\n> ")
        try:
            job = json.loads(job_data)
            jobs = load_jobs()
            jobs.append(job)
            save_jobs(jobs)
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
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
