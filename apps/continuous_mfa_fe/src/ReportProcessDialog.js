import React, { useState, useEffect } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
} from "@mui/material";
import apiClient from "./utils/apiClient"; // Import API client

export default function ReportProcessDialog({ isOpen, onClose, onProcess }) {
  const [selectedProduct, setSelectedProduct] = useState("");
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (isOpen) {
      setLoading(true);
      apiClient
        .get("/products")
        .then((response) => {
          setProducts(response); // Store API response in state
          setLoading(false);
        })
        .catch((error) => {
          console.error("Error fetching products:", error);
          setLoading(false);
        });
    }
  }, [isOpen]); // Fetch products only when the dialog opens

  const handleProcess = () => {
    if (selectedProduct) {
      onProcess(selectedProduct); // Pass selected product ID to parent
      onClose(); // Close the dialog after processing
    }
  };

  return (
    <Dialog open={isOpen} onClose={onClose}>
      <DialogTitle>Select Product</DialogTitle>
      <DialogContent>
        {loading ? (
          <CircularProgress />
        ) : (
          <FormControl fullWidth>
            <InputLabel>Product</InputLabel>
            <Select
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
            >
              {products.map((product) => (
                <MenuItem key={product.id} value={product.id}>
                  {product.title} {/* Show title, but value is ID */}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button
          onClick={handleProcess}
          color="primary"
          variant="contained"
          disabled={!selectedProduct}
        >
          Process
        </Button>
      </DialogActions>
    </Dialog>
  );
}
