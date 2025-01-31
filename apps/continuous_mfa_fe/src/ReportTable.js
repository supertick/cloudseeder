import React, { useEffect, useCallback, useState } from 'react'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableContainer from '@mui/material/TableContainer'
import TableHead from '@mui/material/TableHead'
import TableRow from '@mui/material/TableRow'
import Paper from '@mui/material/Paper'
import Tooltip from '@mui/material/Tooltip'
import IconButton from '@mui/material/IconButton'
import TableSortLabel from '@mui/material/TableSortLabel'
import DeleteIcon from '@mui/icons-material/Delete'
import DownloadIcon from '@mui/icons-material/Download'
import { useMFALite } from './MFALiteContext'
import { useUser } from './UserContext'
import apiClient from './utils/apiClient'

export default function ReportTable() {
  const { reports, setReports, mfaStatus } = useMFALite()
  const { userInfo } = useUser()

  const [sortColumn, setSortColumn] = useState('start_datetime')
  const [sortDirection, setSortDirection] = useState('desc') // Default: latest first

  // const fetchReports = useCallback(async () => {
  //   try {
  //     const restOperation = post({
  //       apiName: 'MetalyticsApi',
  //       path: '/listReports',
  //       options: {
  //         body: {
  //           xlsFileName: '',
  //           email: userInfo?.signInDetails?.loginId,
  //           debug: false
  //         },
  //         responseType: 'blob'
  //       }
  //     })

  //     const { body } = await restOperation.response
  //     const response = await body.json()
  //     setReports(response)
  //   } catch (error) {
  //     console.error('Error listing reports:', error)
  //   }
  // }, [userInfo, setReports])

  const fetchReports = async () => {
    const response = await apiClient.get('/reports')
    setReports(response)
  }

  useEffect(() => {
    fetchReports()
    if (userInfo?.signInDetails?.loginId) {
      fetchReports()
      
      const interval = setInterval(fetchReports, 5000)
      return () => clearInterval(interval)
    }
  }, [])

  const handleDownload = async (filename) => {
    try {
      const safeName = userInfo.signInDetails.loginId.replace(/[@.]/g, '_')
      const path = `public/reports/${safeName}/${filename}`
      const downloadUrl = null // await getUrl({ path })
      window.location.href = downloadUrl.url.href
    } catch (error) {
      console.error('Error downloading report:', error)
    }
  }

  const handleDelete = async (filename) => {
    try {
      // const restOperation = post({
      //   apiName: 'MetalyticsApi',
      //   path: '/deleteReport',
      //   options: {
      //     body: {
      //       filename,
      //       email: userInfo?.signInDetails?.loginId,
      //       debug: false
      //     }
      //   }
      // })
      // await restOperation
      fetchReports()
    } catch (error) {
      console.error('Error deleting report:', error)
    }
  }

  function formatDateToLocal(isoDateString) {
    const date = new Date(isoDateString)
    const options = {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    }
    return date.toLocaleString('en-US', options).replace(',', '')
  }

  const handleSort = (column) => {
    const isAsc = sortColumn === column && sortDirection === 'asc'
    setSortColumn(column)
    setSortDirection(isAsc ? 'desc' : 'asc')
  }

  const sortedReports = [...reports]
    .filter(report => !(report.title.endsWith('log') && !userInfo.hasAdmin))
    .sort((a, b) => {
      let valueA, valueB
      if (sortColumn === 'title') {
        valueA = a.title.toLowerCase()
        valueB = b.title.toLowerCase()
      } else if (sortColumn === 'start_datetime') {
        valueA = new Date(a.start_datetime).getTime()
        valueB = new Date(b.start_datetime).getTime()
      }

      if (valueA < valueB) return sortDirection === 'asc' ? -1 : 1
      if (valueA > valueB) return sortDirection === 'asc' ? 1 : -1
      return 0
    })

  return (
    <>
      {mfaStatus && (
        <div style={{ marginTop: '10px', fontWeight: 'bold', color: '#2f3f5c' }}>
          {mfaStatus}
        </div>
      )}
      <TableContainer component={Paper} style={{ marginTop: '20px' }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell sx={{ backgroundColor: '#82A8C8', color: '#25344B' }}></TableCell>
              <TableCell
                sx={{ backgroundColor: '#82A8C8', color: '#25344B' }}
                onClick={() => handleSort('title')}
              >
                <TableSortLabel active={sortColumn === 'title'} direction={sortDirection}>
                  Report Name
                </TableSortLabel>
              </TableCell>
              <TableCell
                sx={{ backgroundColor: '#82A8C8', color: '#25344B' }}
                onClick={() => handleSort('start_datetime')}
              >
                <TableSortLabel active={sortColumn === 'start_datetime'} direction={sortDirection}>
                  Processing Date
                </TableSortLabel>
              </TableCell>
              <TableCell sx={{ backgroundColor: '#82A8C8', color: '#25344B' }} align="right">
                Download
              </TableCell>
              <TableCell sx={{ backgroundColor: '#82A8C8', color: '#25344B' }} align="right">
                Delete
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedReports.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center">
                  No reports available
                </TableCell>
              </TableRow>
            ) : (
              sortedReports.map((report) => (
                <TableRow key={report.id}>
                  <TableCell>
                    {(report.title.endsWith('.xlsx') || report.title.endsWith('.xls')) && (
                      <img src="/processing.gif" alt="report" width="30" />
                    )}
                  </TableCell>
                  <TableCell component="th" scope="row">
                    {report.title}
                  </TableCell>
                  <TableCell>{formatDateToLocal(report.start_datetime)}</TableCell>
                  <TableCell align="right">
                    {!report.title.endsWith('.xlsx') && (
                      <Tooltip title="Download">
                        <IconButton onClick={() => handleDownload(report.title)}>
                          <DownloadIcon />
                        </IconButton>
                      </Tooltip>
                    )}
                  </TableCell>
                  <TableCell align="right">
                    <Tooltip title="Delete">
                      <IconButton onClick={() => handleDelete(report.title)}>
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  )
}
