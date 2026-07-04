import React, { createContext, useState, useEffect, useContext } from 'react';
import { getCart, addToCart as apiAddToCart, removeFromCart as apiRemoveFromCart } from '../api/cartApi';
import { AuthContext } from './AuthContext';

export const CartContext = createContext();

export const CartProvider = ({ children }) => {
    const [cartItems, setCartItems] = useState([]);
    const { user } = useContext(AuthContext);

    const fetchCart = async () => {
        if (user) {
            try {
                const data = await getCart();
                setCartItems(data);
            } catch (error) {
                console.error("Error fetching cart", error);
            }
        } else {
            setCartItems([]);
        }
    };

    useEffect(() => {
        fetchCart();
    }, [user]);

    const addToCart = async (productId, variantId, quantity) => {
        if (!user) {
            alert("لطفاً ابتدا وارد حساب کاربری خود شوید.");
            return;
        }
        await apiAddToCart(productId, variantId, quantity);
        await fetchCart();
    };

    const remove = async (itemId) => {
        await apiRemoveFromCart(itemId);
        await fetchCart();
    };

    return (
        <CartContext.Provider value={{ cartItems, addToCart, remove, fetchCart }}>
            {children}
        </CartContext.Provider>
    );
};