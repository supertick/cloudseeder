import React from "react";
import { Table, TableHead, TableBody, TableRow, TableCell, TableContainer, Tooltip, IconButton } from "@mui/material";
import { Link } from "react-router-dom";
import { Delete as DeleteIcon, Apps as AppsIcon, Analytics as AnalyticsIcon } from "@mui/icons-material";

export default function ReportTable({ reports, handleOpenDeleteDialog }) {
  return (
    <TableContainer sx={{ maxHeight: "800px", overflowY: "auto" }}>
      <Table sx={{ borderCollapse: "collapse" }}>
        <TableHead>
          <TableRow>
            <TableCell></TableCell>
            <TableCell>Report</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {reports.map((record) => (
            <TableRow key={record.id}>
              <TableCell>              
              <AnalyticsIcon style={{ fontSize: 30, color: "#2F3F5C" }} />
              </TableCell>
              <TableCell>
                <Link to={`/products`} style={{ textDecoration: "none", color: "#1976d2" }}>{record.title} {record.id}</Link>
              </TableCell>
              <TableCell>
                <Tooltip title="Delete">
                  <IconButton onClick={() => handleOpenDeleteDialog(record.id)}>
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
