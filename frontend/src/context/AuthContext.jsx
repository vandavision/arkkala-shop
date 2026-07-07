import React, { createContext, useState, useEffect } from 'react';
import { getUserProfile, loginWithEmail as apiLoginEmail, verifyOtp as apiVerifyOtp } from '../api/authApi';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchUser = async () => {
            if (localStorage.getItem('access_token')) {
                try {
                    const profile = await getUserProfile();
                    setUser(profile);
                } catch (error) {
                    console.log('User not logged in or token expired');
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                }
            }
            setLoading(false);
        };
        fetchUser();
    }, []);

    const loginEmail = async (email, password) => {
        await apiLoginEmail(email, password);
        const profile = await getUserProfile();
        setUser(profile);
    };

    const loginOtp = async (phone, code) => {
        await apiVerifyOtp(phone, code);
        const profile = await getUserProfile();
        setUser(profile);
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loginEmail, loginOtp, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};