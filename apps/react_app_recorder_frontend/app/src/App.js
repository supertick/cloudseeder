import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Button, Container, Typography, Box } from '@mui/material';
import Login from './pages/Login';
import Home from './pages/Home';
import { CssBaseline } from '@mui/material';
import useAuthStore from './store/authStore'; // Import Zustand store

function Navbar() {
  const { token, user, logout } = useAuthStore();

  const handleLogout = () => {
    logout(); // Clear token and user info
  };

  return (
    <AppBar position="static">
      <Toolbar>
        <Button color="inherit" component={Link} to="/">
          Home
        </Button>
        {!token ? (
          <Button color="inherit" component={Link} to="/login">
            Login
          </Button>
        ) : (
          <Box display="flex" alignItems="center" ml="auto">
            <Typography variant="body1" sx={{ marginRight: 2 }}>
              Welcome, {user?.full_name}
            </Typography>
            <Button color="inherit" onClick={handleLogout} component={Link} to="/login">
              Logout
            </Button>
          </Box>
        )}
      </Toolbar>
    </AppBar>
  );
}

function App() {
  return (
    <Router>
      <CssBaseline />
      <Navbar />
      <Container maxWidth="md">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
        </Routes>
      </Container>
    </Router>
  );
}

export default App;
