import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
} from "@mui/material";

export default function InputUploadDialog({
  isInputUploadDialogOpen,
  handleCloseInputUploadDialog,
  handleInputFileUpload,
}) {
  const [selectedInputUploadFile, setSelectedInputUploadFile] = useState(null);

  const handleInputUploadFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedInputUploadFile(file);
  };

  const handleInputUploadDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    const file = event.dataTransfer.files[0];
    setSelectedInputUploadFile(file);
  };

  const handleInputUploadDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
  };

  const handleConfirmInputUpload = () => {
    if (selectedInputUploadFile) {
      handleInputFileUpload(selectedInputUploadFile); // Call the parent function with the selected file
      setSelectedInputUploadFile(null);
      handleCloseInputUploadDialog();
    }
  };

  return (
    <Dialog
      open={isInputUploadDialogOpen}
      onClose={handleCloseInputUploadDialog}
      aria-labelledby="input-upload-dialog-title"
      aria-describedby="input-upload-dialog-description"
    >
      <DialogTitle id="input-upload-dialog-title">Upload Input File</DialogTitle>
      <DialogContent>
        <Box sx={{ mb: 2 }}>
          <Button variant="contained" component="label">
            Select File
            <input
              type="file"
              hidden
              onChange={handleInputUploadFileSelect}
            />
          </Button>
          {selectedInputUploadFile && (
            <Typography variant="body2" sx={{ mt: 1 }}>
              Selected File: {selectedInputUploadFile.name}
            </Typography>
          )}
        </Box>
        <Box
          sx={{
            border: "2px dashed #ccc",
            borderRadius: "8px",
            padding: "20px",
            textAlign: "center",
            cursor: "pointer",
            "&:hover": { backgroundColor: "#f9f9f9" },
          }}
          onDrop={handleInputUploadDrop}
          onDragOver={handleInputUploadDragOver}
        >
          <Typography variant="body2" color="textSecondary">
            Drag and drop a file here, or click "Select File" above
          </Typography>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={handleCloseInputUploadDialog} color="primary">
          Cancel
        </Button>
        <Button
          onClick={handleConfirmInputUpload}
          color="primary"
          variant="contained"
          disabled={!selectedInputUploadFile}
        >
          Upload
        </Button>
      </DialogActions>
    </Dialog>
  );
}
