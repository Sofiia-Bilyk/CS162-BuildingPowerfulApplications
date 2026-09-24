### Output from the docker ps
CONTAINER ID   IMAGE                COMMAND           CREATED         STATUS         PORTS                            
             NAMES
22a060fd0a56   simple-cs162-flask   "python app.py"   3 seconds ago   Up 2 seconds   0.0.0.0:5162->5162/tcp, [::]:5162->5162/tcp   simple-cs162-instance


### Q1. Bigger picture

[ Web Browser ]
        ↓ HTTP request
[ Server (cloud / local machine) ]
        ↓
[ Docker ]
   └── [ Container ]
         ├── Flask App (backend logic)
         ├── Application Code
         └── Dependencies (Python, libraries)
                ↓
         [ Database (e.g., PostgreSQL, SQLite) ]
                ↑
        Data read/write

### Q2. Data persistence
No, the computation server does not persist data when it is stopped. This is because it runs inside a Docker container, and by default containers have ephemeral storage, so any data created inside the container is lost once the container is removed.

You can test this by:
1. Starting the container and creating some data.
2. Stopping and removing the container.
3. Starting a new container from the same image.
4. Observing that the previously created data is gone.


### Q3. Environment variables
Environment variables are key–value pairs stored outside your code that provide configuration. They allow you to separate sensitive or environment-specific data from your application logic.

