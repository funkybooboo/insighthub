# RabbitMQ Shared Library for Python

This module provides **simple, reusable functions** to publish and consume messages via RabbitMQ. It is designed for **job queue workflows** where a server posts jobs and workers process them.

---

## **Installation**

Install dependencies with Poetry:

```bash
poetry add pika python-dotenv
```

Create a `.env` file in your project root with your RabbitMQ URL:

```env
RABBITMQ_URL=amqp://username:password@hostname:5672/
```

> If using Docker Compose, the hostname can be the service name, e.g.:
> `RABBITMQ_URL=amqp://insighthub:insighthub_dev@rabbitmq:5672/`

---

## **Usage**

### **Publishing messages**

```python
from rabbitmq_lib import publish_message

message = {
    "job_id": 123,
    "type": "process_data",
    "payload": {"foo": "bar"}
}

publish_message("jobs_queue", message)
```

* Sends a **persistent JSON message** to a durable queue.
* The queue is automatically declared if it doesn’t exist.

### **Consuming messages**

```python
from rabbitmq_lib import consume_messages

def handle_job(message):
    print(f"Received job: {message}")
    # Process job here

consume_messages("jobs_queue", handle_job)
```

* Messages are acknowledged **only after successful processing**.
* Messages remain in the queue if the worker crashes before completing.
* Expects messages in **JSON format**.

---

## **Workflow Diagram**

```
 +----------------+       +----------------------+       +------------------+
 |                |       |                      |       |                  |
 |     Server     |       |   RabbitMQ Queue     |       |     Workers      |
 |  (API/Backend) | ----> |     "jobs_queue"     | ----> |   process jobs   |
 |                |       |                      |       |                  |
 +----------------+       +----------------------+       +------------------+
         |                        |                             |
         |  Write job to DB       |                             |
         |----------------------->|                             |
         |                        |                             |
         |  Publish message       |                             |
         |----------------------->|                             |
         |                        |  Deliver message            |
         |                        |---------------------------->|
         |                        |                             |
         |                        |                             |
         |                        |   Worker processes job      |
         |                        |                             |
         |                        |<----------------------------|
         |                        |                             |
         |                        |  Worker updates DB / status |
         |                        |                             |
```

**Explanation:**

1. **Server creates a job** in the database and then publishes a message to RabbitMQ.
2. **RabbitMQ queues the message** until a worker consumes it.
3. **Worker consumes the message**, processes the job, and updates the database.
4. Messages are **acknowledged only after successful processing**, ensuring reliability.

---

## **Features**

* Durable queues and persistent messages (survive RabbitMQ restarts).
* Manual acknowledgments for reliability.
* JSON-encoded messages for structured data.
* Simple, reusable API suitable for multiple workers.

---

## **Best Practices**

1. Commit database transactions **before publishing messages** to avoid race conditions.
2. Workers should be **idempotent**, so retries or duplicate messages are safe.
3. Include meaningful identifiers (e.g., `job_id`) in your messages.
4. Consider **separate queues** for different job types for scalability.

---

This makes the workflow **super clear for developers**, showing exactly how jobs flow from server → RabbitMQ → workers → DB.
