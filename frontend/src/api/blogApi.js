import axios from './axios';

export const getPostsList = async (queryString = '') => {
    try {
        const url = queryString ? `/blog/posts/?${queryString}` : '/blog/posts/';
        const response = await axios.get(url);
        return response.data;
    } catch (error) {
        console.error("Error fetching blog posts:", error);
        throw error;
    }
};

export const getBlogCategories = async () => {
    try {
        const response = await axios.get('/blog/categories/');
        return response.data;
    } catch (error) {
        console.error("Error fetching blog categories:", error);
        return [];
    }
};

export const getPostDetail = async (slug) => {
    try {
        const response = await axios.get(`/blog/posts/${slug}/`);
        return response.data;
    } catch (error) {
        console.error("Error fetching post detail:", error);
        throw error;
    }
};

export const submitPostComment = async (slug, data) => {
    try {
        const response = await axios.post(`/blog/posts/${slug}/add_comment/`, data);
        return response.data;
    } catch (error) {
        console.error("Error submitting post comment:", error);
        throw error;
    }
};

export const getSiteSettings = async () => {
    try {
        const response = await axios.get('/home/settings/');
        return response.data;
    } catch (error) {
        console.error("Error fetching site settings:", error);
        return { site_name: 'فروشگاه' };
    }
};