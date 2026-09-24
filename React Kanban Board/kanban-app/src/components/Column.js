import Task from './Task';

function Column({ id, title, tasks, onMoveTask, onDeleteTask, columns }) {
  return (
    <div className={`column ${id}`}>
      <h2 className="column-header">
        {title}
        <span className="task-count">{tasks.length}</span>
      </h2>
      <div className="column-tasks">
        {tasks.map(task => (
          <Task
            key={task.id}
            task={task}
            currentColumn={id}
            columns={columns}
            onMoveTask={onMoveTask}
            onDeleteTask={onDeleteTask}
          />
        ))}
      </div>
    </div>
  );
}

export default Column;
