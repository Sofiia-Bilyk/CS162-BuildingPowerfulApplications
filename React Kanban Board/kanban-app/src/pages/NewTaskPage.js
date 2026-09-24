import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createTask } from '../api';

function NewTaskPage() {
  const navigate = useNavigate();
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Get today's date in YYYY-MM-DD format for min attribute
  const today = new Date().toISOString().split('T')[0];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await createTask({
        description,
        due_date: dueDate || null,
      });
      navigate('/');
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <main className="main">
      <div className="task-form-container">
        <h2 className="task-form-title">Add New Task</h2>
        <p className="task-form-subtitle">Create a new task for your Kanban board</p>

        {error && <div className="form-error">{error}</div>}

        <form className="task-form" onSubmit={handleSubmit}>
          <div className="form-group form-group-full">
            <label htmlFor="task-description">Task Description</label>
            <textarea
              id="task-description"
              name="task-description"
              placeholder="Enter a short description of the task..."
              required
              rows="3"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="due-date">Due Date (optional)</label>
            <input
              type="date"
              id="due-date"
              name="due-date"
              min={today}
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              disabled={loading}
            />
          </div>

          <div className="form-group form-group-submit">
            <button type="submit" disabled={loading}>
              {loading ? 'Adding...' : 'Add Task'}
            </button>
          </div>
        </form>
      </div>
    </main>
  );
}

export default NewTaskPage;
