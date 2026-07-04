import axiosInstance from './axios';

export const getHomePageData = async () => {
    const response = await axiosInstance.get('home/');
    return response.data;
};