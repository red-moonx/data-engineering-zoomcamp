# Module 07: Streaming (Real-Time Data Engineering)

These are my notes on the final module of the Data Engineering Zoomcamp. Here, we transition from batch processing to **Streaming**. This section covers the complexities of real-time data engineering, moving from basic Python-based Kafka consumers to enterprise-grade Apache Flink pipelines.

## 1. Introduction 

### 1.1. What is Streaming?
Streaming is a data processing paradigm where records are processed individually or in small micro-batches as they arrive, rather than waiting for a large set of data to be collected (Batch).

- **Unbounded Data**: Unlike batch (bounded) datasets, streams have no defined end; they are continuous.
- **Low Latency**: Processing happens in real-time or near real-time (milliseconds to seconds).
- **Event-Driven**: The system reacts to individual events as they occur (e.g., a taxi trip finishing, a credit card swipe).

### 1.2. Introduction to Apache Kafka
Apache Kafka is an open-source **distributed event store** and stream-processing platform. It acts as a central hub that allows different parts of a system to communicate asynchronously via events.

#### Core Concepts:
- **Topic**: A logical category where events are stored (similar to a table in a DB).
- **Partition**: Topics are split into partitions to allow multiple consumers to read data in parallel.
- **Broker**: A node in the Kafka cluster. Multiple brokers work together to ensure data is redundant and available.
- **Producer**: An application that pushes ("publishes") events into a topic.
- **Consumer**: An application that reads ("subscribes") events from a topic.
- **Consumer Group**: A group of consumers that work together to consume data from a topic, ensuring each message is processed only once within the group.

#### Why use a Message Broker?
In a traditional setup, every service has to talk to every other service (Point-to-Point). With a broker like Kafka:
1. **Decoupling**: The producer doesn't need to know who the consumer is or if they are even online.
2. **Buffering**: If a consumer is slow or goes down, Kafka stores the messages until the consumer is ready again.
3. **Immutability**: Once an event is written to Kafka, it cannot be changed, providing a reliable audit log.

---

## 🏗️ Chapter 1: Introduction to Streaming Architecture

Real-time data engineering involves handling high-velocity data and stateful aggregations.

### 1.1 Kafka vs. Red Panda
Apache Kafka is historically the industry standard, but it can be **heavy and complex** to run locally for testing (due to the JVM and ZooKeeper/KRaft overhead). 

For this reason, we are using **RedPanda** as a lightweight replacement:
- **Fast & Simple**: Written in C++, it has a much smaller footprint and starts up quickly.
- **Kafka-Compatible**: It use the same Kafka wire protocols, meaning our existing Kafka-based Python libraries and tools will work without any modification.
- **Modern**: It handles high-performance streaming without the JVM complexity, making it ideal for local development and testing.

### 1.2 The Producer & Consumer Pattern
The fundamental communication pattern in streaming:
- **Producer**: Turning Python data (or any object) into streamable bytes and sending them to a cluster.
- **Consumer**: Subscribing to topics to read those bytes back and process them.

---

## ⚙️ Chapter 2: Stream Processing & Data Ingestion

### 2.1 Database Integration (Sinks)
A critical part of a streaming pipeline is persistence. We learn how to move data from a live stream into a permanent **PostgreSQL** database for long-term storage and queryability.

### 2.2 Apache Flink Fundamentals
Flink is designed for high-throughput, low-latency stream processing.
- **Job Managers (The Brain)**: Handles coordination, checkpoints, and recovery.
- **Task Managers (The Muscle)**: Performs the actual data processing tasks.

---

## 🕒 Chapter 3: Advanced Streaming Concepts

### 3.1 Handling Late Data (Watermarks)
In real-time systems, data can arrive out of order. **Watermarks** are used to manage events that arrive late, allowing the system to progress time and trigger computations even when some data is missing or delayed.

### 3.2 Time Windows
Grouping continuous data into discrete time blocks is essential for calculating totals (e.g., "every 5 minutes").
- **Tumbling Windows**: Fixed-size, non-overlapping intervals.
- **Sliding/Session Windows**: More complex patterns for specialized analytics.

---

## 🗒️ Next Actions
- [ ] Setup Red Panda/Kafka cluster.
- [ ] Implement Python Producer for Taxi Data.
- [ ] Develop Flink job for real-time aggregations.
- [ ] Integrate with PostgreSQL Sink.

---
*The journey ends with real-time mastery!* 🌊⚡
