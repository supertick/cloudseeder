import React from 'react';
import { styled } from '@mui/system';
import { Link, useNavigate } from 'react-router-dom';
import IconButton from '@mui/material/IconButton';
import LogoutIcon from '@mui/icons-material/Logout';
import { useUser } from './UserContext';

const TopMenuBarContainer = styled('div')({
  width: '99%',
  height: '50px',
  backgroundColor: '#2f3f5c',
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  padding: '0 20px',
  color: '#fff',
  position: 'fixed',  // ⬅️ Changed from "absolute" to "fixed"
  top: 0,
  left: 0,
  zIndex: 1000,       // ⬅️ Ensures it stays above other content
  boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)', // Optional: adds shadow effect
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
  const { userInfo, setUserInfo } = useUser();
  const navigate = useNavigate();

  const isAdmin = userInfo?.roles?.includes("admin");

  const handleLogout = () => {
    setUserInfo(null)
    navigate('/login');
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
        </IconButton>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
      </UserInfo>
    </TopMenuBarContainer>
  );
}
