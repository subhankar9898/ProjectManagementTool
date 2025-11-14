import { Outlet } from 'react-router-dom';
import './App.css'; // We'll clean this up next

function App() {
  return (
    <div className="App">
      <header>
        {/* We can add a navigation bar here later */}
      </header>
      <main>
        {/* This Outlet component renders the current page */}
        <Outlet />
      </main>
    </div>
  );
}

export default App;