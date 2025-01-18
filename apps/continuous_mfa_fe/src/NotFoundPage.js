// src/NotFoundPage.js
import React from 'react'
import { Link } from 'react-router-dom'

const NotFoundPage = () => {
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        flexDirection: 'column',
        backgroundColor: '#b3e5fc',
        textAlign: 'center'
      }}
    >
      <h1 style={{ fontSize: '4rem', marginBottom: '20px' }}>404</h1>
      <h2 style={{ marginBottom: '20px' }}>Page Not Found</h2>
      <p>The page you are looking for does not exist.</p>
      <Link
        to="/"
        style={{
          marginTop: '20px',
          padding: '10px 20px',
          backgroundColor: '#2f3f5c',
          color: '#fff',
          textDecoration: 'none',
          borderRadius: '5px'
        }}
      >
        Go back to Home
      </Link>
    </div>
  )
}

export default NotFoundPage
