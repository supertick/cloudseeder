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
import PersonIcon from "@mui/icons-material/Person";
import AddIcon from "@mui/icons-material/Add";
import EditIcon from "@mui/icons-material/Edit";
import DeleteIcon from "@mui/icons-material/Delete";
import TopMenuBar from "./TopMenuBar";
import apiClient from "./utils/apiClient";
import Footer from "./Footer";
import AppsIcon from "@mui/icons-material/Apps";

const VALID_ROLES = ["admin", "product", "editor", "viewer"]; // Define valid roles

export default function Product() {
  const [products, setProducts] = useState([]);
  const [deleteProductId, setDeleteProductId] = useState(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false); // Add dialog state
  const [newProduct, setNewProduct] = useState({
    email: "",
    fullname: "",
    roles: [],
  }); // State for new product
  const [editingProduct, setEditingProduct] = useState(null);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await apiClient.get("/products");
        if (response) {
          setProducts(response);
        }
      } catch (error) {
        console.error("Error fetching products:", error);
      }
    };

    fetchProducts();
  }, []);

  const handleAddProduct = () => {
    setNewProduct({ email: "", fullname: "", roles: [] }); // Reset new product form
    setIsAddDialogOpen(true);
  };

  const handleCloseAddDialog = () => {
    setNewProduct({ email: "", fullname: "", roles: [] }); // Clear form
    setIsAddDialogOpen(false);
  };

  const handleSaveAdd = async () => {
    try {
      const response = await apiClient.post("/product", newProduct);
      setProducts((prevProducts) => [...prevProducts, response]);
      handleCloseAddDialog();
    } catch (error) {
      console.error("Error adding product:", error);
    }
  };

  const handleNewProductFieldChange = (field, value) => {
    setNewProduct((prevProduct) => ({
      ...prevProduct,
      [field]: value,
    }));
  };

  const handleEditProduct = (product) => {
    setEditingProduct(product);
    setIsEditDialogOpen(true);
  };

  const handleCloseEditDialog = () => {
    setEditingProduct(null);
    setIsEditDialogOpen(false);
  };

  const handleOpenDeleteDialog = (productId) => {
    setDeleteProductId(productId);
    setIsDeleteDialogOpen(true);
  };

  const handleCloseDeleteDialog = () => {
    setDeleteProductId(null);
    setIsDeleteDialogOpen(false);
  };

  const handleDeleteProduct = async () => {
    try {
      await apiClient.delete(`/product/${deleteProductId}`);
      setProducts((prevProducts) =>
        prevProducts.filter((product) => product.id !== deleteProductId)
      );
      handleCloseDeleteDialog();
    } catch (error) {
      console.error("Error deleting product:", error);
    }
  };

  const handleSaveEdit = async () => {
    try {
      await apiClient.put(`/product/${editingProduct.id}`, editingProduct);
      setProducts((prevProducts) =>
        prevProducts.map((product) =>
          product.id === editingProduct.id ? editingProduct : product
        )
      );
      handleCloseEditDialog();
    } catch (error) {
      console.error("Error updating product:", error);
    }
  };

  const handleEditFieldChange = (field, value) => {
    setEditingProduct((prevProduct) => ({
      ...prevProduct,
      [field]: value,
    }));
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
          <AppsIcon style={{ fontSize: 40, color: "#2F3F5C" }} />
          <h1 style={{ color: "#2F3F5C", margin: 0 }}>Products</h1>
        </div>
        <Box display="flex" justifyContent="flex-end" mb={2}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={handleAddProduct}
          >
            Add Product
          </Button>
        </Box>

        {/* MUI Paper Table */}
        <Paper>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Id</TableCell>
                <TableCell>Title</TableCell>
                <TableCell>Description</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {products.map((product) => (
                <TableRow key={product.id}>
                  <TableCell>{product.id}</TableCell>
                  <TableCell>{product.title}</TableCell>
                  <TableCell>{product.description}</TableCell>
                  <TableCell>
                    <Tooltip title="Edit Product">
                      <IconButton
                        color="primary"
                        onClick={() => handleEditProduct(product)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Delete Product">
                      <IconButton
                        onClick={() => handleOpenDeleteDialog(product.id)}
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
        aria-labelledby="delete-product-dialog-title"
        aria-describedby="delete-product-dialog-description"
      >
        <DialogTitle id="delete-product-dialog-title">
          {"Delete Product?"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-product-dialog-description">
            Are you sure you want to delete product with ID {deleteProductId}?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDeleteProduct} color="secondary" autoFocus>
            Yes
          </Button>
        </DialogActions>
      </Dialog>

      {/* Edit Product Dialog */}
      <Dialog
        open={isEditDialogOpen}
        onClose={handleCloseEditDialog}
        aria-labelledby="edit-product-dialog-title"
        aria-describedby="edit-product-dialog-description"
      >
        <DialogTitle id="edit-product-dialog-title">Edit Product</DialogTitle>
        <DialogContent>
          <TextField
            label="Id"
            value={editingProduct?.id || ""}
            fullWidth
            margin="normal"
            disabled
          />
          <TextField
            label="Title"
            value={editingProduct?.title || ""}
            fullWidth
            margin="normal"
            onChange={(e) => handleEditFieldChange("title", e.target.value)}
          />
          <TextField
            label="Description"
            value={editingProduct?.description || ""}
            fullWidth
            margin="normal"
            onChange={(e) => handleEditFieldChange("description", e.target.value)}
          />

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
      {/* Add Product Dialog */}
      <Dialog
        open={isAddDialogOpen}
        onClose={handleCloseAddDialog}
        aria-labelledby="add-product-dialog-title"
        aria-describedby="add-product-dialog-description"
      >
        <DialogTitle id="add-product-dialog-title">Add New Product</DialogTitle>
        <DialogContent>
          <TextField
            label="Id"
            value={newProduct.id}
            fullWidth
            margin="normal"
            onChange={(e) =>
              handleNewProductFieldChange("id", e.target.value)
            }
          />
          <TextField
            label="Title"
            value={newProduct.title}
            fullWidth
            margin="normal"
            onChange={(e) =>
              handleNewProductFieldChange("title", e.target.value)
            }
          />
          <TextField
            label="Description"
            value={newProduct.description}
            fullWidth
            margin="normal"
            onChange={(e) =>
              handleNewProductFieldChange("description", e.target.value)
            }
          />
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
