import React, { useState } from 'react';
import { TextField, Button, Typography, Box } from '@mui/material';
import axios from 'axios';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

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
      const token = response.data.access_token;

      alert('Login successful!');
      console.log('Token:', token);

      // Save token to localStorage or context (depending on your app needs)
      localStorage.setItem('access_token', token);

    } catch (err) {
      console.error(err.response ? err.response.data : err.message);
      setError('Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
    >
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
    </Box>
  );
}

export default Login;
