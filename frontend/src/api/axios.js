import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/';

const axiosInstance = axios.create({
    baseURL: baseURL,
    timeout: 15000,
    headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    },
});

axiosInstance.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers['Authorization'] = 'Bearer ' + token;
        } else {
            delete config.headers['Authorization'];
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

axiosInstance.interceptors.response.use(
    (response) => {
        return response;
    },
    async (error) => {
        const originalRequest = error.config;
        
        if (!error.response) {
            console.error("ارتباط با سرور قطع شده است. بررسی کنید که بک‌اند روی 0.0.0.0:8000 ران باشد.");
            return Promise.reject(error);
        }

        if (error.response.status === 401 && !originalRequest._retry && !originalRequest.url.includes('token/refresh')) {
            originalRequest._retry = true;
            const refreshToken = localStorage.getItem('refresh_token');
            
            if (refreshToken) {
                try {
                    const response = await axios.post(`${baseURL}users/token/refresh/`, {
                        refresh: refreshToken
                    });
                    
                    const newAccessToken = response.data.access;
                    localStorage.setItem('access_token', newAccessToken);
                    
                    axiosInstance.defaults.headers['Authorization'] = 'Bearer ' + newAccessToken;
                    originalRequest.headers['Authorization'] = 'Bearer ' + newAccessToken;
                    
                    return axiosInstance(originalRequest);
                } catch (err) {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    delete axiosInstance.defaults.headers['Authorization'];
                    window.location.href = '/login';
                }
            } else {
                localStorage.removeItem('access_token');
                delete axiosInstance.defaults.headers['Authorization'];
                window.location.href = '/login';
            }
        }
        return Promise.reject(error);
    }
);

export default axiosInstance;