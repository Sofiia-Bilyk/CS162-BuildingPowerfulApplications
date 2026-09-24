import { useState, useEffect } from 'react';
import Column from '../components/Column';
import { fetchTasks, updateTask, deleteTask } from '../api';

function HomePage() {
  const [tasksByColumn, setTasksByColumn] = useState({});
  const [columns, setColumns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadTasks = async () => {
    try {
      setLoading(true);
      const data = await fetchTasks();
      setTasksByColumn(data.tasks);
      setColumns(data.columns);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const handleMoveTask = async (taskId, newColumn) => {
    try {
      await updateTask(taskId, { column: newColumn });
      // Reload tasks to get updated state
      loadTasks();
    } catch (err) {
      alert('Failed to move task: ' + err.message);
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      await deleteTask(taskId);
      // Reload tasks to get updated state
      loadTasks();
    } catch (err) {
      alert('Failed to delete task: ' + err.message);
    }
  };

  if (loading) {
    return (
      <main className="main">
        <div className="loading">Loading tasks...</div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="main">
        <div className="error">
          <p>Error: {error}</p>
          <button onClick={loadTasks}>Retry</button>
        </div>
      </main>
    );
  }

  return (
    <main className="main">
      <p className="board-title">Project: CS162 Tasks</p>
      <div className="columns">
        {columns.map(column => (
          <Column
            key={column.id}
            id={column.id}
            title={column.title}
            tasks={tasksByColumn[column.id] || []}
            columns={columns}
            onMoveTask={handleMoveTask}
            onDeleteTask={handleDeleteTask}
          />
        ))}
      </div>
    </main>
  );
}

export default HomePage;
