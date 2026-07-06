import React, { createContext, useState, useEffect, useContext } from 'react';
import { getCart, addToCart as apiAddToCart, removeFromCart as apiRemoveFromCart, updateItemQuantity as apiUpdateQty } from '../api/cartApi';
import { AuthContext } from './AuthContext';

export const CartContext = createContext();

export const CartProvider = ({ children }) => {
    const { user } = useContext(AuthContext);
    const [cartItems, setCartItems] = useState([]);
    const [cartLoading, setCartLoading] = useState(true);

    const fetchCart = async () => {
        try {
            const data = await getCart();
            setCartItems(Array.isArray(data) ? data : []);
        } catch (error) {
            console.error("Error fetching cart:", error);
        } finally {
            setCartLoading(false);
        }
    };

    useEffect(() => {
        fetchCart();
    }, [user]);

    const addToCart = async (productId, variantId, quantity = 1) => {
        try {
            await apiAddToCart(productId, variantId, quantity);
            await fetchCart();
            return true;
        } catch (error) {
            throw error;
        }
    };

    const removeFromCart = async (itemId) => {
        try {
            await apiRemoveFromCart(itemId);
            await fetchCart();
        } catch (error) {
            console.error(error);
        }
    };

    const updateQuantity = async (itemId, quantity) => {
        try {
            await apiUpdateQty(itemId, quantity);
            await fetchCart();
        } catch (error) {
            console.error(error);
        }
    };

    return (
        <CartContext.Provider value={{ cartItems, cartLoading, addToCart, removeFromCart, updateQuantity, fetchCart }}>
            {children}
        </CartContext.Provider>
    );
};