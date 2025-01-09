import { useState } from "react"
import { apiClient } from "../utils/apiClient"
import {
  Box,
  Button,
  Container,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  Typography,
  Paper
} from "@mui/material"

export default function Home({ initialWidgets }) {
  const [widgets, setWidgets] = useState(initialWidgets)
  const [showForm, setShowForm] = useState(false)
  const [newWidgetName, setNewWidgetName] = useState("")

  // Add a new widget
  const handleAddWidget = async () => {
    if (newWidgetName.trim() !== "") {
      const newWidget = { name: newWidgetName.trim() }

      const createdWidget = await apiClient.post("/widgets", newWidget)

      setWidgets([...widgets, createdWidget])
      setNewWidgetName("")
      setShowForm(false)
    }
  }

  // Delete a widget
  const handleDeleteWidget = async (uuid) => {
    await apiClient.delete(`/widgets/${uuid}`)
    setWidgets(widgets.filter((widget) => widget.uuid !== uuid))
  }

  return (
    <Container maxWidth="md" sx={{ mt: 4 }}>
      <Typography variant="h3" component="h1" gutterBottom>
        Widgets
      </Typography>

      {/* Table of widgets */}
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell align="center">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {widgets.map((widget) => (
              <TableRow key={widget.uuid}>
                <TableCell>{widget.name}</TableCell>
                <TableCell align="center">
                  <Button
                    variant="contained"
                    color="error"
                    onClick={() => handleDeleteWidget(widget.uuid)}
                  >
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Add Widget Button */}
      <Button
        variant="contained"
        color="primary"
        onClick={() => setShowForm(!showForm)}
        sx={{ mb: 4 }}
      >
        {showForm ? "Cancel" : "Add Widget"}
      </Button>

      {/* Add Widget Form */}
      {showForm && (
        <Box
          component="form"
          sx={{
            display: "flex",
            flexDirection: "column",
            gap: 2,
            mt: 2
          }}
        >
          <TextField
            label="Widget Name"
            variant="outlined"
            value={newWidgetName}
            onChange={(e) => setNewWidgetName(e.target.value)}
          />
          <Button
            variant="contained"
            color="success"
            onClick={handleAddWidget}
          >
            Add Widget
          </Button>
        </Box>
      )}
    </Container>
  )
}

// Fetch widgets from the backend/7
export async function getStaticProps() {
  const initialWidgets = await apiClient.get("/widgets")

  return {
    props: { initialWidgets }
  }
}
