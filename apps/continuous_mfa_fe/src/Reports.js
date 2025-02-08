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

export default function Report() {
  const { id } = useParams();
  const [isUploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
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

  const handleFileUpload = (file) => {
    const epoch_time = new Date().getTime();
    const metadata = {
      id: `${user?.id}-${epoch_time}`,
      filename: file.name,
      user_id: user?.id,
      upload_date: epoch_time,
    };

    const reader = new FileReader();
    reader.onload = () => {
      const base64File = reader.result.split(",")[1]; // Extract the Base64 string
      const payload = {
        ...metadata,
        data: base64File, // Add the encoded file
      };

      // Example of sending the payload
      apiClient
        .post("/upload-file-content", payload)
        .then((response) => {
          console.log("Metadata posted successfully:", response);
          const metadata = {
            id: response.id,
            files: [file.name],
            user_id: user?.id,
            upload_date: epoch_time,
          };
          apiClient
            .post("/input", metadata)
            .then((response) => {
              console.info("File processed successfully:", response);
            })
            .catch((error) => {
              console.error("Error processing file:", error);
            });
            // apiClient.get("/inputs")  
          return response;
        })
        .catch((error) => {
          console.error("Error posting metadata:", error);
        });
    };

    reader.onerror = (error) => {
      console.error("Error reading file:", error);
    };

    reader.readAsDataURL(file); // Read the file as Base64
  };

  const handleOpenDeleteDialog = (fileId) => {
    setDeleteFileId(fileId);
    setIsDeleteDialogOpen(true);
  };

  const handleDeleteFile = async () => {
    try {
      await apiClient.delete(`/input/${deleteFileId}`);
      setInputFiles((prev) => prev.filter((file) => file.id !== deleteFileId));
      setIsDeleteDialogOpen(false);
    } catch (error) {
      console.error("Error deleting file:", error);
    }
  };

  const handleProcessInputFile = () => {
    apiClient.post("/run", {
      "id": crypto.randomUUID(),
      "product": "string",
      "title": "input-1.xlsx",
      "user_id": "john@company1.com",
      "input_dir": "input_dir",
      "output_dir": "output_dir"
    })
  }

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
          <Button variant="contained" color="primary" startIcon={<SyncIcon />} disabled={!selectedFile} onClick={handleProcessInputFile}>
            Process Input File
          </Button>
        </span>

        {/* Input Table */}
        <ReportInputTable inputFiles={inputFiles} selectedFile={selectedFile} setSelectedFile={setSelectedFile} handleOpenDeleteDialog={handleOpenDeleteDialog} />

        <br />

        {/* Report Table */}
        <ReportTable reports={reports} handleOpenDeleteDialog={handleOpenDeleteDialog} />
      </Paper>

      {/* Upload Dialog */}
          <ReportUploadDialog
      isOpen={isUploadDialogOpen}
      onClose={() => setUploadDialogOpen(false)}
      onUpload={handleFileUpload}
    />

      {/* Delete Dialog */}
      <ReportDeleteDialog isOpen={isDeleteDialogOpen} onClose={() => setIsDeleteDialogOpen(false)} onDelete={handleDeleteFile} />

      <Footer />
    </div>
  );
}
