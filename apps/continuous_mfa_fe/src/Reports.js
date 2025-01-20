import React, { useEffect, useState } from "react";
import { formatDate } from "./DateUtils";
import {
  Paper,
  Table,
  Switch,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Avatar,
  Tooltip,
  Button,
  Box,
  Dialog,
  DialogActions,
  DialogContent,
  DialogContentText,
  DialogTitle,
  TextField,
  TableContainer,
  IconButton,
  Radio,
  Select,
  MenuItem,
  Checkbox,
  ListItemText,
} from "@mui/material";
import { Link } from "react-router-dom";
import PersonIcon from "@mui/icons-material/Person";
import AddIcon from "@mui/icons-material/Add";
import DeleteIcon from "@mui/icons-material/Delete";
import TopMenuBar from "./TopMenuBar";
import apiClient from "./utils/apiClient";
import Footer from "./Footer";
import { useParams } from "react-router-dom";
import AppsIcon from "@mui/icons-material/Apps";
import LibraryBooksIcon from "@mui/icons-material/LibraryBooks";
import MenuBookIcon from "@mui/icons-material/MenuBook";
import LocalLibraryIcon from "@mui/icons-material/LocalLibrary";
import CollectionsIcon from "@mui/icons-material/Collections";
import FolderIcon from "@mui/icons-material/Folder";
import WidgetsIcon from "@mui/icons-material/Widgets";
import DownloadIcon from "@mui/icons-material/Download";
import AnalyticsIcon from "@mui/icons-material/Analytics";
import SyncIcon from "@mui/icons-material/Sync";
import InputUploadDialog from "./InputUploadDialog";

