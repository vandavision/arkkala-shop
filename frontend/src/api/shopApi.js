import axios from './axios';

export const getProductsList = async (queryString = '') => {
    try {
        const url = queryString ? `/shop/products/?${queryString}` : '/shop/products/';
        const response = await axios.get(url);
        return response.data;
    } catch (error) {
        console.error("Error fetching products:", error);
        throw error;
    }
};

export const getProductDetail = async (identifier) => {
    try {
        const response = await axios.get(`/shop/products/${identifier}/`);
        return response.data;
    } catch (error) {
        console.error("Error fetching product detail:", error);
        throw error;
    }
};

export const getMaxPrice = async () => {
    try {
        const response = await axios.get('/shop/max-price/');
        return response.data.max_price;
    } catch (error) {
        console.error("Error fetching max price:", error);
        return 50000000; 
    }
};

export const submitComment = async (identifier, commentData) => {
    try {
        const response = await axios.post(`/shop/products/${identifier}/add_comment/`, commentData);
        return response.data;
    } catch (error) {
        console.error("Error submitting comment:", error);
        throw error;
    }
};

export const submitQuestion = async (productSlug, questionData) => {
    try {
        const response = await axios.post(`/shop/products/${productSlug}/add_question/`, questionData);
        return response.data;
    } catch (error) {
        console.error("Error submitting question:", error);
        throw error;
    }
};

export const toggleFavorite = async (identifier) => {
    try {
        const response = await axios.post(`/shop/products/${identifier}/toggle_favorite/`);
        return response.data;
    } catch (error) {
        console.error("Error toggling favorite:", error);
        throw error;
    }
};

export const getFavoritesList = async (queryString = '') => {
    try {
        const url = queryString ? `/shop/products/favorites/?${queryString}` : '/shop/products/favorites/';
        const response = await axios.get(url);
        return response.data;
    } catch (error) {
        console.error("Error fetching favorites:", error);
        throw error;
    }
};

export const getUserComments = async (queryString = '') => {
    try {
        const url = queryString ? `/shop/comments/my_comments/?${queryString}` : '/shop/comments/my_comments/';
        const response = await axios.get(url);
        return response.data;
    } catch (error) {
        console.error("Error fetching user comments:", error);
        throw error;
    }
};