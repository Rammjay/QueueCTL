import argparse
import json
PS C:\Users\rammo\OneDrive\Desktop\flam> python queuecli.py worker start --count 3
Traceback (most recent call last):
  File "C:\Users\rammo\OneDrive\Desktop\flam\queuecli.py", line 38, in <module>
    main() 
    ^^^^^^
  File "C:\Users\rammo\OneDrive\Desktop\flam\queuecli.py", line 31, in main
    start_workers(args.count)
    ^^^^^^^^^^^^^
NameError: name 'start_workers' is not defined. Did you mean: 'start_parser'?
PS C:\Users\rammo\OneDrive\Desktop\flam> 
def main():
    parser = argparse.ArgumentParser(description="QueueCLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # 'enqueue' command
    enqueue_parser = subparsers.add_parser("enqueue", help="Add a job to the queue")
    enqueue_parser.add_argument("job_data", help="Job data in JSON format")

    worker_parser=subparsers.add_parser("worker",help="Worker")
    worker_sub=worker_parser.add_subparsers(dest="worker_cmd",help="worker subcommands")

    start_parser=worker_sub.add_parser("start",help="Start one or more workers")
    start_parser.add_argument("--count",type=int, default=1,help="number of workers to start")

    stop_parser=worker_sub.add_parser("stop",help="stop running workers")
    args = parser.parse_args()

    if args.command == "enqueue":
        try:
            # Parse the JSON input string into a Python dictionary
            job = json.loads(args.job_data)
            print("✅ Enqueued job:")
            print(json.dumps(job, indent=2))  # Pretty-print the job
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON input: {e}")
    elif args.command=="worker":
        if args.worker_cmd=="start":
            start_workers(args.count)
        elif args.worker_cmd=="stop":
            print("to stop press ctrl+c")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()