export default function Reports() {
  const { id } = useParams();
  const [isDialogOpen, setDialogOpen] = useState(false);
  const [user, setUser] = useState(null);
  const [products, setProducts] = useState([]);
  const [inputFiles, setinputFiles] = useState([]);
  const [deleteUserId, setDeleteUserId] = useState(null);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false); // Add dialog state
  const [selectedFile, setSelectedFile] = useState(null); // State for radio button selection
  const sortedFiles = [...inputFiles].sort(
    (a, b) => b.upload_date - a.upload_date
  );

  const [newAccess, setNewAccess] = useState({
    id: "",
    user_id: "",
    product_id: "",
    access: false,
    enabled: false,
  });

  const [editingAccess, setEditingAccess] = useState(null);

  useEffect(() => {
    const fetchUserProductAccess = async () => {
      try {
        const response = await apiClient.get("/inputs");
        if (response) {
          setinputFiles(response);
        }
      } catch (error) {
        console.error("Error fetching inputFiles:", error);
      }
    };

    fetchUserProductAccess();
  }, []);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await apiClient.get("/products");
        if (response) {
          setProducts(response);
        }
      } catch (error) {
        console.error("Error fetching inputFiles:", error);
      }
    };

    fetchProducts();
  }, []);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const response = await apiClient.get("/user/" + id);
        if (response) {
          setUser(response);
        }
      } catch (error) {
        console.error("Error fetching fetchUser:", error);
      }
      const sortedFiles = [...inputFiles].sort(
        (a, b) => b.upload_date - a.upload_date
      );
    };

    fetchUser();
  }, []);

  const handleInputUpload = () => {
    setNewAccess({ email: "", fullname: "", roles: [] }); // Reset new user form
    setIsAddDialogOpen(true);
  };

  const handleCloseAddDialog = () => {
    setNewAccess({ email: "", fullname: "", roles: [] }); // Clear form
    setIsAddDialogOpen(false);
  };

  const handleSaveAdd = async () => {
    try {
      newAccess.id = user.id + "-" + newAccess.product_id;
      newAccess.user_id = user.id;
      const response = await apiClient.post("/user-product-access", newAccess);
      setinputFiles((prevUserProductAccess) => [
        ...prevUserProductAccess,
        response,
      ]);
      handleCloseAddDialog();
    } catch (error) {
      console.error("Error adding user:", error);
    }
  };

  const handleNewAccessFieldChange = (field, value) => {
    setNewAccess((prevUser) => ({
      ...prevUser,
      [field]: value,
    }));
  };

  const handleOpenDeleteInputDialog = (userId) => {
    setDeleteUserId(userId);
    setIsDeleteDialogOpen(true);
  };

  const handleCloseDeleteDialog = () => {
    setDeleteUserId(null);
    setIsDeleteDialogOpen(false);
  };

  const handleDeleteInputFile = async () => {
    try {
      await apiClient.delete(`/input/${deleteUserId}`);
      setinputFiles((prevUserProductAccess) =>
        prevUserProductAccess.filter((user) => user.id !== deleteUserId)
      );
      handleCloseDeleteDialog();
    } catch (error) {
      console.error("Error deleting user:", error);
    }
  };

  const handleToggle = (id, field) => {
    setinputFiles((prevRecords) =>
      prevRecords.map((record) =>
        record.id === id ? { ...record, [field]: !record[field] } : record
      )
    );

    // Find the specific record and merge the changes
    const updatedRecord = inputFiles.find((record) => record.id === id);
    if (updatedRecord) {
      const updatedData = { ...updatedRecord, [field]: !updatedRecord[field] }; // Merge changes

      apiClient
        .put(`/user-product-access/${id}`, updatedData) // Send the full updated record
        .then(() => {
          console.log(`Updated ${field} for record ID ${id}`);
        })
        .catch((error) => {
          console.error(`Error updating ${field} for record ID ${id}:`, error);
        });
    }
  };

  const handleInputDownload = (id) => {
    // Example download logic
    apiClient
      .get(`/download/${id}`, { responseType: "blob" }) // Adjust endpoint as needed
      .then((response) => {
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", `record-${id}.json`); // Adjust file name and type
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      })
      .catch((error) => {
        console.error(`Error downloading file for record ID ${id}:`, error);
      });
  };
  const handleInputFileUpload = (file) => {
    const metadata = {
      filename: file.name,
      uploadDate: new Date().toISOString(),
      description: "This is an uploaded file",
    };
  
    const reader = new FileReader();
    reader.onload = () => {
      const base64File = reader.result.split(",")[1]; // Extract the Base64 string
      const payload = {
        ...metadata,
        file: base64File, // Add the encoded file
      };
  
      // Example of sending the payload
      apiClient.post("/input-file-content", payload);
    };
  
    reader.onerror = (error) => {
      console.error("Error reading file:", error);
    };
  
    reader.readAsDataURL(file); // Read the file as Base64
  };
  

  <InputUploadDialog
    isInputUploadDialogOpen={isDialogOpen}
    handleCloseInputUploadDialog={() => setDialogOpen(false)}
    handleInputFileUpload={handleInputFileUpload}
  />;

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
        <span style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <LibraryBooksIcon style={{ fontSize: 30, color: "#2F3F5C" }} />
          <span style={{ fontSize: 18, color: "#2F3F5C", fontWeight: "bold" }}>
            {user?.fullname} Input Files
          </span>
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => setDialogOpen(true)}
          >
            Add Input File
          </Button>

          <Button
            variant="contained"
            color="primary"
            startIcon={<SyncIcon />}
            onClick={handleInputUpload}
          >
            Process Input File
          </Button>
        </span>
        {/* Input Library */}

        <Paper>
          <TableContainer
            sx={{
              maxHeight: "400px", // Set maximum height for the table container
              overflowY: "auto", // Enable vertical scrolling when content overflows
            }}
          >
            <Table
              sx={{
                borderCollapse: "collapse", // Removes borders between cells
              }}
            >
              <TableHead>
                <TableRow
                  sx={{
                    height: "40px", // Adjust header row height
                    "& .MuiTableCell-root": {
                      padding: "4px 8px", // Reduce padding for header cells
                    },
                  }}
                >
                  <TableCell></TableCell>
                  <TableCell>Filename</TableCell>
                  <TableCell>Uploaded</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {sortedFiles.map((record) => (
                  <TableRow
                    key={record.id}
                    hover
                    selected={record.id === selectedFile} // Highlights the selected row
                    onClick={() => setSelectedFile(record.id)} // Select row on click
                    sx={{
                      height: "30px", // Reduce row height
                      cursor: "pointer", // Indicate the row is clickable
                      "&:hover": {
                        backgroundColor: "#f5f5f5", // Light gray hover effect
                      },
                      "&.Mui-selected": {
                        backgroundColor: "#dbe9ff", // Light blue for selected row
                      },
                      "& .MuiTableCell-root": {
                        padding: "4px 8px", // Reduce padding for body cells
                      },
                    }}
                  >
                    <TableCell>
                      <Radio
                        checked={record.id === selectedFile}
                        value={record.id}
                        name="inputFileSelection"
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{record.files}</TableCell>
                    <TableCell>{formatDate(record.upload_date)}</TableCell>
                    <TableCell>
                      <Tooltip title="Download">
                        <IconButton
                          onClick={(e) => {
                            e.stopPropagation(); // Prevent row selection when clicking download
                            handleInputDownload(record.id);
                          }}
                          size="small"
                        >
                          <DownloadIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete Input File">
                        <IconButton
                          onClick={(e) => {
                            e.stopPropagation(); // Prevent row selection when clicking delete
                            handleOpenDeleteInputDialog(record.id);
                          }}
                          size="small"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
        <br />
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <AnalyticsIcon style={{ fontSize: 30, color: "#2F3F5C" }} />
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "10px",
            }}
          ></div>
          <h3 style={{ color: "#2F3F5C", margin: 0 }}>
            {user?.fullname} Reports
          </h3>
        </div>

        {/* MUI Paper Table */}
        <Paper>
          <TableContainer
            sx={{
              maxHeight: "400px", // Set maximum height for the table container
              overflowY: "auto", // Enable vertical scrolling when content overflows
            }}
          >
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell></TableCell>
                  <TableCell>Report</TableCell>
                  <TableCell>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {inputFiles.map((record) => (
                  <TableRow key={record.id}>
                    <TableCell>
                      <AppsIcon style={{ fontSize: 40, color: "#2F3F5C" }} />
                    </TableCell>
                    <TableCell>
                      <Link
                        to={`/products`} // Link to product details
                        style={{ textDecoration: "none", color: "#1976d2" }}
                      >
                        {record.product_id}
                      </Link>
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Delete Access">
                        <IconButton
                          onClick={() => handleOpenDeleteInputDialog(record.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </div>
      {/* Delete Confirmation Dialog */}
      <Dialog
        open={isDeleteDialogOpen}
        onClose={handleCloseDeleteDialog}
        aria-labelledby="delete-user-dialog-title"
        aria-describedby="delete-user-dialog-description"
      >
        <DialogTitle id="delete-user-dialog-title">
          {"Delete Input File?"}
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="delete-user-dialog-description">
            Are you sure you want to delete access this file {deleteUserId}?
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDeleteDialog} color="primary">
            Cancel
          </Button>
          <Button onClick={handleDeleteInputFile} color="secondary" autoFocus>
            Yes
          </Button>
        </DialogActions>
      </Dialog>
      {/* InputUploadDialog */}
      <InputUploadDialog
        isInputUploadDialogOpen={isDialogOpen}
        handleCloseInputUploadDialog={() => setDialogOpen(false)}
        handleInputFileUpload={handleInputFileUpload}
      />
      ;
      <Footer />
    </div>
  );
}
