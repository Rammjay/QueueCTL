import argparse
import json

def main():
    parser = argparse.ArgumentParser(description="QueueCLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # enqueue command
    enqueue_parser = subparsers.add_parser("enqueue", help="Add a job to the queue")
    enqueue_parser.add_argument("job_data", nargs=argparse.REMAINDER, help="Job data in JSON format")

    # run-worker command
    run_parser = subparsers.add_parser("run-worker", help="Start the worker")

    args = parser.parse_args()

    if args.command == "enqueue":
        try:
            job = json.loads(raw_input)
            print("✅ Enqueued job:")
            print(json.dumps(job, indent=2))
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON input: {e}")

    elif args.command == "run-worker":
        print("👷 Worker started...")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
