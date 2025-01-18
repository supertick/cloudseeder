import React from 'react'
import { HashRouter as Router, Route, Routes } from 'react-router-dom' // Use HashRouter
import Home from './Home'
import Admin from './Admin'
import CloneSelectMFA from './CloneSelectMFA'
import MFALite from './MFALite'
import SimpleFileUpload from './SimpleFileUpload'
import NotFoundPage from './NotFoundPage'
import { UserProvider } from './UserContext'
import { MFALiteProvider } from './MFALiteContext'
import './custom-styles.css'
import UserProductAccess from './UserProductAccess'


function App({ signOut }) {
  return (
    <UserProvider>
      <MFALiteProvider>
        <Router>
          <Routes>
            <Route path="/" element={<Home />} /> {/* Set Home as the default */}
            <Route path="/home" element={<Home />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/adminproducts" element={<UserProductAccess />} />
            <Route path="/mfalite" element={<MFALite signOut={signOut} />} />
            <Route path="/cloneselectmfa" element={<CloneSelectMFA signOut={signOut} />} />
            <Route path="/file" element={<SimpleFileUpload signOut={signOut} />} />
            <Route path="*" element={<NotFoundPage />} /> {/* Catch-all route for 404s */}
          </Routes>
        </Router>
      </MFALiteProvider>
    </UserProvider>
  );
}

export default App
