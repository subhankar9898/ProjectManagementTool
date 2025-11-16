import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api'; // Import your api client

function RegisterPage() {
  // State for the form inputs
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState('Developer'); // Default role
  const [error, setError] = useState(null);

  // useNavigate hook to redirect
  const navigate = useNavigate();

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent default form refresh
    setError(null); // Clear previous errors

    try {
      // Send the register request to the backend
      await api.post('/register', {
        email: email,
        password: password,
        full_name: fullName,
        role: role,
      });

      // If registration is successful, redirect to the login page
      navigate('/login');

    } catch (err) {
      // If there's an error
      console.error('Registration error', err);
      if (err.response && err.response.data) {
        setError(err.response.data.message);
      } else {
        setError('Registration failed. Please try again.');
      }
    }
  };

  return (
    <div>
      <h1>Register Page</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="fullName">Full Name:</label>
          <input
            type="text"
            id="fullName"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <div>
          <label htmlFor="role">Role:</label>
          <select value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="Developer">Developer</option>
            <option value="Manager">Manager</option>
            <option value="Admin">Admin</option>
          </select>
        </div>
        <button type="submit">Register</button>
      </form>
      
      {/* Show an error message if it fails */}
      {error && <p style={{ color: 'red' }}>{error}</p>}
      
      <p>
        Already have an account? <Link to="/login">Login here</Link>
      </p>
    </div>
  );
}

export default RegisterPage;