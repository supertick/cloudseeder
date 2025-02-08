import React from "react";
import { Table, TableHead, TableBody, TableRow, TableCell, TableContainer, Tooltip, IconButton, Radio } from "@mui/material";
import { Delete as DeleteIcon } from "@mui/icons-material";
import { formatDate } from "./DateUtils";

export default function ReportInputTable({ inputFiles, selectedFile, setSelectedFile, handleOpenDeleteDialog }) {
  return (
    <TableContainer sx={{ maxHeight: "180px", overflowY: "auto" }}>
      <Table sx={{ borderCollapse: "collapse" }}>
        {/* Make the Table Head Sticky */}
        <TableHead sx={{ position: "sticky", top: 0, zIndex: 1 }}>
          <TableRow>
            <TableCell></TableCell>
            <TableCell>Filename</TableCell>
            <TableCell>Uploaded</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {inputFiles.map((record) => (
            <TableRow key={record.id} hover onClick={() => setSelectedFile(record.id)}>
              <TableCell><Radio checked={record.id === selectedFile} /></TableCell>
              <TableCell>{record.files}</TableCell>
              <TableCell>{formatDate(record.upload_date)}</TableCell>
              <TableCell>
                <Tooltip title="Delete">
                  <IconButton onClick={(e) => { e.stopPropagation(); handleOpenDeleteDialog(record.id); }}>
                    <DeleteIcon />
                  </IconButton>
                </Tooltip>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
}
