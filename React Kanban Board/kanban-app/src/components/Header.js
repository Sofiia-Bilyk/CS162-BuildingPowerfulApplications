import { NavLink } from 'react-router-dom';

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <h1 className="header-title">Kanban Board</h1>
        <nav className="header-nav">
          <NavLink to="/" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'} end>
            Board
          </NavLink>
          <NavLink to="/new-task" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
            Add Task
          </NavLink>
        </nav>
      </div>
    </header>
  );
}

export default Header;
