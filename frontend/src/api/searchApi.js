import axiosInstance from './axios';

export const getCategoryTree = async () => {
    const response = await axiosInstance.get('search/categories/tree/');
    return response.data;
};

export const globalSearch = async (query) => {
    const response = await axiosInstance.get(`search/global/?q=${query}`);
    return response.data;
};

export const getBrandsList = async () => {
    const response = await axiosInstance.get('search/brands/');
    return response.data;
};