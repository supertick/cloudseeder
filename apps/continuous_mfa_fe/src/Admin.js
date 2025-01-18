import React from 'react';
import TopMenuBar from './TopMenuBar';
import { useUser } from './UserContext';
import {
  Paper,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Avatar,
} from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';

const mockUserData = [
  { fullName: 'John Doe', lastLoggedIn: '2025-01-15 08:45 AM', errors: 1, success: 45, role: 'Admin' },
  { fullName: 'Jane Smith', lastLoggedIn: '2025-01-14 06:30 PM', errors: 0, success: 32, role: 'User' },
  { fullName: 'Alice Johnson', lastLoggedIn: '2025-01-13 01:15 PM', errors: 2, success: 58, role: 'User' },
  { fullName: 'Robert Brown', lastLoggedIn: '2025-01-12 10:05 AM', errors: 3, success: 20, role: 'User' },
  { fullName: 'Emily Davis', lastLoggedIn: '2025-01-11 07:25 PM', errors: 0, success: 67, role: 'User' },
];

export default function Admin() {
  const { userInfo } = useUser();

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
      <TopMenuBar />
      <div
        style={{
          textAlign: 'center',
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          padding: '20px',
          borderRadius: '10px',
          width: '90%',
          maxWidth: '1200px',
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
        }}
      >
        <h1>Admin</h1>
        <h2>User List</h2>
        {/* MUI Paper Table */}
        <Paper
          style={{
            margin: '20px auto',
            padding: '20px',
            boxShadow: 'none',
            backgroundColor: 'rgba(255, 255, 255, 0.9)',
          }}
        >
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Profile</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Full Name</TableCell>
                <TableCell>Last Logged In</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Errors</TableCell>
                <TableCell>Success</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockUserData.map((user, index) => {
                const email = `${user.fullName.toLowerCase().replace(' ', '.')}@metalyticsbio.com`;
                return (
                  <TableRow key={index}>
                    <TableCell>
                      <Avatar>
                        <PersonIcon /> {/* Blank person icon */}
                      </Avatar>
                    </TableCell>
                    <TableCell>
                      <a href={`mailto:${email}`} style={{ textDecoration: 'none', color: '#1976d2' }}>
                        {email}
                      </a>
                    </TableCell>
                    <TableCell>{user.fullName}</TableCell>
                    <TableCell>{user.lastLoggedIn}</TableCell>
                    <TableCell>{user.role}</TableCell>
                    <TableCell>{user.errors}</TableCell>
                    <TableCell>{user.success}</TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </Paper>
        <p>Version 0.0.7</p>
      </div>
    </div>
  );
}
