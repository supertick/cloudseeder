import React, { useEffect, useState } from "react";
import {
  Paper,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Avatar,
  IconButton,
  Tooltip,
  Button,
  Box,
} from "@mui/material";
import PersonIcon from "@mui/icons-material/Person";
import AddIcon from "@mui/icons-material/Add";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import TopMenuBar from "./TopMenuBar";
import { useUser } from "./UserContext";
import apiClient from "./utils/apiClient";
import Footer from "./Footer";

export default function Admin() {
  const { userInfo } = useUser(); // Access logged-in user info from context
  const [users, setUsers] = useState([]); // State to store users

  // Fetch user data from the API
  useEffect(() => {
    const fetchUsers = async () => {
      try {
        const response = await apiClient.get("/users");
        if (response) {
          setUsers(response);
        }
      } catch (error) {
        console.error("Error fetching users:", error);
      }
    };

    fetchUsers();
  }, []);

  const handleAddUser = () => {
    // Logic for adding a new user
    console.log("Add user button clicked");
  };

  const handleEditUser = (userId) => {
    // Logic for editing a user
    console.log("Edit user:", userId);
  };

  const handleDeleteUser = (userId) => {
    // Logic for deleting a user
    console.log("Delete user:", userId);
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
      <TopMenuBar />
      <div
        style={{
          textAlign: "center",
          backgroundColor: "rgba(255, 255, 255, 0.8)",
          padding: "20px",
          borderRadius: "10px",
          width: "90%",
          maxWidth: "1200px",
          boxShadow: "0 4px 8px rgba(0, 0, 0, 0.2)",
        }}
      >
        <h2>User List</h2>
        {/* Add User Button */}
        <Box display="flex" justifyContent="flex-end" mb={2}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleAddUser}
          >
            Add User
          </Button>
        </Box>

        {/* MUI Paper Table */}
        <Paper
          style={{
            margin: "20px auto",
            padding: "20px",
            boxShadow: "none",
            backgroundColor: "rgba(255, 255, 255, 0.9)",
          }}
        >
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Profile</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Full Name</TableCell>
                <TableCell>Last Logged In</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Errors</TableCell>
                <TableCell>Success</TableCell>
                <TableCell>Actions</TableCell> {/* New column for edit/delete */}
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>
                    <Avatar>
                      <PersonIcon /> {/* Blank person icon */}
                    </Avatar>
                  </TableCell>
                  <TableCell>
                    <a
                      href={`mailto:${user.email}`}
                      style={{ textDecoration: "none", color: "#1976d2" }}
                    >
                      {user.email}
                    </a>
                  </TableCell>
                  <TableCell>{user.fullname}</TableCell>
                  <TableCell>{user.last_login}</TableCell>
                  <TableCell>{user.role}</TableCell>
                  <TableCell>{user.errors}</TableCell>
                  <TableCell>{user.success}</TableCell>
                  <TableCell>
                    <Tooltip title="Edit User">
                      <IconButton
                        color="primary"
                        onClick={() => handleEditUser(user.id)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete User">
                      <IconButton
                        color="secondary"
                        onClick={() => handleDeleteUser(user.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      </div>
      <Footer />
    </div>
  );
}
