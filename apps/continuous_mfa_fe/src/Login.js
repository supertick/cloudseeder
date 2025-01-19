import React, { useState } from "react";
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Grid,
  Link,
  Paper,
  Alert,
} from "@mui/material";
import {jwtDecode } from "jwt-decode"; // Import jwt-decode
import { useUser } from "./UserContext"; // Import useUser
import apiClient from "./utils/apiClient";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState(""); // State to manage error messages

  const { setUserInfo } = useUser(); // Access setUserInfo from UserContext

  const handleLogin = async (event) => {
    event.preventDefault();

    try {
      const response = await apiClient.postForm("/login", {
        email: email,
        username: email,
        password: password,
      });

      if (response && response.access_token) {
        // Decode the JWT to extract the user information
        const decodedToken = jwtDecode(response.access_token);
        const user = decodedToken.user;

        // Update the user context with the decoded user information
        setUserInfo(user);

        // Clear any previous error messages
        setErrorMessage("");

        // Optionally, redirect to another page or perform additional actions
        console.log("User logged in successfully:", user);
      }
    } catch (error) {
      // Set a user-friendly error message
      setErrorMessage("Invalid email or password. Please try again.");
      console.error("Login failed:", error);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        backgroundColor: "#b3e5fc",
        backgroundImage: "url(/freeze_data.png)",
        backgroundSize: "cover",
        backgroundPosition: "center",
        paddingTop: "50px",
      }}
    >
      <Container component="main" maxWidth="xs">
        <Paper
          style={{
            margin: "20px auto",
            borderRadius: "16px",
            overflow: "hidden", // Ensure the header styles don't bleed
            boxShadow: "0 4px 10px rgba(0, 0, 0, 0.1)",
          }}
          elevation={10}
        >
          {/* Dialog Header */}
          <Box
            style={{
              backgroundColor: "rgb(47, 63, 92)", // Header background
              color: "white", // Header text color
              padding: "16px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center", // Center the content horizontally
              gap: "10px", // Space between the logo and text
            }}
          >
            <img
              src="/Metalytics-Logo_light.webp"
              alt="Metalytics Logo"
              style={{
                height: "40px", // Adjust as needed
              }}
            />
            <Typography component="h1" variant="h6">
              Continuous MFA Login
            </Typography>
          </Box>

          {/* Form */}
          <Box
            style={{
              padding: "20px",
              backgroundColor: "rgb(252, 254, 255)", // Background color for the form
            }}
          >
            {errorMessage && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {errorMessage}
              </Alert>
            )}
            <Box component="form" onSubmit={handleLogin} noValidate>
              <TextField
                margin="normal"
                required
                fullWidth
                id="email"
                label="Email Address"
                name="email"
                autoComplete="email"
                autoFocus
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
              <TextField
                margin="normal"
                required
                fullWidth
                name="password"
                label="Password"
                type="password"
                id="password"
                autoComplete="current-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2, backgroundColor: "rgb(47, 63, 92)" }}
              >
                Login
              </Button>
              <Grid container>
                <Grid item xs>
                  <Link href="#" variant="body2">
                    Forgot password?
                  </Link>
                </Grid>
                <Grid item>
                  <Link href="#" variant="body2">
                    {"Don't have an account? Sign Up"}
                  </Link>
                </Grid>
              </Grid>
            </Box>
          </Box>
        </Paper>
      </Container>
    </div>
  );
};

export default Login;
