// apiClient.js

const isBrowser = typeof window !== 'undefined'

const defaultBaseUrl = isBrowser
    ? `${window.location.protocol}//${window.location.hostname}:8000`
    : process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'

// Default configuration
const DEFAULT_TIMEOUT = 120000; //  2 minutes
const MAX_RETRIES = 3;
const RETRY_DELAY = 1000; // 1 second

class ApiError extends Error {
    constructor(status, message, details = null) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.details = details;

        // Ensure the error is properly serializable
        this.toJSON = function () {
            return {
                name: this.name,
                message: this.message,
                status: this.status,
                details: this.details
            };
        };
    }
}

class ApiClient {
    constructor(baseUrl = defaultBaseUrl) {
        // Remove trailing slash if present
        this.baseUrl = baseUrl.replace(/\/$/, '');
        this.timeout = DEFAULT_TIMEOUT;
        this.maxRetries = MAX_RETRIES;
        this.retryDelay = RETRY_DELAY;
    }

    buildUrl(endpoint, queryParams = {}) {
        // Remove leading slash if present
        const cleanEndpoint = endpoint.replace(/^\//, '');
        let url;

        try {
            url = new URL(`${this.baseUrl}/${cleanEndpoint}`);
        } catch (e) {
            console.error('Failed to construct URL:', e);
            throw new Error(`Invalid URL: ${this.baseUrl}/${cleanEndpoint}`);
        }

        // Add query parameters
        Object.entries(queryParams).forEach(([key, value]) => {
            if (value !== undefined && value !== null) {
                url.searchParams.append(key, value.toString());
            }
        });

        return url.toString();
    }

    async request(endpoint, options = {}, queryParams = {}) {
        const url = this.buildUrl(endpoint, queryParams);
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };

        let attempt = 0;
        let lastError = null;

        while (attempt < this.maxRetries) {
            try {
                console.log(`Making request to: ${url} (attempt ${attempt + 1}/${this.maxRetries})`, {
                    method: options.method,
                    headers,
                    body: options.body
                });

                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), this.timeout);

                const response = await fetch(url, {
                    ...options,
                    headers,
                    signal: controller.signal
                });

                clearTimeout(timeoutId);

                let responseData;
                let responseText;

                try {
                    // Always get the text first
                    responseText = await response.text();

                    // Try to parse as JSON if possible
                    if (responseText) {
                        try {
                            responseData = JSON.parse(responseText);
                        } catch {
                            responseData = responseText;
                        }
                    }
                } catch {
                    responseText = response.statusText;
                    responseData = responseText;
                }

                if (!response.ok) {
                    const errorMessage = typeof responseData === 'object'
                        ? responseData.error || responseData.message || responseData.detail || 'Unknown error'
                        : responseData;

                    throw new ApiError(
                        response.status,
                        errorMessage,
                        {
                            url,
                            method: options.method,
                            responseData,
                            attempt: attempt + 1
                        }
                    );
                }

                return responseData;
            } catch (error) {
                lastError = error;
                attempt++;

                const errorDetails = {
                    url,
                    method: options.method || 'GET',
                    attempt,
                    maxRetries: this.maxRetries,
                    error: error.message,
                    status: error.status,
                    details: error.details || {}
                };

                // If it's an abort error (timeout), create a more descriptive error
                if (error.name === 'AbortError') {
                    console.error(`Request timed out after ${this.timeout}ms`, errorDetails);
                    if (attempt === this.maxRetries) {
                        throw new ApiError(
                            408,
                            `Request timed out after ${this.maxRetries} attempts`,
                            errorDetails
                        );
                    }
                } else if (attempt === this.maxRetries) {
                    console.error('API Request failed:', errorDetails);
                    throw new ApiError(
                        error.status || 500,
                        error.message || 'Request failed',
                        errorDetails
                    );
                }

                console.warn(`Request attempt ${attempt} failed, retrying in ${this.retryDelay}ms`, errorDetails);
                await new Promise(resolve => setTimeout(resolve, this.retryDelay));
            }
        }

        // This shouldn't be reached, but just in case
        throw lastError || new ApiError(500, 'Request failed after all retries');
    }

    async get(endpoint, queryParams = {}) {
        return this.request(endpoint, {
            method: 'GET'
        }, queryParams);
    }

    async post(endpoint, body = null) {
        const url = this.baseUrl + endpoint;
        console.log(`[ApiClient] Making POST request to ${url}`);
        console.log('[ApiClient] Request body:', JSON.stringify(body, null, 2));

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(body),
            });

            console.log(`[ApiClient] Response status: ${response.status}`);
            const responseText = await response.text();
            console.log('[ApiClient] Raw response:', responseText);

            let responseData;
            try {
                responseData = JSON.parse(responseText);
            } catch (e) {
                console.error('[ApiClient] Failed to parse response as JSON:', e);
                throw new Error('Invalid JSON response');
            }

            console.log('[ApiClient] Parsed response:', JSON.stringify(responseData, null, 2));

            if (!response.ok) {
                const error = new Error('API request failed');
                error.status = response.status;
                error.details = responseData;
                throw error;
            }

            return responseData;
        } catch (error) {
            console.error('[ApiClient] Request error:', error);
            console.error('[ApiClient] Error details:', error.details);
            throw error;
        }
    }

    async put(endpoint, body, queryParams = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: body ? JSON.stringify(body) : undefined
        }, queryParams);
    }

    async patch(endpoint, body, queryParams = {}) {
        return this.request(endpoint, {
            method: 'PATCH',
            body: body ? JSON.stringify(body) : undefined
        }, queryParams);
    }

    async delete(endpoint, body, queryParams = {}) {
        return this.request(endpoint, {
            method: 'DELETE',
            body: body ? JSON.stringify(body) : undefined
        }, queryParams);
    }
}

export const apiClient = new ApiClient()
