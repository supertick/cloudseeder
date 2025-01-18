import React, { createContext, useState, useEffect, useContext } from 'react'
import { fetchAuthSession, getCurrentUser, signOut as amplifySignOut } from '@aws-amplify/auth'

const UserContext = createContext()

export const UserProvider = ({ children }) => {
  const [userInfo, setUserInfo] = useState(null)

  useEffect(() => {
    const fetchUserDetails = async () => {
      try {
        // const userInfo = await getCurrentUser()
        // const session = await fetchAuthSession()

        const userInfo = {
          username: 'admin@scribble.ai',
          email: 'admin@scribble.ai',
          signInDetails: {
            signInUserSession: {
              accessToken: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBzY3JpYmJsZS5haSIsImV4cCI6MTczNjk4OTgyOH0.Ufr-KYpBGSSUCwLHJEO1tMmTgZes43kgFqvMGMj-fU8',  
              idToken: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbkBzY3JpYmJsZS5haSIsImV4cCI6MTczNjk4OTgyOH0.Ufr-KYpBGSSUCwLHJEO1tMmTgZes43kgFqvMGMj-fU8',
            },
          },
        }
        const session = {
          tokens: {
            idToken: {
              payload: {
                'cognito:groups': ['admin'],
              },
            },
          }
        }

        if (!userInfo || !session) return

        const groups = session.tokens.idToken.payload['cognito:groups'] || []
        const dynamicGroups = groups.reduce((acc, group) => {
          acc[`has${group}`] = true
          return acc
        }, {})

        setUserInfo({
          username: userInfo.username,
          signInDetails: userInfo.signInDetails,
          idToken: session.tokens.idToken,
          accessToken: session.tokens.accessToken,
          // Add the initial run state variables
          runMFALite: true,
          runCloneSelectMFA: true,
          runTimeSegmentedMFA: true,
          runBioInterpreter: true,
          runCoreMFAtoMFALite: true,
          ...dynamicGroups,
        })
        console.log(userInfo)
        console.log(session)
      } catch (error) {
        console.error('Error fetching user info:', error)
      }
    }

    fetchUserDetails()
  }, [])

  const updateRunState = (key, value) => {
    setUserInfo((prev) => ({ ...prev, [key]: value }))
  }

  const signOut = async () => {
    try {
      await amplifySignOut()
      setUserInfo(null)
    } catch (error) {
      console.error('Error signing out:', error)
    }
  }

  return (
    <UserContext.Provider value={{ userInfo, updateRunState, signOut }}>
      {children}
    </UserContext.Provider>
  )
}

// Custom hook to access user data
export const useUser = () => useContext(UserContext)
