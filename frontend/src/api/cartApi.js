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

export const getCart = async () => {
    const response = await axiosInstance.get('/orders/cart/', getHeaders());
    return response.data;
};

export const addToCart = async (productId, variantId, quantity = 1) => {
    const data = { product: productId, quantity: quantity };
    if (variantId) data.variant = variantId;
    const response = await axiosInstance.post('/orders/cart/add/', data, getHeaders());
    return response.data;
};

export const updateItemQuantity = async (itemId, quantity) => {
    const response = await axiosInstance.patch(`/orders/cart/${itemId}/update_quantity/`, { quantity }, getHeaders());
    return response.data;
};

export const removeFromCart = async (itemId) => {
    const response = await axiosInstance.delete(`/orders/cart/${itemId}/remove/`, getHeaders());
    return response.data;
};

export const checkout = async (checkoutData) => {
    const response = await axiosInstance.post('/orders/orders/checkout/', checkoutData, getHeaders());
    return response.data;
};

export const getShippingMethods = async () => {
    const response = await axiosInstance.get('/orders/shipping-methods/');
    return response.data;
};

export const validateCoupon = async (code) => {
    const response = await axiosInstance.post('/orders/orders/validate_coupon_api/', { code }, getHeaders());
    return response.data;
};

export const getUserOrders = async (queryString = '') => {
    const url = queryString ? `/orders/orders/?${queryString}` : '/orders/orders/';
    const response = await axiosInstance.get(url, getHeaders());
    return response.data;
};

export const getOrderDetail = async (orderId) => {
    const response = await axiosInstance.get(`/orders/orders/${orderId}/`, getHeaders());
    return response.data;
};

export const submitOrderRequest = async (orderId, reason, requestType) => {
    const response = await axiosInstance.post('/orders/order-requests/', { order: orderId, reason: reason, request_type: requestType }, getHeaders());
    return response.data;
};

export const getOrderRequests = async () => {
    const response = await axiosInstance.get('/orders/order-requests/', getHeaders());
    return response.data;
};