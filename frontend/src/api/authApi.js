import axiosInstance from './axios';

export const loginUser = async (email, password) => {
    const response = await axiosInstance.post('users/login/', { email, password });
    if (response.data.access) {
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
    }
    return response.data;
};

export const registerUser = async (userData) => {
    const response = await axiosInstance.post('users/register/', userData);
    return response.data;
};

export const getUserProfile = async () => {
    const response = await axiosInstance.get('users/profile/');
    return response.data;
};