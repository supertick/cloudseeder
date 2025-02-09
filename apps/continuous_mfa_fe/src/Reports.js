import React, { useEffect, useState } from "react";
import {
  Paper,
  Button,
} from "@mui/material";
import { useParams } from "react-router-dom";
import {
  Add as AddIcon,
  Sync as SyncIcon,
  LibraryBooks as LibraryBooksIcon,
} from "@mui/icons-material";
import TopMenuBar from "./TopMenuBar";
import apiClient from "./utils/apiClient";
import Footer from "./Footer";
import ReportInputTable from "./ReportInputTable";
import ReportTable from "./ReportTable";
import ReportUploadDialog from "./ReportUploadDialog";
import ReportDeleteDialog from "./ReportDeleteDialog";
import ReportProcessDialog from "./ReportProcessDialog"; // Import the new dialog

export default function Report() {
  const { id } = useParams();
  const [isUploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isProcessDialogOpen, setIsProcessDialogOpen] = useState(false); // New state for process dialog
  const [deleteFileId, setDeleteFileId] = useState(null);
  const [user, setUser] = useState(null);
  const [inputFiles, setInputFiles] = useState([]);
  const [reports, setReports] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);

  const fetchData = async () => {
    try {
      const [userRes, inputsRes, reportsRes] = await Promise.all([
        apiClient.get(`/user/${id}`),
        apiClient.get("/inputs"),
        apiClient.get("/reports"),
      ]);
      setUser(userRes);
      setInputFiles(inputsRes.sort((a, b) => b.upload_date - a.upload_date));
      setReports(reportsRes.sort((a, b) => b.upload_date - a.upload_date));
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  useEffect(() => {
    fetchData();
  }, [id]);

  const handleProcessInputFile = (selectedProduct) => {
    apiClient.post("/run", {
      id: crypto.randomUUID(),
      product: selectedProduct,
      title: "input-1.xlsx",
      user_id: user?.email,
      input_dir: "input_dir",
      output_dir: "output_dir"
    }).then(response => {
      console.log("Processing started:", response);
    }).catch(error => {
      console.error("Error processing input file:", error);
    });
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
      <Paper
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
        <span style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <LibraryBooksIcon style={{ fontSize: 30, color: "#2F3F5C" }} />
          <span style={{ fontSize: 18, color: "#2F3F5C", fontWeight: "bold" }}>{user?.fullname}</span>
          <Button variant="contained" color="primary" startIcon={<AddIcon />} onClick={() => setUploadDialogOpen(true)}>
            Add Input
          </Button>
          <Button
            variant="contained"
            color="primary"
            startIcon={<SyncIcon />}
            disabled={!selectedFile}
            onClick={() => setIsProcessDialogOpen(true)}
          >
            Process Input File
          </Button>
        </span>

        {/* Input Table */}
        <ReportInputTable
          inputFiles={inputFiles}
          selectedFile={selectedFile}
          setSelectedFile={setSelectedFile}
          handleOpenDeleteDialog={setIsDeleteDialogOpen}
        />

        <br />

        {/* Report Table */}
        <ReportTable reports={reports} handleOpenDeleteDialog={setIsDeleteDialogOpen} />
      </Paper>

      {/* Upload Dialog */}
      <ReportUploadDialog
        isOpen={isUploadDialogOpen}
        onClose={() => setUploadDialogOpen(false)}
        onUpload={fetchData} // Refresh inputs after upload
      />

      {/* Process Dialog */}
      <ReportProcessDialog
        isOpen={isProcessDialogOpen}
        onClose={() => setIsProcessDialogOpen(false)}
        onProcess={handleProcessInputFile}
      />

      {/* Delete Dialog */}
      <ReportDeleteDialog
        isOpen={isDeleteDialogOpen}
        onClose={() => setIsDeleteDialogOpen(false)}
        onDelete={fetchData} // Refresh inputs after delete
      />

      <Footer />
    </div>
  );
}
