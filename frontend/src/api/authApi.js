import axiosInstance from './axios';

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