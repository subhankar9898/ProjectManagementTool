import React from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import ProjectDetailPage from './pages/ProjectDetailPage.jsx';

import App from './App.jsx';
import './index.css'; // We'll clean this up next

// Import your new pages
import LoginPage from './pages/LoginPage.jsx';
import RegisterPage from './pages/RegisterPage.jsx';
import DashboardPage from './pages/DashboardPage.jsx';

// Create the router configuration
const router = createBrowserRouter([
  {
    path: '/login',
    element: <LoginPage />,
  },
  {
    path: '/register',
    element: <RegisterPage />,
  },
  {
    path: '/',
    element: <ProtectedRoute />, // <-- Add this
    children: [
      {
        path: '/',
        element: <App />, // App is now INSIDE the protected route
        children: [
          {
            path: '/', // The default page (dashboard)
            element: <DashboardPage />,
          },
          {
            path: '/project/:id', // <-- ADD THIS WHOLE BLOCK
            element: <ProjectDetailPage />,
          },
        ]
        
      },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>
);