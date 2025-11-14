import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api'; // Import your api client


function DashboardPage() {
  // State for storing the list of projects
  const [metrics, setMetrics] = useState(null);
  const [projects, setProjects] = useState([]);
  
  // State for the new project form
  const [projectName, setProjectName] = useState('');
  const [projectDesc, setProjectDesc] = useState('');
  const [error, setError] = useState(null);

  const navigate = useNavigate();

  // This function fetches projects from the backend
  const fetchProjects = async () => {
    try {
      // Get the token from localStorage
      const token = localStorage.getItem('access_token');
      
      // Send the GET request with the Authorization header
      const response = await api.get('/projects', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      setProjects(response.data.projects); // Store projects in state
    } catch (err) {
      console.error('Error fetching projects:', err);
      setError('Failed to fetch projects.');
    }
  };

  const fetchMetrics = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await api.get('/dashboard-metrics', {
        headers: { Authorization: `Bearer ${token}` },
      });
      setMetrics(response.data);
    } catch (err) {
      console.error('Error fetching metrics:', err);
    }
  };

  // useEffect hook runs once when the component loads
  useEffect(() => {
    fetchProjects();
    fetchMetrics(); 
  }, []);

  // Handle new project form submission
  // Handle new project form submission
  const handleCreateProject = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      const token = localStorage.getItem('access_token');
      
      // This is the corrected block
      await api.post('/projects',
        { // The data to send
          name: projectName,
          description: projectDesc,
        },
        { // The config with the auth header
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      ); // <-- The closing parenthesis was missing

      // Reset form and refresh project list
      setProjectName('');
      setProjectDesc('');
      fetchProjects(); 
      fetchMetrics();// Re-fetch projects to show the new one
      
    } catch (err) {
      console.error('Error creating project:', err);
      setError(err.response?.data?.message || 'Failed to create project.');
    }
  };

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    navigate('/login'); // Redirect to login page
  };

  return (
    <div>
      <button onClick={handleLogout} style={{ float: 'right' }}>
        Logout
      </button>

      <h1>Your Projects</h1>

      {/* --- DASHBOARD METRICS --- */}
{metrics && (
  <div className="metrics-summary" style={{ display: 'flex', gap: '20px', margin: '20px 0' }}>
    <div style={{ padding: '10px', border: '1px solid #555', color: metrics.tasks_overdue > 0 ? 'red' : 'inherit' }}>
      <strong>Tasks Overdue</strong>
      <p style={{ fontSize: '2em', margin: 0 }}>{metrics.tasks_overdue}</p>
    </div>
    <div style={{ padding: '10px', border: '1px solid #555' }}>
      <strong>Total Projects</strong>
      <p style={{ fontSize: '2em', margin: 0 }}>{metrics.total_projects}</p>
    </div>
    <div style={{ padding: '10px', border: '1px solid #555' }}>
      <strong>Total Tasks</strong>
      <p style={{ fontSize: '2em', margin: 0 }}>{metrics.total_tasks}</p>
    </div>
    <div style={{ padding: '10px', border: '1px solid #555' }}>
      <strong>Tasks By Status</strong>
      <p style={{ margin: 0 }}>
        To Do: {metrics.tasks_by_status['To Do']} | 
        In Progress: {metrics.tasks_by_status['In Progress']} | 
        Done: {metrics.tasks_by_status['Done']}
      </p>
    </div>
  </div>
)}
<hr />
{/* --- END METRICS --- */}
      
      {/* List of existing projects */}
      <div className="project-list">
        {projects.length === 0 ? (
          <p>You have no projects. Create one below!</p>
        ) : (
          <ul>
            {projects.map((project) => (
              <li key={project.id}>
              <Link to={`/project/${project.id}`}>
                <strong>{project.name}</strong>
              </Link>
              : {project.description}
            </li>
            ))}
          </ul>
        )}
      </div>

      <hr />

      {/* Form to create a new project */}
      <h2>Create New Project</h2>
      <form onSubmit={handleCreateProject}>
        <div>
          <label htmlFor="projectName">Project Name:</label>
          <input
            type="text"
            id="projectName"
            value={projectName}
            onChange={(e) => setProjectName(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="projectDesc">Description:</label>
          <textarea
            id="projectDesc"
            value={projectDesc}
            onChange={(e) => setProjectDesc(e.target.value)}
          />
        </div>
        <button type="submit">Create Project</button>
      </form>
      
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default DashboardPage;