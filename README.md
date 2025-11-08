
# **QueueCTL – Job Queue Command-Line System**

QueueCTL is a lightweight, file-based job queue and worker system built in Python.
It manages background job execution with support for multiple workers, automatic retries with exponential backoff, and a Dead Letter Queue (DLQ) for persistent failure handling.

This project is implemented entirely using Python’s standard libraries (with `filelock` for concurrency control) and designed to demonstrate the working principles of a distributed task queue.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Rammjay/queuectl.git
cd queuectl
```

### 2. Install Dependencies

QueueCTL only requires one external package:

```bash
pip install filelock
```

### 3. Running the CLI

You can check all available commands using:

```bash
python queuecli.py --help
```

---

## 💡 Note on JSON Input (Important)

Different shells handle **quotes inside JSON strings** differently.
You must use the correct syntax based on your environment.

| Environment                            | Example Command                                                                               | Works Because                                                                 |
| -------------------------------------- | --------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **Windows PowerShell**                 | `powershell<br>python queuecli.py enqueue --json '{""id"":""job1"",""command"":""sleep 2""}'` | PowerShell interprets `""` as a literal `"`, producing valid JSON internally. |
| **Windows CMD / Linux / macOS (Bash)** | `bash<br>python queuecli.py enqueue --json "{\"id\":\"job1\",\"command\":\"sleep 2\"}"`       | Escaped quotes (`\"`) are correctly passed to Python as `"` characters.       |

Both commands produce this valid JSON input:

```json
{"id":"job1","command":"sleep 2"}
```

---

### Example

```bash
# PowerShell
python queuecli.py enqueue --json '{""id"":""job5"",""command"":""echo Hello""}'

# CMD / Bash
python queuecli.py enqueue --json "{\"id\":\"job5\",\"command\":\"echo Hello\"}"
```

Both result in:

```
Enqueued job: job5
```

---



## Project Structure

```
QueueCTL/
├── queuecli.py          # Main CLI script
├── queue.json           # Pending jobs
├── processed.json       # Successfully completed jobs
├── failed.json          # Dead Letter Queue (DLQ)
├── config.json          # Configuration settings
└── README.md            # Project documentation
```

---

## Usage Examples

### 1. **Enqueue a Job**

```bash
python queuecli.py enqueue --json '{"id":"job1","command":"echo Hello World"}'
```

**Output:**

```
Enqueued job: job1
```

---

### 2. **Start Worker(s)**

```bash
python queuecli.py worker start --count 2
```

**Output:**

```
Worker-1 started.
Worker-2 started.
Started 2 worker(s).
Worker-1 executing: echo Hello World (attempt 1)
Hello World
Worker-1 finished: job1
All workers stopped gracefully.
```

---

### 3. **Stop Workers**

```bash
python queuecli.py worker stop
```

Stops all running workers gracefully after their current job.

---

### 4. **View Queue Status**

```bash
python queuecli.py status
```

Displays job counts and worker state:

```
Pending Jobs   : 0
Processed Jobs : 2
Failed Jobs    : 1
Worker State   : Running
```

---

### 5. **List Jobs**

```bash
python queuecli.py list --state pending
python queuecli.py list --state processed
python queuecli.py list --state failed
```

---

### 6. **View and Retry DLQ Jobs**

```bash
python queuecli.py dlq list
python queuecli.py dlq retry job1
```

---

### 7. **Configuration Management**

```bash
python queuecli.py config show
python queuecli.py config set max_retries 5
python queuecli.py config get backoff_base
```

---

## Architecture Overview

### **Job Lifecycle**

1. Jobs are added to `queue.json` via the **enqueue** command.
2. Workers pick up available jobs and execute their commands using `subprocess`.
3. If a job fails, it automatically retries using **exponential backoff** (`delay = base ^ attempt`).
4. After exceeding the configured retry limit, the job moves to the **Dead Letter Queue (DLQ)**.
5. All states (pending, processed, failed) persist across restarts through JSON-based storage.

---

### **Concurrency & Persistence**

* Uses **`filelock`** to ensure only one worker modifies `queue.json` at a time.
* Supports multiple worker threads to enable parallel job execution.
* Persists all data using simple JSON files — portable, transparent, and easy to inspect.

---

### **Graceful Shutdown**

Workers continuously check for a stop flag file (`stop.flag`).
When triggered, workers complete their current job before exiting safely — ensuring no job corruption or mid-process termination.

---

### **Configuration**

All runtime behavior is controlled by `config.json`:

```json
{
  "max_retries": 3,
  "backoff_base": 2,
  "failure_rate": 0.3
}
```

These values can be modified at runtime using CLI commands without editing the file directly.

---

## Assumptions & Trade-offs

| Aspect            | Decision                         | Rationale                                              |
| ----------------- | -------------------------------- | ------------------------------------------------------ |
| **Storage**       | JSON files                       | Simplifies setup and persistence; no DB dependency.    |
| **Concurrency**   | Python threads                   | Lightweight and sufficient for I/O-based workloads.    |
| **Locking**       | FileLock                         | Prevents duplicate job processing.                     |
| **Job Execution** | OS shell commands via subprocess | Realistic execution model using system-level commands. |
| **Retry Policy**  | Exponential backoff              | Standard, configurable failure recovery pattern.       |
| **Graceful Stop** | Stop flag file                   | Cross-platform and easy to manage.                     |

---


## Testing Instructions (PowerShell)

You can validate all major flows directly from **PowerShell** using these commands.


| Test                     | Command                                                                                                                        | Expected Result                                                    |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------ |
| **Enqueue valid job**    | `python queuecli.py enqueue --json '{""id"":""job1"",""command"":""echo success""}'`                                           | Job appears in `queue.json` and completes successfully.            |
| **Enqueue failing job**  | `python queuecli.py enqueue --json '{""id"":""job2"",""command"":""invalidcmd""}'`                                             | Retries automatically and moves to `failed.json` after 3 attempts. |
| **Parallel processing**  | `python queuecli.py worker start --count 3`<br>`python queuecli.py enqueue --json '{""id"":""job3"",""command"":""sleep 2""}'` | All jobs execute concurrently.                                     |
| **DLQ retry**            | `python queuecli.py dlq retry job2`                                                                                            | Job requeued into `queue.json`.                                    |
| **Configuration update** | `python queuecli.py config set max_retries 5`                                                                                  | Config updated and persisted in file.                              |

## Summary

This project was implemented to demonstrate understanding of background processing systems — focusing on job management, concurrency, retry handling, and graceful shutdowns.
It uses minimal dependencies and a modular structure that makes it easy to extend or migrate to a database-backed version later.


## Author

**<Rammohan J>**
Python Developer | QueueCTL Implementation
📧 [rammohanjram@gmail.com](mailto:rammohanjram@gmail.com)
🌐 [github.com/Rammjay>](https://github.com/Rammjay)


