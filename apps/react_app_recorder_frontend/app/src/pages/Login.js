import React, { useState } from 'react';
import {
  TextField,
  Button,
  Typography,
  Box,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
} from '@mui/material';
import { Add, Edit, Delete } from '@mui/icons-material';
import axios from 'axios';
import useAuthStore from '../store/authStore'; // Import the store

function LoginAndUsers() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [users, setUsers] = useState([]);
  const [editingUser, setEditingUser] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newUser, setNewUser] = useState({ id: '', full_name: '', email: '', roles: [] });

  // Zustand store hooks
  const { token, setToken, user, setUser, logout } = useAuthStore();

  // Handle Login
  const handleLogin = async () => {
    setLoading(true);
    setError('');

    const url = 'http://localhost:8000/token';
    const headers = {
      'Accept': 'application/json',
      'Content-Type': 'application/x-www-form-urlencoded',
    };

    const body = new URLSearchParams({
      grant_type: 'password',
      username: email,
      password: password,
      scope: '',
      client_id: 'string',
      client_secret: 'string',
    });

    try {
      const response = await axios.post(url, body, { headers });
      const accessToken = response.data.access_token;

      // Store the token in Zustand
      setToken(accessToken);

      // Simulating user data (replace with real user data if available)
      setUser({ email });

      await fetchUsers(accessToken);
    } catch (err) {
      console.error(err.response ? err.response.data : err.message);
      setError('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  // Fetch users
  const fetchUsers = async (accessToken) => {
    const url = 'http://localhost:8000/v1/users';
    const headers = {
      'Accept': 'application/json',
      'Authorization': `Bearer ${accessToken}`,
    };

    try {
      const response = await axios.get(url, { headers });
      setUsers(response.data);
    } catch (err) {
      console.error(err.response ? err.response.data : err.message);
      setError('Failed to fetch users');
    }
  };

  // Handle Logout
  const handleLogout = () => {
    logout(); // Clear token and user from Zustand store
    setUsers([]); // Clear user list
  };

  return (
    <Box
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
    >
      {!token ? (
        <>
          <Typography variant="h4" component="h1" gutterBottom>
            Login
          </Typography>
          {error && (
            <Typography color="error" gutterBottom>
              {error}
            </Typography>
          )}
          <TextField
            label="Email"
            variant="outlined"
            fullWidth
            margin="normal"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <TextField
            label="Password"
            type="password"
            variant="outlined"
            fullWidth
            margin="normal"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <Button
            variant="contained"
            color="primary"
            onClick={handleLogin}
            disabled={loading}
            sx={{ mt: 2 }}
          >
            {loading ? 'Logging in...' : 'Login'}
          </Button>
        </>
      ) : (
        <>
          <Typography variant="h4" component="h1" gutterBottom>
            Welcome, {user?.email}
          </Typography>
    
          <Typography variant="h4" component="h1" gutterBottom>
            User List
          </Typography>
          {error && (
            <Typography color="error" gutterBottom>
              {error}
            </Typography>
          )}
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Full Name</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Roles</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.id}</TableCell>
                  <TableCell>{user.full_name}</TableCell>
                  <TableCell>{user.email}</TableCell>
                  <TableCell>{user.roles.join(', ')}</TableCell>
                  <TableCell>
                    <IconButton onClick={() => console.log('Edit User', user)}>
                      <Edit />
                    </IconButton>
                    <IconButton onClick={() => console.log('Delete User', user)}>
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </>
      )}
    </Box>
  );
}

export default LoginAndUsers;
