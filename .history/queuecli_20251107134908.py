import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(description="QueueCLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # 'enqueue' command
    enqueue_parser = subparsers.add_parser("enqueue", help="Add a job to the queue")

    args, extra = parser.parse_known_args()

    if args.command == "enqueue":
        # Get the entire raw JSON string (after the word 'enqueue')
        raw_input = " ".join(extra).strip()

        if not raw_input:
            print("📥 Paste your JSON job and press Enter:")
            raw_input = input("> ")

        try:
            job = json.loads(raw_input)
            print("✅ Enqueued job:")
            print(json.dumps(job, indent=2))
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON input:\n{raw_input}\nError: {e}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
