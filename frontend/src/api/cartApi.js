import axiosInstance from './axios';

export const getCart = async () => {
    const response = await axiosInstance.get('orders/cart/');
    return response.data;
};

export const addToCart = async (productId, variantId, quantity = 1) => {
    const data = { product: productId, quantity: quantity };
    if (variantId) data.variant = variantId;
    const response = await axiosInstance.post('orders/cart/add/', data);
    return response.data;
};

export const removeFromCart = async (itemId) => {
    const response = await axiosInstance.delete(`orders/cart/${itemId}/remove/`);
    return response.data;
};

export const checkout = async (checkoutData) => {
    const response = await axiosInstance.post('orders/orders/checkout/', checkoutData);
    return response.data;
};

export const getShippingMethods = async () => {
    const response = await axiosInstance.get('orders/shipping-methods/');
    return response.data;
};