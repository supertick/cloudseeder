import React from "react";
import {
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  Button,
} from "@mui/material";

export default function ReportDeleteDialog({ isOpen, onClose, onDelete }) {
  return (
    <Dialog open={isOpen} onClose={onClose}>
      <DialogTitle>Delete Input File?</DialogTitle>
      <DialogContent>
        <DialogContentText>Are you sure you want to delete this file?</DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">Cancel</Button>
        <Button onClick={onDelete} color="secondary" autoFocus>
          Yes, Delete
        </Button>
      </DialogActions>
    </Dialog>
  );
}
