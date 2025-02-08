import React, { useState, useRef } from "react";
import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Button,
  Typography,
  Box,
  CircularProgress,
} from "@mui/material";

export default function ReportUploadDialog({ isOpen, onClose, onUpload }) {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    const droppedFile = event.dataTransfer.files[0];
    if (droppedFile) {
      setFile(droppedFile);
    }
  };

  const handleUpload = () => {
    if (file) {
      setIsUploading(true);
      onUpload(file);
      setTimeout(() => {
        setIsUploading(false);
        setFile(null);
        onClose();
      }, 1000);
    }
  };

  return (
    <Dialog open={isOpen} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Upload Input File</DialogTitle>
      <DialogContent>
        {/* Drag & Drop Zone */}
        <Box
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          sx={{
            border: "2px dashed #1976d2",
            borderRadius: "8px",
            textAlign: "center",
            padding: "20px",
            backgroundColor: isDragging ? "#f0f8ff" : "#fafafa",
            cursor: "pointer",
          }}
          onClick={() => fileInputRef.current.click()}
        >
          <Typography variant="body1" color="textSecondary">
            {file ? `Selected: ${file.name}` : "Drag & drop a file here or click to select"}
          </Typography>
        </Box>

        {/* Hidden File Input */}
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          style={{ display: "none" }}
        />
      </DialogContent>

      <DialogActions>
        <Button onClick={onClose} color="primary" disabled={isUploading}>
          Cancel
        </Button>
        <Button onClick={handleUpload} color="primary" disabled={!file || isUploading}>
          {isUploading ? <CircularProgress size={20} /> : "Upload"}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
