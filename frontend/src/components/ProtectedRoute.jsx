import { Navigate, Outlet } from 'react-router-dom';

function ProtectedRoute() {
  // Check if the access token exists in localStorage
  const token = localStorage.getItem('access_token');

  // If token exists, show the page (using <Outlet />)
  // If not, redirect to the /login page
  return token ? <Outlet /> : <Navigate to="/login" replace />;
}

export default ProtectedRoute;