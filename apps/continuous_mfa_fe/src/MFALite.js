import React, { useState } from 'react'
import { useUser } from './UserContext'
import TopMenuBar from './TopMenuBar'
import ReportTable from './ReportTable'
import Radio from '@mui/material/Radio'
import RadioGroup from '@mui/material/RadioGroup'
import FormControlLabel from '@mui/material/FormControlLabel'
import Grid from '@mui/material/Grid'
import FileUploadSection from './FileUploadSection'

export default function MFALite({ signOut }) {
  const { userInfo, updateRunState } = useUser()
  const [selectedProduct, setSelectedProduct] = useState(null)

  if (!userInfo) {
    return null
  }

  const products = [
    { name: 'CloneSelectMFA', img: '/CloneSelectMFA.png' },
    { name: 'MFALite', img: '/MFAlite.png' },
    { name: 'TimeSegmentedMFA', img: '/TimeSegmentedMFA.png' },
    { name: 'BioInterpreter', img: '/BioInterpreter.png' },
    { name: 'CoreMFAtoMFALite', img: '/CoreMFAtoMFALite.png' },
    { name: 'BMSMFALite', img: '/BMSMFALite.png' },
    { name: 'PerfuseMFALite', img: '/PerfuseMFALite.png' },
  ]

  const imageStyle = (enabled, isSelected) => ({
    width: '230px',
    borderRadius: '15px',
    filter: !enabled ? 'grayscale(100%)' : 'none',
    opacity: !enabled ? 0.5 : 1,
    border: isSelected ? '4px solid #1976d2' : '4px solid transparent',
    cursor: enabled ? 'pointer' : 'not-allowed',
  })

  const handleProductSelection = (productName) => {
    setSelectedProduct(productName)
    products.forEach((product) => {
      const runKey = `run${product.name}`
      updateRunState(runKey, product.name === productName)
    })
  }

  const renderImageWithRadioButton = (product) => {
    const runKey = `run${product.name}`
    const hasKey = `has${product.name}`

    // Skip rendering if the user lacks permission for the product
    if (!userInfo[hasKey]) {
      return null
    }

    const isSelected = selectedProduct === product.name

    return (
      <div
        style={{ position: 'relative', textAlign: 'center', margin: '10px' }}
        key={product.name}
        onClick={() => userInfo[hasKey] && handleProductSelection(product.name)}
      >
        <img
          src={product.img}
          alt={product.name}
          style={imageStyle(userInfo[hasKey], isSelected)}
        />
        <FormControlLabel
          value={product.name}
          control={<Radio color="primary" />}
          label=""
          checked={isSelected}
          disabled={!userInfo[hasKey]}
        />
      </div>
    )
  }

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
        paddingTop: '50px',
      }}
    >
      <TopMenuBar userInfo={userInfo} />
      <div
        style={{
          textAlign: 'center',
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          padding: '20px',
          borderRadius: '15px',
          width: '80%',
          position: 'relative',
        }}
      >
        <h2>Select a product to run</h2>
        <Grid container spacing={2} justifyContent="space-between">
          <RadioGroup
            name="productSelection"
            value={selectedProduct}
            onChange={(event) => handleProductSelection(event.target.value)}
            style={{ display: 'flex', flexDirection: 'row', flexWrap: 'wrap' }}
          >
            {products.map(renderImageWithRadioButton)}
          </RadioGroup>
        </Grid>

        {selectedProduct && (
          <Grid item xs={12} sm={6} md={3}>
            <FileUploadSection />
          </Grid>
        )}

        <div style={{ marginTop: '40px', maxHeight: '800px', overflowY: 'auto' }}>
          <ReportTable />
        </div>
        <div style={{ marginTop: '20px' }}>0.9.5</div>
      </div>
    </div>
  )
}
