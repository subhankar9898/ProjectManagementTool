import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api'; // Import your api client

function LoginPage() {
  // State for the form inputs
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState(null);

  // useNavigate hook to redirect
  const navigate = useNavigate();

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent default form refresh
    setError(null); // Clear previous errors

    try {
      // Send the login request to the backend
      const response = await api.post('/login', {
        email: email,
        password: password,
      });

      // If login is successful
      if (response.data.access_token) {
        // Store the token in localStorage
        localStorage.setItem('access_token', response.data.access_token);
        
        // Store user info (optional, but helpful)
        localStorage.setItem('user', JSON.stringify(response.data.user));

        // Navigate to the dashboard
        navigate('/');
      }
    } catch (err) {
      // If there's an error
      console.error('Login error', err);
      if (err.response && err.response.data) {
        setError(err.response.data.message);
      } else {
        setError('Login failed. Please try again.');
      }
    }
  };

  return (
    <div>
      <h1>Login Page</h1>
      <form onSubmit={handleSubmit}>
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
        <button type="submit">Login</button>
      </form>
      {/* Show an error message if login fails */}
      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default LoginPage;