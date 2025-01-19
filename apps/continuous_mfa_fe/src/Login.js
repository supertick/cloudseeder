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
import apiClient from "./utils/apiClient";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState(""); // State to manage error messages

  const handleLogin = async (event) => {
    event.preventDefault();

    try {
      const response = await apiClient.postForm("/login", {
        email: email,
        username: email,
        password: password,
      });

      if (response) {
        // Assuming successful login returns a token or user data
        console.log("User logged in successfully:", response);

        // Clear any previous error messages
        setErrorMessage("");

        // Perform actions for successful login, e.g., redirect or update context
        // Example: useUser.setState({ userInfo: response.data });
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
      flexDirection: "column", // Adjust for header on top
      height: "100vh",
      backgroundColor: "#b3e5fc",
      backgroundImage: "url(/freeze_data.png)",
      backgroundSize: "cover",
      backgroundPosition: "center",
    }}
  >
    {/* Header Section */}
    <div
      style={{
        backgroundColor: "rgb(47, 63, 92)",
        color: "white",
        textAlign: "center",
        padding: "20px 0",
      }}
    >
      <Typography variant="h6" component="div">
        Continuous MFA
      </Typography>
    </div>

    {/* Main Content */}
    <Container component="main" maxWidth="xs" style={{ paddingTop: "20px" }}>        <Paper
          style={{
            margin: "20px auto",
            padding: "20px",
            boxShadow: "none",
            borderRadius: "16px",
          }}
          elevation={10}
        >
          <Box
            sx={{
              marginTop: 8,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
            }}
          >
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                marginBottom: 2, // Add spacing below the header
              }}
            >
              <img
                src="/Metalytics-Logo_light.webp"
                alt="Metalytics Logo"
                style={{
                  height: "40px", // Adjust as needed
                  marginRight: "10px", // Add space between logo and text
                  color: "#1976d2", // Set the logo color
                }}
              />
              <Typography component="h1" variant="h5">
                Continuous MFA
              </Typography>
            </Box>
            <Box
              component="form"
              onSubmit={handleLogin}
              noValidate
              sx={{ mt: 3 }}
            >
              {errorMessage && (
                <Alert severity="error" sx={{ mb: 2 }}>
                  {errorMessage}
                </Alert>
              )}
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
                sx={{ mt: 3, mb: 2 }}
              >
                Login
              </Button>
              {/* 
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
              */}
            </Box>
          </Box>
        </Paper>
      </Container>
    </div>
  );
};

export default Login;
