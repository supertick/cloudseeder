import React from 'react';
import { styled } from '@mui/system';
import { Link, useNavigate } from 'react-router-dom';
import IconButton from '@mui/material/IconButton';
import LogoutIcon from '@mui/icons-material/Logout';
import { useUser } from './UserContext';

const TopMenuBarContainer = styled('div')({
  width: '100%',
  height: '50px',
  backgroundColor: '#2f3f5c',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '0 20px',
  color: '#fff',
  position: 'absolute',
  top: 0,
});

const Logo = styled('img')({
  height: '40px',
});

const UserInfo = styled('div')({
  display: 'flex',
  alignItems: 'center',
  fontSize: '16px',
});

const UserName = styled('span')({
  marginRight: '10px',
});

const NavMenu = styled('nav')({
  display: 'flex',
  gap: '20px',
  alignItems: 'center',
});

const MenuLink = styled(Link)({
  color: '#fff',
  textDecoration: 'none',
  fontSize: '16px',
  '&:hover': {
    textDecoration: 'underline',
  },
});

export default function TopMenuBar() {
  const { userInfo, signOut } = useUser();
  const navigate = useNavigate();

  // Check if the user has an admin role
  const isAdmin = userInfo?.roles?.includes("admin");

  // Enhanced logout function
  const handleLogout = () => {
    sessionStorage.clear(); // Clears all stored session data
    // signOut(); // Call the existing signOut function from context
    navigate('/login'); // Redirect to login page
  };

  return (
    <TopMenuBarContainer>
      <Link to="/">
        <Logo src="/Metalytics-Logo_light.webp" alt="logo" />
      </Link>
      <NavMenu>
        {isAdmin && (
          <>
            <MenuLink to="/users">Users</MenuLink>
            <MenuLink to="/products">Products</MenuLink>
          </>
        )}
        <MenuLink to={`/reports/${userInfo?.id}`}>My Reports</MenuLink>
      </NavMenu>
      <UserInfo>
        <UserName>{userInfo?.email}</UserName>
        <IconButton onClick={handleLogout} color="inherit">
          <LogoutIcon />
        </IconButton>
      </UserInfo>
    </TopMenuBarContainer>
  );
}
