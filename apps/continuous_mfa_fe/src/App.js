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
import Login from './Login'
import { AppProvider } from "./AppContext";
import Product from './Product'

function App({ signOut }) {
  return (
    <UserProvider>
      <AppProvider>
      <MFALiteProvider>
        <Router>
          <Routes>
            <Route path="/" element={<Home />} /> {/* Set Home as the default */}
            <Route path="/home" element={<Home />} />
            <Route path="/users" element={<Admin />} />
            <Route path="/products" element={<Product />} />
            <Route path="/adminproducts" element={<UserProductAccess />} />
            <Route path="/mfalite" element={<MFALite signOut={signOut} />} />
            <Route path="/cloneselectmfa" element={<CloneSelectMFA signOut={signOut} />} />
            <Route path="/file" element={<SimpleFileUpload signOut={signOut} />} />
            <Route path="/login" element={<Login />} /> {/* Catch-all route for 404s */}
            <Route path="*" element={<NotFoundPage />} /> {/* Catch-all route for 404s */}
          </Routes>
        </Router>
      </MFALiteProvider>
      </AppProvider>
    </UserProvider>
  );
}

export default App
