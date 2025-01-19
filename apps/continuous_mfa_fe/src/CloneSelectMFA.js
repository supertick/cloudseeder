// src/CloneSelectMFA.js
import React, { useEffect, useState } from 'react'
import { useUser } from './UserContext'
import TopMenuBar from './TopMenuBar'
import FileUploadSection from './FileUploadSection'
import ReportTable from './ReportTable'

export default function CloneSelectMFA({ signOut }) {
  const {userInfo } = useUser()


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
      <TopMenuBar/>
      <div
        style={{
          textAlign: 'center',
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          padding: '20px',
          borderRadius: '10px',
          width: '80%'
        }}
      >
        {/* Flex container for image and button on the same row */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <img src="/CloneSelectMFA-Aug2024.png" alt="CloneSelectMFA" width="300" style={{ margin: '10px' }} />
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', marginLeft: '20px' }}>
          </div>
        </div>


        <div style={{ marginTop: '40px' }}>
        </div>
      </div>
    </div>
  )
}
