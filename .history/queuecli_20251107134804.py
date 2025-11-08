import argparse
import json

def main():
    parser = argparse.ArgumentParser(description="QueueCLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # 'enqueue' command
    enqueue_parser = subparsers.add_parser("enqueue", help="Add a job to the queue")
    args,extra=parser.parse_known_args()

    if args.command == "enqueue":
        raw_input=" ".join(extra).strip()
        if not raw_input:
            print("paste your JSON")
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
