import { useState, useEffect, useCallback } from 'react'; // <-- 1. ADD useCallback
import { useParams, Link } from 'react-router-dom';
import api from '../api';

function ProjectDetailPage() {
  const [tasks, setTasks] = useState([]);
  const [error, setError] = useState(null);
  const { id } = useParams();

  const [stories, setStories] = useState([]);
const [aiDescription, setAiDescription] = useState('');

    // State for the new task form
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [assigneeId, setAssigneeId] = useState('');
    const [deadline, setDeadline] = useState('');
    const [newMemberId, setNewMemberId] = useState('');

  // 2. WRAP your function in useCallback
  const fetchTasks = useCallback(async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await api.get(`/projects/${id}/tasks`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setTasks(response.data.tasks);
    } catch (err) {
      console.error('Error fetching tasks:', err);
      setError(err.response?.data?.message || 'Failed to fetch tasks.');
    }
  }, [id]); // 3. ADD 'id' as the dependency for useCallback
  const fetchStories = useCallback(async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await api.get(`/projects/${id}/stories`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setStories(response.data);
    } catch (err) {
      console.error('Error fetching stories:', err);
    }
  }, [id]);

  // Handle new task creation
const handleCreateTask = async (e) => {
    e.preventDefault();
    setError(null);
  
    try {
      const token = localStorage.getItem('access_token');
      await api.post(`/projects/${id}/tasks`, 
        {
          title: title,
          description: description,
          assignee_id: Number(assigneeId) || null,
          deadline: deadline || null, // Send null if empty
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
  
      // Clear form and refresh tasks
      setTitle('');
      setDescription('');
      setAssigneeId('');
      setDeadline('');
      fetchTasks(); // Refresh the task list
  
    } catch (err) {
      console.error('Error creating task:', err);
      setError(err.response?.data?.message || 'Failed to create task.');
    }
  };

  const handleAddMember = async (e) => {
    e.preventDefault();
    setError(null);
    try {
      const token = localStorage.getItem('access_token');
      await api.post(`/projects/${id}/members`, 
        { user_id: newMemberId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      alert("Member added successfully!");
      setNewMemberId('');
    } catch (err ){
      console.error('Error adding member:', err);
      setError(err.response?.data?.message || 'Failed to add member.');
    }
  };

  // Handle task status update
  const handleUpdateStatus = async (taskId, newStatus) => {
    setError(null);
    try {
      const token = localStorage.getItem('access_token');
      await api.patch(`/tasks/${taskId}/status`, 
        {
          status: newStatus,
        },
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      
      // Refresh the task list to show the change
      fetchTasks();
      
    } catch (err) {
      console.error('Error updating status:', err);
      setError(err.response?.data?.message || 'Failed to update status.');
    }
  };

  const handleGenerateStories = async (e) => {
    e.preventDefault();
    setError(null);
    if (!aiDescription) {
      setError('Please enter a project description.');
      return;
    }
    try {
      const token = localStorage.getItem('access_token');
      await api.post(`/projects/${id}/generate-stories`, 
        { projectDescription: aiDescription },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setAiDescription(''); // Clear the text area
      fetchStories(); // Refresh the stories list
    } catch (err) {
      console.error('Error generating stories:', err);
      setError(err.response?.data?.message || 'Failed to generate stories.');
    }
  };
  // Run fetchTasks when the component loads
  useEffect(() => {
    fetchTasks();
    fetchStories(); // <-- ADD THIS
  }, [fetchTasks, fetchStories]); // <-- ADD fetchStories// 4. This is now safe because fetchTasks is "memoized"

  return (
    <div>
      <Link to="/">&larr; Back to Dashboard</Link>
      {/* --- ADD MEMBER FORM --- */}
      <form onSubmit={handleAddMember} style={{ marginBottom: '20px' }}>
        <label>Add Member (User ID): </label>
        <input 
          type="number" 
          value={newMemberId} 
          onChange={(e) => setNewMemberId(e.target.value)} 
          placeholder="e.g. 2"
          style={{ width: '60px', marginRight: '10px' }}
        />
        <button type="submit">Add</button>
      </form>
      <hr />
      <h1>Project {id} Tasks</h1>
      {/* --- NEW TASK FORM --- */}
<form onSubmit={handleCreateTask} style={{ margin: '20px 0', padding: '10px', border: '1px solid #555' }}>
  <h3>Create New Task</h3>
  <div>
    <label>Title: </label>
    <input 
      type="text" 
      value={title} 
      onChange={(e) => setTitle(e.target.value)} 
      required 
    />
  </div>
  <div>
    <label>Description: </label>
    <textarea 
      value={description} 
      onChange={(e) => setDescription(e.target.value)} 
    />
  </div>
  <div>
    <label>Assignee ID: </label>
    <input 
      type="number" 
      placeholder="(e.g., 2 for dev@test.com)"
      value={assigneeId} 
      onChange={(e) => setAssigneeId(e.target.value)} 
    />
  </div>
  <div>
        <label>Deadline: </label>
        <input 
          type="date" 
          value={deadline} 
          onChange={(e) => setDeadline(e.target.value)} 
        />
      </div>
  <button type="submit">Create Task</button>
</form>
{/* --- END NEW TASK FORM --- */}

{error && <p style={{ color: 'red' }}>{error}</p>}

{/* ... your task list div is below this ... */}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {/* We will make these into columns next */}
      <div className="task-list">
      <h3>To Do</h3>
        {tasks.filter(t => t.status === 'To Do').map(task => (
          <div key={task.id} style={{ border: '1px solid #444', padding: '5px', margin: '5px' }}>
            <strong>{task.title}</strong>
            <p>{task.description}</p>
            <small>Assigned to: {task.assignee_name || 'unassigned'}</small>
            <div>
              <select 
                value={task.status} 
                onChange={(e) => handleUpdateStatus(task.id, e.target.value)}
              >
                <option value="To Do">To Do</option>
                <option value="In Progress">In Progress</option>
                <option value="Done">Done</option>
              </select>
            </div>
          </div>
        ))}

<h3>In Progress</h3>
        {tasks.filter(t => t.status === 'In Progress').map(task => (
          <div key={task.id} style={{ border: '1px solid #444', padding: '5px', margin: '5px' }}>
            <strong>{task.title}</strong>
            <p>{task.description}</p>
            <small>Assigned to: {task.assignee_name || 'unassigned'}</small>
            <div>
              <select 
                value={task.status} 
                onChange={(e) => handleUpdateStatus(task.id, e.target.value)}
              >
                <option value="To Do">To Do</option>
                <option value="In Progress">In Progress</option>
                <option value="Done">Done</option>
              </select>
            </div>
          </div>
        ))}

<h3>Done</h3>
        {tasks.filter(t => t.status === 'Done').map(task => (
          <div key={task.id} style={{ border: '1px solid #444', padding: '5px', margin: '5px' }}>
            <strong>{task.title}</strong>
            <p>{task.description}</p>
            <small>Assigned to: {task.assignee_name || 'unassigned'}</small>
            <div>
              <select 
                value={task.status} 
                onChange={(e) => handleUpdateStatus(task.id, e.target.value)}
              >
                <option value="To Do">To Do</option>
                <option value="In Progress">In Progress</option>
                <option value="Done">Done</option>
              </select>
            </div>
          </div>
        ))}
      </div>
    
    <hr />

    {/* --- AI STORY GENERATOR --- */}
    <div>
      <h2>AI User Story Generator</h2>
      <form onSubmit={handleGenerateStories} style={{ margin: '10px 0', padding: '10px', border: '1px solid #555' }}>
        <div>
          <label>Enter Project Description:</label>
          <textarea 
            value={aiDescription}
            onChange={(e) => setAiDescription(e.target.value)}
            placeholder="e.g., An ecommerce website where customers can browse products..."
            style={{ width: '90%', minHeight: '80px', margin: '10px 0' }}
          />
        </div>
        <button type="submit">Generate Stories</button>
      </form>

      <h3>Generated Stories</h3>
      {stories.length === 0 ? (
        <p>No user stories generated yet.</p>
      ) : (
        <ul style={{ listStyle: 'none', padding: 0 }}>
          {stories.map(story => (
            <li key={story.id} style={{ border: '1px solid #444', padding: '10px', margin: '5px' }}>
              {story.story_text}
            </li>
          ))}
        </ul>
      )}
    </div>
    </div>
  );
}

export default ProjectDetailPage;