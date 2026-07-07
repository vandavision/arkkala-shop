import React, { createContext, useState, useEffect } from 'react';
import { getUserProfile, getAuthConfig, loginWithEmail as apiLoginEmail, verifyOtp as apiVerifyOtp } from '../api/authApi';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [authMode, setAuthMode] = useState('OTP'); // Default fallback
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const initializeAuth = async () => {
            try {
                const config = await getAuthConfig();
                setAuthMode(config.mode);
            } catch (error) {
                console.error('Failed to fetch auth config, defaulting to OTP');
            }

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
        initializeAuth();
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
        <AuthContext.Provider value={{ user, authMode, loginEmail, loginOtp, logout, loading }}>
            {children}
        </AuthContext.Provider>
    );
};