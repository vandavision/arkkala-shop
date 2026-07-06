import axios from './axios';

export const getCategoryTree = async () => {
    try {
        const response = await axios.get('search/categories/tree/');
        return response.data;
    } catch (error) {
        console.error("Error fetching categories:", error);
        return [];
    }
};

export const getBrandsList = async () => {
    try {
        const response = await axios.get('/search/brands/');
        return response.data;
    } catch (error) {
        console.error("Error fetching brands:", error);
        return [];
    }
};


export const globalSearch = async (query) => {
    try {
        const response = await axios.get(`search/global/?q=${encodeURIComponent(query)}&limit=4`);
        return response.data;
    } catch (error) {
        console.error("Error performing global search:", error);
        return null;
    }
};