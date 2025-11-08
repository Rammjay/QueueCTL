import argparse
import json

def main():
    parser=argparse.ArgumentParser(description="QueueCLI")
    subparsers=parser.add_subparsers(dest="command",help="Commands")
    #enqueue
    enqueue_parser=subparsers.add_parser("enqueue", help="Add a job to the queue")
    enqueue_parser.add_argument("job_data",help="job data in JSON")
    #run
    run_parser=subparsers.add_parser("run-worker",help="start the worker")
    #


    args=parser.parse_args()

    if args.command=="enqueue":
        try:
            job=json.loads(args.job_data)
            print("enqueued job:")
            print(json.dumps(job,indent=2))
        except json.JSONDecodeError as e:
            print("invalid input:")


    elif args.command=="run-worker":
        print("worker started")
    else:
        parser.print_help()

if __name__=="__main__":
    main()