import React, { createContext, useState, useEffect, useContext } from 'react';
import { getUserProfile, getAuthConfig, loginWithEmail as apiLoginEmail, verifyOtp as apiVerifyOtp } from '../api/authApi';

export const AuthContext = createContext();

export const useAuth = () => {
    return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [authMode, setAuthMode] = useState('OTP'); // Default fallback
    const [loading, setLoading] = useState(true);

    const fetchProfile = async () => {
        try {
            const profile = await getUserProfile();
            setUser(profile);
            return profile;
        } catch (error) {
            console.error("Error fetching updated profile", error);
            throw error;
        }
    };

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
        await fetchProfile();
    };

    const loginOtp = async (phone, code) => {
        await apiVerifyOtp(phone, code);
        await fetchProfile();
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, authMode, loginEmail, loginOtp, logout, loading, fetchProfile }}>
            {children}
        </AuthContext.Provider>
    );
};