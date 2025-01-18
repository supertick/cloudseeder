import React from 'react'
import { styled } from '@mui/system'
import { Link } from 'react-router-dom'
import IconButton from '@mui/material/IconButton'
import LogoutIcon from '@mui/icons-material/Logout'
import { useUser } from './UserContext' // assuming UserContext.js is in the same directory

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
  top: 0
})

const Logo = styled('img')({
  height: '40px'
})

const UserInfo = styled('div')({
  display: 'flex',
  alignItems: 'center',
  fontSize: '16px'
})

const UserName = styled('span')({
  marginRight: '10px'
})

export default function TopMenuBar() {
  const { userInfo, signOut } = useUser()

  return (
    <TopMenuBarContainer>
      <Link to="/">
        <Logo src="/Metalytics-Logo_light.webp" alt="logo" />
      </Link>
      <UserInfo>
        <UserName>{JSON.stringify(userInfo)}</UserName>
        <UserName>{userInfo?.username}</UserName>
        <IconButton onClick={signOut} color="inherit">
          <LogoutIcon />
        </IconButton>
      </UserInfo>
    </TopMenuBarContainer>
  )
}
