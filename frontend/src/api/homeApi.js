import axiosInstance from './axios';

export const getHomePageData = async () => {
    const response = await axiosInstance.get('home/');
    return response.data;
};

export const getSiteSettings = async () => {
    try {
        const response = await axiosInstance.get('home/settings/');
        return response.data;
    } catch (error) {
        console.error("Error fetching site settings:", error);
        return null;
    }
};

export const getFaqsList = async () => {
    try {
        const response = await axiosInstance.get('home/faq/');
        return response.data;
    } catch (error) {
        console.error("Error fetching FAQs:", error);
        return [];
    }
};

export const getAboutUsData = async () => {
    try {
        const response = await axiosInstance.get('home/about/');
        return response.data;
    } catch (error) {
        console.error("Error fetching about us content:", error);
        return null;
    }
};