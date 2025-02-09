import React, { createContext, useContext, useState, useEffect } from "react";

// Create the context
export const UserContext = createContext();

// Provider to wrap around your app
export const UserProvider = ({ children }) => {
  // Load user from sessionStorage if available
  const [userInfo, setUserInfo] = useState(() => {
    const storedUser = sessionStorage.getItem("userInfo");
    return storedUser ? JSON.parse(storedUser) : null;
  });

  // Save userInfo to sessionStorage whenever it changes
  useEffect(() => {
    if (userInfo) {
      sessionStorage.setItem("userInfo", JSON.stringify(userInfo));
    } else {
      sessionStorage.removeItem("userInfo"); // Clear sessionStorage on logout
    }
  }, [userInfo]);

  return (
    <UserContext.Provider value={{ userInfo, setUserInfo }}>
      {children}
    </UserContext.Provider>
  );
};

// Custom hook for accessing the user context
export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error("useUser must be used within a UserProvider");
  }
  return context;
};
