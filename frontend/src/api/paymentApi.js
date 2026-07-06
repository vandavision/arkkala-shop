import axiosInstance from './axios';

const getGuestId = () => localStorage.getItem('guest_id') || '';

const getHeaders = () => {
    return {
        headers: { 'X-Guest-ID': getGuestId() }
    };
};

export const requestPayment = async (orderId, gateway = 'zarinpal') => {
    try {
        const response = await axiosInstance.post('/payments/request_payment/', {
            order_id: orderId,
            gateway: gateway
        }, getHeaders());
        return response.data;
    } catch (error) {
        console.error("Error requesting payment:", error);
        throw error;
    }
};