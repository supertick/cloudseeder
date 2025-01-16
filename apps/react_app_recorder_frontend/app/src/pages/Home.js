import React from 'react';
import { Typography, Box } from '@mui/material';

function Home() {
  return (
    <Box
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
    >
      <Typography variant="h3" component="h1" gutterBottom>
        Welcome to Scribble 2.0
      </Typography>
      <Typography>
        This is the home page. Navigate to the login page to access your account.
      </Typography>
    </Box>
  );
}

export default Home;
