import React from "react";
import {
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  TableContainer,
  Tooltip,
  IconButton,
  Radio
} from "@mui/material";
import { Delete as DeleteIcon, GetApp as DownloadIcon } from "@mui/icons-material";
import { formatDate } from "./DateUtils";

export default function ReportInputTable({ inputFiles, selectedFile, setSelectedFile, handleOpenDeleteDialog }) {

  // Function to handle file download
  const handleDownload = (fileUrl, fileName) => {
    const link = document.createElement("a");
    link.href = fileUrl;
    link.download = fileName; // Suggested file name
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Sort inputFiles by upload_date in descending order
  const sortedFiles = [...inputFiles].sort((a, b) => new Date(b.upload_date) - new Date(a.upload_date));

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
          {sortedFiles.map((record) => (
            <TableRow key={record.id} hover onClick={() => setSelectedFile(record.id)}>
              <TableCell><Radio checked={record.id === selectedFile} /></TableCell>
              <TableCell>{record.files}</TableCell>
              <TableCell>{formatDate(record.upload_date)}</TableCell>
              <TableCell>
                <Tooltip title="Download">
                  <IconButton
                    onClick={(e) => { 
                      e.stopPropagation();
                      handleDownload(record.fileUrl, record.files);
                    }}
                  >
                    <DownloadIcon />
                  </IconButton>
                </Tooltip>
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
