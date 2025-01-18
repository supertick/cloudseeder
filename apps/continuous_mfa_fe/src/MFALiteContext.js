import React, { createContext, useContext, useState } from 'react'

// Create a context
const MFALiteContext = createContext()

// Custom hook to use the context
export const useMFALite = () => useContext(MFALiteContext)

// Context provider component
export const MFALiteProvider = ({ children }) => {
  const [fileData, setFileData] = useState(null)
  const [reports, setReports] = useState([])
  const [mfaStatus, setMfaStatus] = useState('') // Track MFA Lite status

  const value = {
    fileData,
    setFileData,
    reports,
    setReports,
    mfaStatus,
    setMfaStatus,
  }

  return <MFALiteContext.Provider value={value}>{children}</MFALiteContext.Provider>
}
