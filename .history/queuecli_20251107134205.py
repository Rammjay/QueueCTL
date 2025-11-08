import argparse
import json

def main():
    parser = argparse.ArgumentParser(description="QueueCLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # 'enqueue' command
    enqueue_parser = subparsers.add_parser("enqueue", help="Add a job to the queue")
    enqueue_parser.add_argument("--json", help="Job data in JSON format")

    args = parser.parse_args()

    if args.command == "enqueue":
        if args.json:
            jpb_data=args.json
        else:
            print("paste your  JSON and press enter")
            job_data=input("> ")
        try:
            # Parse the JSON input string into a Python dictionary
            job = json.loads(job_data)
            print("✅ Enqueued job:")
            print(json.dumps(job, indent=2))  # Pretty-print the job
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON input: {e}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
