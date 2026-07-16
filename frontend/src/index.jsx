import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { HelmetProvider } from 'react-helmet-async';

import '../assets/css/bootstrap.min.css';
import '../assets/css/bootstrap-icon/bootstrap-icons.min.css';
import '../assets/css/normalize.css';
import '../assets/css/default-style.css';
import '../assets/css/color.css';
import '../assets/css/mega-menu.css';
import '../assets/css/style.css';
import '../assets/css/responsive.css';
import './styles/main.css';

import App from './App';
import { AuthProvider } from './context/AuthContext';
import { CartProvider } from './context/CartContext';
import { CompareProvider } from './context/CompareContext';
import { SiteProvider } from './context/SiteContext'; 

document.documentElement.dir = 'rtl';
document.documentElement.lang = 'fa';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <HelmetProvider>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <AuthProvider>
          <SiteProvider> 
            <CartProvider>
              <CompareProvider>
                <App />
              </CompareProvider>
            </CartProvider>
          </SiteProvider>
        </AuthProvider>
      </BrowserRouter>
    </HelmetProvider>
  </React.StrictMode>
);