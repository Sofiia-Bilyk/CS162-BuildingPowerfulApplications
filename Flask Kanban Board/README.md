# Kanban Board - Flask Application

A simple Kanban board with database persistence built using Flask and SQLAlchemy.

## Technologies Used

- **Flask** - Python web framework
- **Flask-SQLAlchemy** - Database ORM for Flask
- **SQLite** - Lightweight database (stored in `kanban.db`)
- **Jinja2** - Template engine (built into Flask)

## Project Structure

```
KanbanApp/
├── app.py              # Main Flask application (routes, models, config)
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html      # Main Kanban board template
└── instance/
    └── kanban.db       # SQLite database (created on first run)
```

## Setup & Running

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open in browser**: http://127.0.0.1:5000

## Features

- Add new tasks (created in "To Do" column)
- Move tasks between columns (Backlog, To Do, In Progress, Review, Done)
- Delete tasks
- Due date support
- Data persists in SQLite database
