// apiClient.js

const BASE_URL = process.env.REACT_APP_API_BASE_URL || `${window.location.origin}/v1`;

let jwtToken = null;

const handleError = (error) => {
  console.error('API Client Error:', error);
  alert(`An error occurred: ${error.message}`);
  throw error; // Re-throw the error so it can be handled further if needed
};

const logRequest = (method, url, options) => {
  console.info(`HTTP ${method} Request to: ${BASE_URL}${url}`);
  console.info('Options:', options);
};

const apiClient = {
  setToken(token) {
    jwtToken = token;
  },

  clearToken() {
    jwtToken = null;
  },

  async get(url) {
    const options = {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(jwtToken && { Authorization: `Bearer ${jwtToken}` }),
      },
    };
    logRequest('GET', url, options);

    try {
      const response = await fetch(`${BASE_URL}${url}`, options);

      if (!response.ok) {
        throw new Error(`GET request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      handleError(error);
    }
  },

  async post(url, data) {
    const options = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(jwtToken && { Authorization: `Bearer ${jwtToken}` }),
      },
      body: JSON.stringify(data),
    };
    logRequest('POST', url, options);

    try {
      const response = await fetch(`${BASE_URL}${url}`, options);

      if (!response.ok) {
        throw new Error(`POST request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      handleError(error);
    }
  },

  async put(url, data) {
    const options = {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(jwtToken && { Authorization: `Bearer ${jwtToken}` }),
      },
      body: JSON.stringify(data),
    };
    logRequest('PUT', url, options);

    try {
      const response = await fetch(`${BASE_URL}${url}`, options);

      if (!response.ok) {
        throw new Error(`PUT request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      handleError(error);
    }
  },

  async delete(url) {
    const options = {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...(jwtToken && { Authorization: `Bearer ${jwtToken}` }),
      },
    };
    logRequest('DELETE', url, options);

    try {
      const response = await fetch(`${BASE_URL}${url}`, options);

      if (!response.ok) {
        throw new Error(`DELETE request failed with status ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      handleError(error);
    }
  },

  async head(url) {
    const options = {
      method: 'HEAD',
      headers: {
        'Content-Type': 'application/json',
        ...(jwtToken && { Authorization: `Bearer ${jwtToken}` }),
      },
    };
    logRequest('HEAD', url, options);

    try {
      const response = await fetch(`${BASE_URL}${url}`, options);

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
