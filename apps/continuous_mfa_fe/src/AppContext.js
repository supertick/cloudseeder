import React, { createContext, useContext, useState } from "react";

// Create the context
export const AppContext = createContext();

// Provider to manage the global state
export const AppProvider = ({ children }) => {
  const [appData, setAppData] = useState({}); // Initialize as an empty dictionary

  // Function to update specific keys in the dictionary
  const setAppKey = (key, value) => {
    setAppData((prevData) => ({
      ...prevData,
      [key]: value,
    }));
  };

  return (
    <AppContext.Provider value={{ appData, setAppKey }}>
      {children}
    </AppContext.Provider>
  );
};

// Custom hook for accessing AppContext
export const useApp = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error("useApp must be used within an AppProvider");
  }
  return context;
};
