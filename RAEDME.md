# DNS Resolver with Redis Cache (Dockerized)

A **production-style DNS resolver** built using **Python**, **Redis**, and **Docker Compose**.

This project demonstrates how real-world DNS systems work internally:

* UDP-based DNS server
* Redis-backed DNS cache with TTL
* Rate limiting to prevent abuse
* Cache metrics (hit/miss/blocked)
* Fully containerized setup

> This is an **infrastructure-level project**, not a typical web CRUD app.

---

## 🚀 Features

* 🌐 **UDP DNS Server** (custom resolver)
* ⚡ **Redis-based DNS Cache** with TTL (Time To Live)
* 🚦 **Rate Limiting** (per-domain)
* 📊 **Cache Metrics** (total, hit, miss, blocked)
* 📦 **Docker Compose Orchestration**
* 🧪 Testable using `dig`

---

## 🧠 Architecture Overview

```
Client (dig / OS resolver)
        |
        |  UDP DNS Query (Port 1053)
        v
+-----------------------+
|  DNS Resolver (Python)|
|  - Cache Lookup       |
|  - Rate Limiting      |
|  - Upstream Forward   |
+----------+------------+
           |
           v
     Redis Cache (TTL)
           |
           v
     Upstream DNS (8.8.8.8)
```

---

## 🛠️ Tech Stack

* **Python 3.11**
* **dnspython** – DNS packet handling
* **Redis** – In-memory cache & counters
* **Docker & Docker Compose**
* **UDP Networking**

---

## 📁 Project Structure

```
DNS-Resolver/
│
├── resolver/
│   ├── udp_server.py     # UDP DNS server
│   ├── server.py         # CLI resolver (earlier phases)
│   └── __init__.py
│
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## ⚙️ How It Works

1. Client sends a DNS query (UDP)
2. Resolver checks **Redis cache**
3. If cache hit → respond immediately
4. If cache miss → forward to **8.8.8.8**
5. Store response in Redis with TTL
6. Apply rate limiting per domain
7. Return DNS response to client

---

## ▶️ Run the Project

### 1️⃣ Start the system

```bash
docker compose up --build
```

Expected log:

```
🚀 UDP DNS Server listening on 1053
```

---

### 2️⃣ Test DNS Resolution (Windows / macOS / Linux)

#### Recommended (works everywhere):

```bash
docker run --rm nicolaka/netshoot dig "@host.docker.internal" -p 1053 google.com
```

You should see:

```
;; ANSWER SECTION:
google.com.   300   IN   A   xxx.xxx.xxx.xxx
```

---

### 3️⃣ Verify Cache Behavior

Run the same command again:

* First time → `CACHE MISS`
* Second time → `CACHE HIT`

---

## 📊 View Cache Metrics

```bash
docker compose run resolver stats
```

Example output:

```
📊 DNS Cache Metrics
-------------------
Total Queries : 10
Cache Hits    : 6
Cache Misses  : 3
Rate Blocked  : 1
```

---

## 🚦 Rate Limiting

* **Limit**: 5 requests per domain per 10 seconds
* Excess queries receive `SERVFAIL`
* Implemented using Redis atomic counters + TTL

---

## 🧠 Key Concepts Demonstrated

* DNS resolution & record types
* TTL-based caching
* UDP networking
* Redis atomic operations
* Docker networking & port mapping
* Infrastructure observability

---

## 🧪 Supported DNS Record Types

* `A` (IPv4)
* `AAAA` (IPv6)
* `CNAME` (Alias)

---

## 📌 Why This Project Matters

This project mirrors how:

* ISPs cache DNS records
* CDNs accelerate name resolution
* DNS providers prevent abuse

It demonstrates **systems thinking**, **infra design**, and **backend depth**.

---

## 🔮 Future Enhancements

* Async DNS server (`asyncio`)
* Per-client (IP-based) rate limiting
* Prometheus `/metrics` endpoint
* Bind to port 53 with Linux capabilities
* Grafana dashboards

---

## ⭐ If you liked this project

Give it a ⭐ on GitHub and feel free to fork & extend it!
