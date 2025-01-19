import React, { useEffect, useState } from "react";
import {
  Paper,
  Table,
  Switch,
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
import DeleteIcon from "@mui/icons-material/Delete";
import TopMenuBar from "./TopMenuBar";
import apiClient from "./utils/apiClient";
import Footer from "./Footer";
import { useParams } from "react-router-dom";
import AppsIcon from "@mui/icons-material/Apps";

const VALID_ROLES = ["admin", "user", "editor", "viewer"]; // Define valid roles

export default function User() {
  const { id } = useParams();

  const [user, setUser] = useState(null);
  const [products, setProducts] = useState([]);
  const [userProductAccess, setUserProductAccess] = useState([]);
  const [deleteUserId, setDeleteUserId] = useState(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false); // Add dialog state
  const [newAccess, setNewAccess] = useState({
    user_id: "",
    product_id: "",
    access: false,
    enabled: false
  }); 

  const [editingAccess, setEditingAccess] = useState(null);

  useEffect(() => {
    const fetchUserProductAccess = async () => {
      try {
        const response = await apiClient.get("/user-product-accesss");
        if (response) {
          setUserProductAccess(response);
        }
      } catch (error) {
        console.error("Error fetching userProductAccess:", error);
      }
    };

    fetchUserProductAccess();
  }, []);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await apiClient.get("/products");
        if (response) {
          setProducts(response);
        }
      } catch (error) {
        console.error("Error fetching userProductAccess:", error);
      }
    };

    fetchProducts();
  }, []);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await apiClient.get("/user/" + id);
        if (response) {
          setUser(response);
        }
      } catch (error) {
        console.error("Error fetching fetchUser:", error);
      }
    };

    fetchUser();
  }, []);

  const handleAddUser = () => {
    setNewAccess({ email: "", fullname: "", roles: [] }); // Reset new user form
    setIsAddDialogOpen(true);
  };

  const handleCloseAddDialog = () => {
    setNewAccess({ email: "", fullname: "", roles: [] }); // Clear form
    setIsAddDialogOpen(false);
  };

  const handleSaveAdd = async () => {
    try {
      const response = await apiClient.post("/user-product-access", newAccess);
      setUserProductAccess((prevUserProductAccess) => [
        ...prevUserProductAccess,
        response,
      ]);
      handleCloseAddDialog();
    } catch (error) {
      console.error("Error adding user:", error);
    }
  };

  const handleNewAccessFieldChange = (field, value) => {
    setNewAccess((prevUser) => ({
      ...prevUser,
      [field]: value,
    }));
  };

  const handleEditUser = (user) => {
    setEditingAccess(user);
    setIsEditDialogOpen(true);
  };

  const handleCloseEditDialog = () => {
    setEditingAccess(null);
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
      setUserProductAccess((prevUserProductAccess) =>
        prevUserProductAccess.filter((user) => user.id !== deleteUserId)
      );
      handleCloseDeleteDialog();
    } catch (error) {
      console.error("Error deleting user:", error);
    }
  };

  const handleSaveEdit = async () => {
    try {
      await apiClient.put(`/user/${editingAccess.id}`, editingAccess);
      setUserProductAccess((prevUserProductAccess) =>
        prevUserProductAccess.map((user) =>
          user.id === editingAccess.id ? editingAccess : user
        )
      );
      handleCloseEditDialog();
    } catch (error) {
      console.error("Error updating user:", error);
    }
  };

  const handleEditFieldChange = (field, value) => {
    setEditingAccess((prevUser) => ({
      ...prevUser,
      [field]: value,
    }));
  };

  const handleToggle = (id, field) => {
    setUserProductAccess((prevRecords) =>
      prevRecords.map((record) =>
        record.id === id ? { ...record, [field]: !record[field] } : record
      )
    );

    // Find the specific record to send updated value to the server
    const updatedRecord = userProductAccess.find((record) => record.id === id);
    if (updatedRecord) {
      apiClient
        .put(`/user-product-access/${id}`, { [field]: !updatedRecord[field] })
        .then(() => {
          console.log(`Updated ${field} for record ID ${id}`);
        })
        .catch((error) => {
          console.error(`Error updating ${field} for record ID ${id}:`, error);
        });
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
          <h1 style={{ color: "#2F3F5C", margin: 0 }}>User {user?.fullname}</h1>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          {user?.email}
        </div>

        <Box display="flex" justifyContent="flex-end" mb={2}>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleAddUser}
          >
            Add Product Access
          </Button>
        </Box>

        {/* MUI Paper Table */}
        <Paper>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell></TableCell>
                <TableCell>Product</TableCell>
                <TableCell>Access</TableCell>
                <TableCell>Enabled</TableCell>
                <TableCell>Errors</TableCell>
                <TableCell>Success</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {userProductAccess.map((record) => (
                <TableRow key={record.id}>
                  <TableCell>
                    <AppsIcon style={{ fontSize: 40, color: "#2F3F5C" }} />
                  </TableCell>
                  <TableCell>
                    <Link
                      to={`/products`} // Link to product details
                      style={{ textDecoration: "none", color: "#1976d2" }}
                    >
                      {record.product_id}
                    </Link>
                  </TableCell>
                  {/* Toggle for "access" */}
                  <TableCell>
                    <Switch
                      checked={record.access}
                      onChange={() => handleToggle(record.id, "access")}
                      color="primary"
                    />
                  </TableCell>
                  {/* Toggle for "enabled" */}
                  <TableCell>
                    <Switch
                      checked={record.enabled}
                      onChange={() => handleToggle(record.id, "enabled")}
                      color="primary"
                    />
                  </TableCell>
                  <TableCell>{record.errors}</TableCell>
                  <TableCell>{record.success}</TableCell>
                  <TableCell>
                    <Tooltip title="Delete Access">
                      <IconButton
                        onClick={() => handleOpenDeleteDialog(record.id)}
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


      {/* Add User Dialog */}
      <Dialog
        open={isAddDialogOpen}
        onClose={handleCloseAddDialog}
        aria-labelledby="add-user-dialog-title"
        aria-describedby="add-user-dialog-description"
      >
        <DialogTitle id="add-user-dialog-title">Add Product Access</DialogTitle>
        <DialogContent>
          <TextField
            label="Email"
            value={user?.id}
            fullWidth
            margin="normal"
            onChange={(e) =>
              handleNewAccessFieldChange("user_id", e.target.value)
            }
            style={{ display: "none" }}
          />
          <Select
            label="Roles"
            value={newAccess.roles || ""} // Ensure a default value
            onChange={(e) =>
              handleNewAccessFieldChange("product_id", e.target.value)
            }
            fullWidth
          >
            {products.map((product) => (
              <MenuItem key={product.id} value={product.id}>
                {product.id}{" "}
                {/* Adjust field name as needed */}
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
