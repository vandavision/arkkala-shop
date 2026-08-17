import axiosInstance from './axios';

const getGuestId = () => {
    let guestId = localStorage.getItem('guest_id');
    if (!guestId) {
        guestId = 'guest_' + Math.random().toString(36).substring(2, 15) + Date.now().toString(36);
        localStorage.setItem('guest_id', guestId);
    }
    return guestId;
};

const getHeaders = () => ({
    headers: { 'X-Guest-ID': getGuestId() }
});

export const getProductsList = async (queryString = '') => {
    try {
        const url = queryString ? `/shop/products/?${queryString}` : '/shop/products/';
        const response = await axiosInstance.get(url);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getProductDetail = async (identifier) => {
    try {
        const response = await axiosInstance.get(`/shop/products/${identifier}/`, getHeaders());
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getMaxPrice = async () => {
    try {
        const response = await axiosInstance.get('/shop/max-price/');
        return response.data.max_price;
    } catch (error) {
        return 50000000;
    }
};

export const submitComment = async (identifier, commentData) => {
    try {
        const response = await axiosInstance.post(`/shop/products/${identifier}/add_comment/`, commentData);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const submitQuestion = async (productSlug, questionData) => {
    try {
        const response = await axiosInstance.post(`/shop/products/${productSlug}/add_question/`, questionData);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const toggleFavorite = async (identifier) => {
    try {
        const response = await axiosInstance.post(`/shop/products/${identifier}/toggle_favorite/`);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getFavoritesList = async (queryString = '') => {
    try {
        const url = queryString ? `/shop/products/favorites/?${queryString}` : '/shop/products/favorites/';
        const response = await axiosInstance.get(url);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getUserComments = async (queryString = '') => {
    try {
        const url = queryString ? `/shop/comments/?${queryString}` : '/shop/comments/';
        const response = await axiosInstance.get(url);
        return response.data;
    } catch (error) {
        throw error;
    }
};

export const getRecommendations = async () => {
    try {
        const response = await axiosInstance.get('/shop/products/recommendations/', getHeaders());
        return response.data.results || response.data;
    } catch (error) {
        return [];
    }
};