"""
app.py - Kanban Board REST API

A simple REST API for managing Kanban board tasks.
Returns JSON responses for all endpoints.
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

# =============================================================================
# APP CONFIGURATION
# =============================================================================

app = Flask(__name__)

# Enable CORS for React frontend
CORS(app)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kanban.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

db = SQLAlchemy(app)

# =============================================================================
# DATABASE MODEL
# =============================================================================

class Task(db.Model):
    """Task Model - Represents a single task on the Kanban board"""

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    column = db.Column(db.String(50), nullable=False, default='todo')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert task to dictionary for JSON response"""
        return {
            'id': self.id,
            'description': self.description,
            'due_date': self.due_date.strftime('%Y-%m-%d') if self.due_date else None,
            'column': self.column,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# =============================================================================
# API ENDPOINTS
# =============================================================================

VALID_COLUMNS = ['backlog', 'todo', 'progress', 'review', 'done']


@app.route('/')
def index():
    """Root route - API info"""
    return jsonify({
        'message': 'Kanban Board API',
        'endpoints': {
            'GET /api/tasks': 'Get all tasks',
            'POST /api/tasks': 'Create a task',
            'PUT /api/tasks/<id>': 'Update a task',
            'DELETE /api/tasks/<id>': 'Delete a task'
        }
    })


@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """
    GET /api/tasks
    Returns all tasks organized by column
    """
    all_tasks = Task.query.order_by(Task.created_at.desc()).all()

    # Organize tasks by column
    tasks_by_column = {col: [] for col in VALID_COLUMNS}
    for task in all_tasks:
        if task.column in tasks_by_column:
            tasks_by_column[task.column].append(task.to_dict())

    return jsonify({
        'tasks': tasks_by_column,
        'columns': [
            {'id': 'backlog', 'title': 'Backlog'},
            {'id': 'todo', 'title': 'To Do'},
            {'id': 'progress', 'title': 'In Progress'},
            {'id': 'review', 'title': 'Review'},
            {'id': 'done', 'title': 'Done'}
        ]
    })


@app.route('/api/tasks', methods=['POST'])
def create_task():
    """
    POST /api/tasks
    Create a new task

    Request body:
    {
        "description": "Task description",
        "due_date": "YYYY-MM-DD" (optional),
        "column": "todo" (optional, defaults to "todo")
    }
    """
    data = request.get_json()

    if not data or not data.get('description'):
        return jsonify({'error': 'Description is required'}), 400

    description = data.get('description')
    due_date_str = data.get('due_date')
    column = data.get('column', 'todo')

    # Validate column
    if column not in VALID_COLUMNS:
        return jsonify({'error': f'Invalid column. Must be one of: {VALID_COLUMNS}'}), 400

    # Parse due date if provided
    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

    # Create new task
    new_task = Task(
        description=description,
        due_date=due_date,
        column=column
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify({'task': new_task.to_dict()}), 201


@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """
    PUT /api/tasks/<id>
    Update a task (move to different column, update description, etc.)

    Request body:
    {
        "column": "progress" (optional),
        "description": "Updated description" (optional),
        "due_date": "YYYY-MM-DD" (optional)
    }
    """
    task = Task.query.get(task_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    # Update column if provided
    if 'column' in data:
        if data['column'] not in VALID_COLUMNS:
            return jsonify({'error': f'Invalid column. Must be one of: {VALID_COLUMNS}'}), 400
        task.column = data['column']

    # Update description if provided
    if 'description' in data:
        if not data['description']:
            return jsonify({'error': 'Description cannot be empty'}), 400
        task.description = data['description']

    # Update due date if provided
    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        else:
            task.due_date = None

    db.session.commit()

    return jsonify({'task': task.to_dict()})


@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """
    DELETE /api/tasks/<id>
    Delete a task
    """
    task = Task.query.get(task_id)

    if not task:
        return jsonify({'error': 'Task not found'}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({'message': 'Task deleted successfully'})


# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def init_db():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
