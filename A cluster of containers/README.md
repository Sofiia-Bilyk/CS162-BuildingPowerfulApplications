# PCW 22: Docker Compose and Multi-Container Applications

## Q1. What has changed since last session?

Key differences between the `session_21/web` and `session_22/web` directories:

1. **Database switch from SQLite to PostgreSQL**: `app.py` changed its `SQLALCHEMY_DATABASE_URI` from `'sqlite://'` (an in-memory SQLite database) to `'postgresql://cs162_user:cs162_password@db/cs162'` (a PostgreSQL server). The commented-out environment variable example from session 21 was removed since the connection is now hardcoded to the Postgres service.

2. **New `docker-compose.yml` file added**: This file orchestrates three services:
   - `web` — the Flask calculator app (2 replicas)
   - `db` — a PostgreSQL database (`postgres:alpine`)
   - `adminer` — a web-based database admin UI on port 8080

**Why these changes were made**: Session 21 used an in-memory SQLite database, which is simple but ephemeral and unsuitable for multi-container or multi-replica setups (each container would have its own isolated in-memory DB). Session 22 introduces a shared PostgreSQL database running in its own container, allowing all Flask replicas to read/write to the same persistent data store. The `docker-compose.yml` ties everything together so the full stack can be launched with a single command.

## Q2. What was different between manual and automatic configurations?

The major obvious difference is the **number of web replicas**. When bringing the system up manually (e.g., `docker run`), you typically start **one** instance of the Flask container. When using `docker stack deploy` with the `docker-compose.yml`, the configuration specifies `replicas: 2`, so **two** instances of the Flask web server are launched automatically.

**Impact on the system**:
- **Load balancing**: Docker Swarm automatically distributes incoming requests across the two replicas, providing basic load balancing.
- **Database consistency matters**: With multiple web replicas all writing to the same PostgreSQL database, the shared database becomes essential. If we were still using in-memory SQLite, each replica would have its own separate database and users would see different data depending on which replica served their request.
- **Resource limits enforced**: The compose file also sets CPU (0.2) and memory (64M) limits per replica, which would not be applied in a simple manual `docker run` unless explicitly specified.
- **Restart policies**: The `on-failure` restart policy means crashed containers are automatically restarted, improving reliability compared to manual management.

## Q3. Inspect the database

The login credentials for the Adminer interface at `http://localhost:8080` can be found in the `docker-compose.yml` under the `db` service's environment variables:

| Field    | Value             |
|----------|-------------------|
| System   | PostgreSQL        |
| Server   | db                |
| Username | cs162_user        |
| Password | cs162_password    |
| Database | cs162             |

After logging in and navigating to the `expression` table, submitted calculations should be visible with their `id`, `text` (the expression string), `value` (the computed result), and `now` (the timestamp).

## Q4. Bigger picture

The system running on your computer consists of several containerized services communicating over a Docker virtual network (`webnet`):

```
 Browser (Host Machine)
   |
   |  Port 5162              Port 8080
   v                          v
+---------+              +---------+
|   Web   | (x2 replicas)|  Adminer|
|  Flask  |              | DB Admin|
+---------+              +---------+
     |                        |
     |     Docker network     |
     |      ("webnet")        |
     +----------+-------------+
                |
                v
          +-----------+
          |    db     |
          | PostgreSQL|
          | Port 5432 |
          +-----------+
```

**Components explained**:
- **Flask web app (`web`)**: A Python web server that accepts math expressions, evaluates them using a recursive descent parser, and stores results in the database. Runs in 2 replicas behind Docker Swarm's built-in load balancer.
- **PostgreSQL (`db`)**: A relational database management system (RDBMS) running in its own container. Stores all calculation history persistently. Unlike SQLite (which is file/memory-based and embedded), PostgreSQL is a full client-server database that multiple applications can connect to simultaneously.
- **Adminer (`adminer`)**: A lightweight, single-PHP-file web-based database management tool. Provides a GUI to inspect, query, and manage the PostgreSQL database. Accessible on port 8080.
- **Docker Swarm**: The orchestration mode of Docker that manages deploying and scaling the services defined in `docker-compose.yml`. It handles replica management, load balancing, restart policies, and resource limits.
- **webnet (overlay network)**: A virtual network created by Docker that allows the containers to communicate with each other by service name (e.g., the Flask app connects to the database using the hostname `db`).

**Key terminology**:
- **Docker**: A platform for running applications in isolated containers — lightweight, portable environments that package an app with all its dependencies.
- **Container**: A running instance of a Docker image; an isolated process with its own filesystem, network, and resource limits.
- **Docker Compose / `docker-compose.yml`**: A YAML file that defines multi-container applications — which services to run, how they connect, and their configuration.
- **Docker Stack**: A Swarm-mode command (`docker stack deploy`) that deploys a compose file as a set of services with orchestration features like replicas and rolling updates.
- **Replicas**: Multiple identical instances of a service, used for load distribution and redundancy.
- **RDBMS (Relational Database Management System)**: A database system (like PostgreSQL) that stores data in tables with rows and columns, supporting SQL queries.
- **Adminer**: A database administration tool (alternative to phpMyAdmin) that supports PostgreSQL, MySQL, SQLite, and others through a web browser interface.
- **`psycopg2`**: The most popular Python adapter for PostgreSQL, enabling Python applications to execute SQL commands against a Postgres database.
