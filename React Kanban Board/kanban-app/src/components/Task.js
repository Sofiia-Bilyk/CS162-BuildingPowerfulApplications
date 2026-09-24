function Task({ task, currentColumn, columns, onMoveTask, onDeleteTask }) {
  const formatDate = (dateStr) => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const handleMove = (newColumn) => {
    onMoveTask(task.id, newColumn);
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      onDeleteTask(task.id);
    }
  };

  // Get other columns for move buttons
  const otherColumns = columns.filter(col => col.id !== currentColumn);

  return (
    <div className="task">
      <div className="task-content">
        <div className="task-description">{task.description}</div>
        {task.due_date && (
          <div className="task-meta">Due: {formatDate(task.due_date)}</div>
        )}
      </div>
      <div className="task-actions">
        <div className="move-buttons">
          {otherColumns.map(col => (
            <button
              key={col.id}
              className="move-btn"
              onClick={() => handleMove(col.id)}
              title={`Move to ${col.title}`}
            >
              {col.title}
            </button>
          ))}
        </div>
        <button className="delete-btn" onClick={handleDelete} title="Delete task">
          Delete
        </button>
      </div>
    </div>
  );
}

export default Task;
