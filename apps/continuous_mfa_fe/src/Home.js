// src/Home.js
import React from 'react'
import { Link } from 'react-router-dom'
import TopMenuBar from './TopMenuBar'
import { useUser } from './UserContext'

export default function Home() {
  // Get user info from the UserContext
  const { userInfo } = useUser()

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: '#b3e5fc',
        backgroundImage: 'url(/freeze_data.png)',
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        paddingTop: '50px'
      }}
    >
      <TopMenuBar />
      <div
        style={{
          textAlign: 'center',
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          padding: '20px',
          borderRadius: '10px'
        }}
      >
        <h1>Welcome to Continuous MFA</h1>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginBottom: '20px' }}>
          {/* Hyperlinked image for /mfalite */}
          <Link to="/mfalite">
            <img src="/MFAlite.png" alt="MFALite" width="300" style={{ margin: '10px' }} />
          </Link>

          {/* Hyperlinked image for /cloneselectmfa */}
          <Link to="/cloneselectmfa">
            <img src="/CloneSelectMFA.png" alt="CloneSelectMFA" width="300" style={{ margin: '10px' }} />
          </Link>
        </div>

        <p>version 0.0.6</p>
      </div>
    </div>
  )
}
