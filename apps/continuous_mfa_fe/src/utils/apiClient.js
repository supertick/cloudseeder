// apiClient.js

const BASE_URL = process.env.REACT_APP_API_BASE_URL || `${window.location.origin}/v1`;

let jwtToken = null;

const handleError = (error) => {
  console.error('API Client Error:', error);
  alert(`An error occurred: ${error.message}`);
  throw error; // Re-throw the error so it can be handled further if needed
};

const apiClient = {
  setToken(token) {
    jwtToken = token;
  },

  clearToken() {
    jwtToken = null;
  },

  async get(url) {
    try {
      const response = await fetch(`${BASE_URL}${url}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...(jwtToken && { Authorization: `Bearer ${jwtToken}` }),
        },
      });

      if (!response.ok) {
        throw new Error(`GET request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      handleError(error);
    }
  },

  async post(url, data) {
    try {
      const response = await fetch(`${BASE_URL}${url}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(jwtToken && { Authorization: `Bearer ${jwtToken}` }),
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`POST request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      handleError(error);
    }
  },

  async put(url, data) {
    try {
      const response = await fetch(`${BASE_URL}${url}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(jwtToken && { Authorization: `Bearer ${jwtToken}` }),
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`PUT request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      handleError(error);
    }
  },

  async delete(url) {
    try {
      const response = await fetch(`${BASE_URL}${url}`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          ...(jwtToken && { Authorization: `Bearer ${jwtToken}` }),
        },
      });

      if (!response.ok) {
        throw new Error(`DELETE request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      handleError(error);
    }
  },

  async head(url) {
    try {
      const response = await fetch(`${BASE_URL}${url}`, {
        method: 'HEAD',
        headers: {
          'Content-Type': 'application/json',
          ...(jwtToken && { Authorization: `Bearer ${jwtToken}` }),
        },
      });

      if (!response.ok) {
        throw new Error(`HEAD request failed with status ${response.status}`);
      }

      return response.headers;
    } catch (error) {
      handleError(error);
    }
  },
};

export default apiClient;
