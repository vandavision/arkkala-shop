// arkkala/frontend/src/api/authApi.js
import axiosInstance from './axios';

export const getAuthConfig = async () => {
    const response = await axiosInstance.get('users/auth-config/');
    return response.data;
};

export const loginWithEmail = async (email, password) => {
    const response = await axiosInstance.post('users/login/', { email, password });
    if (response.data.access) {
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
    }
    return response.data;
};

export const registerWithEmail = async (userData) => {
    const response = await axiosInstance.post('users/register/', userData);
    return response.data;
};

export const requestPasswordReset = async (email) => {
    const response = await axiosInstance.post('users/password-reset/request/', { email });
    return response.data;
};

export const confirmPasswordReset = async (data) => {
    const response = await axiosInstance.post('users/password-reset/confirm/', data);
    return response.data;
};

export const sendOtp = async (phone_number) => {
    const response = await axiosInstance.post('users/otp/send/', { phone_number });
    return response.data;
};

export const verifyOtp = async (phone_number, code) => {
    const response = await axiosInstance.post('users/otp/verify/', { phone_number, code });
    if (response.data.access) {
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
    }
    return response.data;
};

export const getUserProfile = async () => {
    const response = await axiosInstance.get('users/profile/');
    return response.data;
};

export const updateUserProfile = async (userData) => {
    const isFormData = userData instanceof FormData;
    const headers = isFormData ? { 'Content-Type': 'multipart/form-data' } : {};
    
    const response = await axiosInstance.patch('users/profile/', userData, { headers });
    return response.data;
};

export const getUserAddresses = async () => {
    const response = await axiosInstance.get('users/addresses/');
    return response.data;
};

export const addUserAddress = async (data) => {
    const response = await axiosInstance.post('users/addresses/', data);
    return response.data;
};

export const deleteUserAddress = async (id) => {
    const response = await axiosInstance.delete(`users/addresses/${id}/`);
    return response.data;
};

export const setDefaultAddress = async (id) => {
    const response = await axiosInstance.post(`users/addresses/${id}/set_default/`);
    return response.data;
};