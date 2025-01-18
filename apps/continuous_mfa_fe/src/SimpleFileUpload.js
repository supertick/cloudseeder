import React, { useState } from 'react'
import Button from '@mui/material/Button'
import Box from '@mui/material/Box'

export default function SimpleFileUpload() {
  const [selectedFile, setSelectedFile] = useState(null)

  const handleFileChange = (event) => {
    const file = event.target.files[0]
    if (file) {
      setSelectedFile(file.name) // Set the selected file's name
    }
  }

  return (
    <Box sx={{ textAlign: 'center', marginTop: '20px' }}>
      <input
        type="file"
        accept="*/*"
        id="upload-button"
        style={{ display: 'none' }} // Hide the default file input
        onChange={handleFileChange}
      />
      <label htmlFor="upload-button">
        <Button variant="contained" color="primary" component="span">
          Choose File
        </Button>
      </label>

      {selectedFile && (
        <Box sx={{ marginTop: '10px', fontSize: '16px' }}>
          Selected file: {selectedFile}
        </Box>
      )}
    </Box>
  )
}
