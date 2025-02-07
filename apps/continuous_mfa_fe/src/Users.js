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
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  Select,
  MenuItem,
  Checkbox,
  ListItemText,
} from "@mui/material";
import { Link } from "react-router-dom";
import PersonIcon from "@mui/icons-material/Person";
import AddIcon from "@mui/icons-material/Add";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import TopMenuBar from "./TopMenuBar";
import apiClient from "./utils/apiClient";
import Footer from "./Footer";

const VALID_ROLES = ["admin", "user"]; // Define valid roles

export default function Users() {
  const [users, setUsers] = useState([]);
  const [deleteUserId, setDeleteUserId] = useState(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false); // Add dialog state
  const [newUser, setNewUser] = useState({
    email: "",
    fullname: "",
    roles: [],
  }); // State for new user
  const [editingUser, setEditingUser] = useState(null);

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
    setNewUser({ email: "", fullname: "", roles: [] }); // Reset new user form
    setIsAddDialogOpen(true);
  };

  const handleCloseAddDialog = () => {
    setNewUser({ email: "", fullname: "", roles: [] }); // Clear form
    setIsAddDialogOpen(false);
  };

  const handleSaveAdd = async () => {
    try {
      const response = await apiClient.post("/user", newUser);
      setUsers((prevUsers) => [...prevUsers, response]);
      handleCloseAddDialog();
    } catch (error) {
      console.error("Error adding user:", error);
    }
  };

  const handleNewUserFieldChange = (field, value) => {
    setNewUser((prevUser) => ({
      ...prevUser,
      [field]: value,
    }));
  };

  const handleEditUser = (user) => {
    setEditingUser(user);
    setIsEditDialogOpen(true);
  };

  const handleCloseEditDialog = () => {
    setEditingUser(null);
    setIsEditDialogOpen(false);
  };

  const handleOpenDeleteDialog = (userId) => {
    setDeleteUserId(userId);
    setIsDeleteDialogOpen(true);
  };

  const handleCloseDeleteDialog = () => {
    setDeleteUserId(null);
    setIsDeleteDialogOpen(false);
  };

  const handleDeleteUser = async () => {
    try {
      await apiClient.delete(`/user/${deleteUserId}`);
      setUsers((prevUsers) =>
        prevUsers.filter((user) => user.id !== deleteUserId)
      );
      handleCloseDeleteDialog();
    } catch (error) {
      console.error("Error deleting user:", error);
    }
  };

  const handleSaveEdit = async () => {
    try {
      await apiClient.put(`/user/${editingUser.id}`, editingUser);
      setUsers((prevUsers) =>
        prevUsers.map((user) =>
          user.id === editingUser.id ? editingUser : user
        )
      );
      handleCloseEditDialog();
    } catch (error) {
      console.error("Error updating user:", error);
    }
  };

  const handleEditFieldChange = (field, value) => {
    setEditingUser((prevUser) => ({
      ...prevUser,
      [field]: value,
    }));
  };

  const formatEpochTimestamp = (epoch) => {
  if (!epoch) return "N/A"; // Handle missing or null timestamps

  const date = new Date(epoch * 1000); // Convert epoch seconds to milliseconds
  return date.toLocaleString(); // Formats as "MM/DD/YYYY, HH:MM:SS AM/PM" based on locale
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
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <PersonIcon style={{ fontSize: 40, color: "#2F3F5C" }} />
          <h1 style={{ color: "#2F3F5C", margin: 0 }}>Users</h1>
        </div>

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
        <Paper>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Profile</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Full Name</TableCell>
                <TableCell>Logins</TableCell>
                <TableCell>Success</TableCell>
                <TableCell>Unsuccessful</TableCell>
                <TableCell>Roles</TableCell> 
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>
                    <Avatar>
                      <PersonIcon />
                    </Avatar>
                  </TableCell>
                  <TableCell>
                    <Link
                      to={`/user/${user.id}`} // Route to user/{id}
                      style={{ textDecoration: "none", color: "#1976d2" }} // Style like a link
                    >
                      {user.email}
                    </Link>
                  </TableCell>{" "}
                  <TableCell>{user.fullname}</TableCell>
                   <TableCell>{user.login_count}</TableCell>
                  <TableCell>{formatEpochTimestamp(user.last_login)}</TableCell>
                  <TableCell>{formatEpochTimestamp(user.last_unsuccessful_login)}</TableCell>
                  <TableCell>{user.roles.join(", ")}</TableCell>
                  <TableCell>
                    <Tooltip title="Edit User">
                      <IconButton
                        color="primary"
                        onClick={() => handleEditUser(user)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete User">
                      <IconButton
                        onClick={() => handleOpenDeleteDialog(user.id)}
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
      {/* Delete Confirmation Dialog */}
      <Dialog
        open={isDeleteDialogOpen}
        onClose={handleCloseDeleteDialog}
        aria-labelledby="delete-user-dialog-title"
        aria-describedby="delete-user-dialog-description"
      >
        <DialogTitle id="delete-user-dialog-title">
          {"Delete User?"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-user-dialog-description">
            Are you sure you want to delete user with ID {deleteUserId}?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDeleteUser} color="secondary" autoFocus>
            Yes
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit User Dialog */}
      <Dialog
        open={isEditDialogOpen}
        onClose={handleCloseEditDialog}
        aria-labelledby="edit-user-dialog-title"
        aria-describedby="edit-user-dialog-description"
      >
        <DialogTitle id="edit-user-dialog-title">Edit User</DialogTitle>
        <DialogContent>
          <TextField
            label="Email"
            value={editingUser?.email || ""}
            fullWidth
            margin="normal"
            disabled
          />
          <TextField
            label="Full Name"
            value={editingUser?.fullname || ""}
            fullWidth
            margin="normal"
            onChange={(e) => handleEditFieldChange("fullname", e.target.value)}
          />
          <Select
            label="Roles"
            multiple
            value={editingUser?.roles || []}
            onChange={(e) => handleEditFieldChange("roles", e.target.value)}
            fullWidth
            renderValue={(selected) => selected.join(", ")}
          >
            {VALID_ROLES.map((role) => (
              <MenuItem key={role} value={role}>
                <Checkbox checked={editingUser?.roles?.includes(role)} />
                <ListItemText primary={role} />
              </MenuItem>
            ))}
          </Select>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseEditDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleSaveEdit} color="secondary" autoFocus>
            Save
          </Button>
        </DialogActions>
      </Dialog>
      {/* Add User Dialog */}
      <Dialog
        open={isAddDialogOpen}
        onClose={handleCloseAddDialog}
        aria-labelledby="add-user-dialog-title"
        aria-describedby="add-user-dialog-description"
      >
        <DialogTitle id="add-user-dialog-title">Add New User</DialogTitle>
        <DialogContent>
          <TextField
            label="Email"
            value={newUser.email}
            fullWidth
            margin="normal"
            onChange={(e) => handleNewUserFieldChange("email", e.target.value)}
          />
          <TextField
            label="Full Name"
            value={newUser.fullname}
            fullWidth
            margin="normal"
            onChange={(e) =>
              handleNewUserFieldChange("fullname", e.target.value)
            }
          />
          <Select
            label="Roles"
            multiple
            value={newUser.roles}
            onChange={(e) => handleNewUserFieldChange("roles", e.target.value)}
            fullWidth
            renderValue={(selected) => selected.join(", ")}
          >
            {VALID_ROLES.map((role) => (
              <MenuItem key={role} value={role}>
                <Checkbox checked={newUser.roles.includes(role)} />
                <ListItemText primary={role} />
              </MenuItem>
            ))}
          </Select>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseAddDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleSaveAdd} color="secondary" autoFocus>
            Save
          </Button>
        </DialogActions>
      </Dialog>

      <Footer />
    </div>
  );
}
