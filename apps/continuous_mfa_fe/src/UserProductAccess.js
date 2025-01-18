import React from 'react';
import TopMenuBar from './TopMenuBar';
import { Paper, Switch, Table, TableHead, TableBody, TableRow, Avatar, TableCell, Typography, Box } from '@mui/material';
import PersonIcon from '@mui/icons-material/Person';

const user = {
  fullName: 'John Doe',
};

const products = [
  'Clone Select MFA',
  'MFALite',
  'Time Segmented MFA',
  'Bio Interpreter',
  'CoreMFA to MFALite',
  'BMS MFALite',
  'Perfuse MFALite',
];

export default function UserProductAccess() {
  // States for toggles
  const [productAccess, setProductAccess] = React.useState(
    products.reduce((acc, product) => ({ ...acc, [product]: { access: false, hidden: false } }), {})
  );

  const handleToggle = (product, field) => {
    setProductAccess((prevState) => ({
      ...prevState,
      [product]: {
        ...prevState[product],
        [field]: !prevState[product][field],
      },
    }));
  };

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100vh',
        backgroundColor: '#e3f2fd',
        paddingTop: '50px',
        flexDirection: 'column',
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
        <h1>User Product Access</h1>

        {/* User Info Section */}
        <Paper
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'flex-start',
            padding: '15px',
            marginBottom: '20px',
            borderRadius: '10px',
            boxShadow: '0 2px 5px rgba(0, 0, 0, 0.15)',
            maxWidth: '400px',
            margin: '0 auto',
          }}
        >
          <Avatar style={{ marginRight: '15px', backgroundColor: '#1976d2', color: '#fff' }}>
            <PersonIcon />
          </Avatar>
          <Typography variant="h6" style={{ fontWeight: 'bold' }}>
            {user.fullName} Admin
          </Typography>
        </Paper>

        {/* Products Table */}
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
                <TableCell>Product</TableCell>
                <TableCell align="center">Access</TableCell>
                <TableCell align="center">Hidden</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {products.map((product, index) => (
                <TableRow key={index}>
                  <TableCell>{product}</TableCell>
                  <TableCell align="center">
                    <Switch
                      checked={productAccess[product].access}
                      onChange={() => handleToggle(product, 'access')}
                      color="primary"
                    />
                  </TableCell>
                  <TableCell align="center">
                    <Switch
                      checked={productAccess[product].hidden}
                      onChange={() => handleToggle(product, 'hidden')}
                      color="secondary"
                    />
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      </div>
    </div>
  );
}
