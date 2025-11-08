import argparse

def main():
    parser=argparse.ArgumentParser(description="QueueCLI")
    subparsers=parser.add_subparsers(dest="command",help="Commands")
    #enqueue
    enqueue_parser=subparsers.add_parser("enqueue", help="Add a job to the queue")
    enqueue_parser.add_argument("job_name",help="Name of the job")
    #rum
    run_parser=subparsers.add_parser("run-worker",help="start the worker")


    args=parser.parse_args()

    if args.command=="enqueue":
        print(f"enqueued job:{args.job_name}")
    elif args.commad=="run-worker":
        print("worker started")
    else:
        parser.print_help()

if __name__=="__main__":
    main()