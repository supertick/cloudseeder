import React from 'react'
import { styled } from '@mui/system'
import Button from '@mui/material/Button'
import { post } from 'aws-amplify/api'
import { uploadData } from 'aws-amplify/storage'
import { useMFALite } from './MFALiteContext'
import { useUser } from './UserContext' // Import useUser to access userInfo

const StyledInput = styled('input')({
  display: 'none' // Hide the actual input
})

const PrimaryButton = styled(Button)({
  backgroundColor: '#2f3f5c',
  '&:hover': {
    backgroundColor: '#25344b'
  }
})

const DropZone = styled('div')({
  width: '100%',
  height: '100px',
  border: '2px dashed #2f3f5c',
  borderRadius: '10px',
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  color: '#2f3f5c',
  marginBottom: '10px',
  fontSize: '16px',
  cursor: 'pointer',
  '&:hover': {
    borderColor: '#25344b'
  }
})

export default function FileUploadSection() {
  const { fileData, setFileData, setMfaStatus } = useMFALite()
  const { userInfo } = useUser() // Get userInfo from the user context

  const startMFALite = async (filename) => {
    try {
      const restOperation = post({
        apiName: 'MetalyticsApi',
        path: '/startMFALite',
        options: {
          body: {
            xlsFileName: filename,
            email: userInfo?.signInDetails?.loginId,
            debug: false,
            payload: userInfo
          },
          responseType: 'blob'
        }
      })
  
      const { body } = await restOperation.response
      const response = await body.json()
  
      if (response) {
        setMfaStatus('MFA processing successfully started')
        // setProgress(100) // Simulate progress completion
      } else {
        setMfaStatus('MFA processing failed to start')
      }
    } catch (error) {
      console.error('Error starting MFA Lite:', error)
      setMfaStatus('Error starting MFA Lite')
    }
  }  

  const handleFileSelect = (file) => {
    if (file) {
      console.log('Selected file:', file)
      setFileData(file)
      setMfaStatus('')
    }
  }

  const handleDrop = (event) => {
    event.preventDefault()
    const droppedFile = event.dataTransfer.files[0]
    handleFileSelect(droppedFile)
  }

  const uploadFile = async () => {
    if (!fileData) return
  
    const safeName = userInfo.signInDetails.loginId.replace(/[@.]/g, '_')
    const filePath = `public/reports/${safeName}/${fileData.name}`
  
    try {
      console.log('Uploading file:', fileData.name)
      const result = await uploadData({
        path: filePath,
        data: fileData,
        contentType: fileData.type // Ensure correct content type
      })
  
      console.log('File uploaded successfully:', result)
  
      // Add a 3-second delay before calling startMFALite
      setTimeout(async () => {
        await startMFALite(fileData.name)
      }, 3000) // 3000 milliseconds = 3 seconds
  
    } catch (error) {
      console.error('Error uploading file:', error)
      setMfaStatus('Error uploading file or starting MFA Lite')
    }
  }

  
  return (
    <div>

      {/* Drag-and-Drop Area */}
      <DropZone onDrop={handleDrop} onDragOver={(e) => e.preventDefault()}>
        Drag & drop your file here or click below
      </DropZone>

      {fileData && <p>Selected file: {fileData.name}</p>}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '10px' }}>
        <label htmlFor="contained-button-file">
          <StyledInput
            accept=".xlsx,.xls"
            id="contained-button-file"
            type="file"
            onChange={(e) => handleFileSelect(e.target.files[0])}
          />
          <PrimaryButton variant="contained" component="span">
            Choose File
          </PrimaryButton>
        </label>
        {fileData && (
          <PrimaryButton variant="contained" color="secondary" onClick={uploadFile}>
            Upload File
          </PrimaryButton>
        )}
      </div>
    </div>
  )
}
