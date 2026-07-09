// arkkala/frontend/src/context/SiteContext.jsx
import React, { createContext, useState, useEffect } from 'react';
import { getSiteSettings } from '../api/homeApi';

export const SiteContext = createContext();

export const SiteProvider = ({ children }) => {
    const [settings, setSettings] = useState({
        site_name: 'فروشگاه',
        about_us_footer: 'در حال بارگذاری...',
        phone_number: '...',
        working_hours: '...',
        telegram: '',
        instagram: '',
        whatsapp: '',
        linkedin: '',
        twitter: '',
        copyright_text: '',
        logo_url: null,
        seller_legal_name: '',
        seller_address: '',
        seller_economic_code: '',
        seller_postal_code: '',
        seller_registration_number: '',
        namad_1_img_url: null, namad_1_link: null,
        namad_2_img_url: null, namad_2_link: null,
        namad_3_img_url: null, namad_3_link: null,
        namad_4_img_url: null, namad_4_link: null,
        namad_5_img_url: null, namad_5_link: null,
        namad_6_img_url: null, namad_6_link: null,
        namad_7_img_url: null, namad_7_link: null,
    });

    useEffect(() => {
        getSiteSettings().then(data => {
            if (data) setSettings(prev => ({ ...prev, ...data }));
        });
    }, []);

    return (
        <SiteContext.Provider value={{ settings }}>
            {children}
        </SiteContext.Provider>
    );
};