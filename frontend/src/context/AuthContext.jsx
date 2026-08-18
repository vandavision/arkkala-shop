import React, { createContext, useState, useEffect } from 'react';
import axiosInstance from '../api/axios';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [authMode, setAuthMode] = useState(() => {
        return localStorage.getItem('site_auth_mode') || null;
    });

    const fetchAuthConfig = async () => {
        try {
            const response = await axiosInstance.get('users/auth-config/');
            const mode = response.data.mode;
            setAuthMode(mode);
            localStorage.setItem('site_auth_mode', mode);
        } catch (error) {
            const fallbackMode = 'EMAIL';
            setAuthMode(fallbackMode);
            localStorage.setItem('site_auth_mode', fallbackMode);
        }
    };

    const fetchUser = async () => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            setLoading(false);
            return;
        }

        try {
            const response = await axiosInstance.get('users/profile/');
            setUser(response.data);
        } catch (error) {
            setUser(null);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const initializeAuth = async () => {
            await fetchAuthConfig();
            await fetchUser();
        };
        initializeAuth();
    }, []);

    const login = (userData, tokens) => {
        localStorage.setItem('access_token', tokens.access);
        localStorage.setItem('refresh_token', tokens.refresh);
        axiosInstance.defaults.headers['Authorization'] = 'Bearer ' + tokens.access;
        setUser(userData);
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        delete axiosInstance.defaults.headers['Authorization'];
        setUser(null);
    };

    return (
        <AuthContext.Provider value={{ user, loading, authMode, login, logout, fetchUser }}>
            {children}
        </AuthContext.Provider>
    );
};