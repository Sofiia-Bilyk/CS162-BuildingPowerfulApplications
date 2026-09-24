"""
app.py - Main Flask Application

This is the entry point for the Kanban Board Flask application.
It initializes the Flask app, configures the database, and registers routes.

Technologies used:
- Flask: Web framework for Python
- SQLAlchemy: ORM for database operations
- Jinja2: Template engine (built into Flask)
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# =============================================================================
# APP CONFIGURATION
# =============================================================================

# Create the Flask application instance
app = Flask(__name__)

# Configure the SQLite database
# SQLite is a lightweight database that stores data in a single file
# This is perfect for development and small applications
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///kanban.db'

# Disable modification tracking to save resources
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Secret key for session management (needed for flash messages, etc.)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'

# Initialize SQLAlchemy with our Flask app
# This creates the 'db' object we'll use to interact with the database
db = SQLAlchemy(app)

# =============================================================================
# DATABASE MODEL
# =============================================================================

class Task(db.Model):
    """
    Task Model - Represents a single task on the Kanban board

    This model defines the structure of the 'task' table in our database.
    Each task has:
    - id: Unique identifier (auto-generated)
    - description: The task text/content
    - due_date: Optional due date for the task
    - column: Which Kanban column the task belongs to
    - created_at: Timestamp when the task was created
    """

    # Primary key - unique identifier for each task
    id = db.Column(db.Integer, primary_key=True)

    # Task description - required field, max 500 characters
    description = db.Column(db.String(500), nullable=False)

    # Due date - optional, stored as a Date type
    due_date = db.Column(db.Date, nullable=True)

    # Column name - which Kanban column this task is in
    # Default is 'todo' as per requirements (tasks created in "To Do" column)
    # Possible values: 'backlog', 'todo', 'progress', 'review', 'done'
    column = db.Column(db.String(50), nullable=False, default='todo')

    # Timestamp when task was created - auto-set to current time
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        """String representation of the Task for debugging"""
        return f'<Task {self.id}: {self.description[:30]}...>'

    def to_dict(self):
        """
        Convert task to dictionary format
        Useful for JSON API responses
        """
        return {
            'id': self.id,
            'description': self.description,
            'due_date': self.due_date.strftime('%Y-%m-%d') if self.due_date else None,
            'column': self.column,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

# =============================================================================
# ROUTES - WEB PAGES
# =============================================================================

@app.route('/')
def index():
    """
    Main page route - displays the Kanban board

    This route:
    1. Fetches all tasks from the database
    2. Organizes them by column
    3. Renders the main template with the organized tasks
    """

    # Query all tasks from the database, ordered by creation date
    all_tasks = Task.query.order_by(Task.created_at.desc()).all()

    # Organize tasks by column for easier template rendering
    # This creates a dictionary where keys are column names
    # and values are lists of tasks in that column
    tasks_by_column = {
        'backlog': [],
        'todo': [],
        'progress': [],
        'review': [],
        'done': []
    }

    # Sort each task into its respective column
    for task in all_tasks:
        if task.column in tasks_by_column:
            tasks_by_column[task.column].append(task)

    # Render the template and pass the organized tasks
    return render_template('index.html', tasks=tasks_by_column)

@app.route('/add_task', methods=['POST'])
def add_task():
    """
    Add a new task to the board

    This route handles the form submission from the "Add New Task" form.
    Tasks are always created in the "To Do" column as per requirements.

    Expected form data:
    - task-description: The task text (required)
    - due-date: The due date in YYYY-MM-DD format (optional)
    """

    # Get the task description from the form
    description = request.form.get('task-description')

    # Get the due date (optional)
    due_date_str = request.form.get('due-date')

    # Validate that description is provided
    if not description:
        # If no description, redirect back to home
        return redirect(url_for('index'))

    # Parse the due date if provided
    due_date = None
    if due_date_str:
        try:
            # Convert string to Python date object
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            # If date parsing fails, leave it as None
            pass

    # Create a new Task object
    # Note: column defaults to 'todo' as defined in the model
    new_task = Task(
        description=description,
        due_date=due_date
    )

    # Add the new task to the database session
    db.session.add(new_task)

    # Commit the session to save changes to the database
    db.session.commit()

    # Redirect back to the main page to see the new task
    return redirect(url_for('index'))

@app.route('/move_task/<int:task_id>', methods=['POST'])
def move_task(task_id):
    """
    Move a task to a different column

    This route handles moving tasks between Kanban columns.
    It receives the task ID in the URL and the new column in the form data.

    Args:
        task_id: The ID of the task to move (from URL)

    Expected form/JSON data:
        - column: The target column name
    """

    # Find the task by ID, or return 404 if not found
    task = Task.query.get_or_404(task_id)

    # Get the new column from request
    # Support both form data and JSON for flexibility
    if request.is_json:
        new_column = request.json.get('column')
    else:
        new_column = request.form.get('column')

    # List of valid column names
    valid_columns = ['backlog', 'todo', 'progress', 'review', 'done']

    # Validate the new column
    if new_column in valid_columns:
        # Update the task's column
        task.column = new_column

        # Save changes to database
        db.session.commit()

    # Check if this is an AJAX request
    if request.is_json:
        # Return JSON response for AJAX requests
        return jsonify({'success': True, 'task': task.to_dict()})

    # Redirect back to main page for regular form submissions
    return redirect(url_for('index'))

@app.route('/delete_task/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    """
    Delete a task from the board

    This route removes a task from the database permanently.

    Args:
        task_id: The ID of the task to delete (from URL)
    """

    # Find the task by ID, or return 404 if not found
    task = Task.query.get_or_404(task_id)

    # Remove the task from the database
    db.session.delete(task)

    # Commit the changes
    db.session.commit()

    # Check if this is an AJAX request
    if request.is_json:
        return jsonify({'success': True})

    # Redirect back to main page
    return redirect(url_for('index'))

# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

def init_db():
    """
    Initialize the database

    This function creates all database tables based on our models.
    It should be called once when setting up the application.
    """
    with app.app_context():
        # Create all tables defined by our models
        db.create_all()
        print("Database initialized successfully!")

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    # Initialize the database (creates tables if they don't exist)
    init_db()

    # Run the Flask development server
    # debug=True enables auto-reload and detailed error pages
    # Note: Set debug=False in production!
    app.run(debug=True)
