import argparse

def main():
    parser=argparse.ArgumentParser(description="QueueCLI")
    subparsers=parser.add_subparsers(dest="command",help="Commands")
    enqueue_parser=subparsers.add_parser("enqueue", help="Add a job to the queue")
    enqueue_parser.add_argument("job_name",help="Name of the job")

    args=parser.parse_args()

    if args.command=="enqueue":
        print("enqueued job={args.job_name}")
    else:
        parser.print_help()

if __name__=="main":
    main()