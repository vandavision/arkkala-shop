import axiosInstance from './axios';

export const getProductDetail = async (productId) => {
    const response = await axiosInstance.get(`shop/products/${productId}/`);
    return response.data;
};

export const submitComment = async (productId, data) => {
    const response = await axiosInstance.post(`shop/products/${productId}/add_comment/`, data);
    return response.data;
};