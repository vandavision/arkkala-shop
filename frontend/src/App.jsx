import React, { useEffect } from 'react';
import { Routes, Route, useLocation, Navigate } from 'react-router-dom';

// Components
import Header from './components/Header';
import Footer from './components/Footer';

// Public Pages
import HomePage from './pages/HomePage';
import ShopPage from './pages/ShopPage';
import ProductDetailPage from './pages/ProductDetailPage';
import CartPage from './pages/CartPage';
import CheckoutPage from './pages/CheckoutPage';
import ComparePage from './pages/ComparePage';
import CategoriesPage from './pages/CategoriesPage';
import BrandsPage from './pages/BrandsPage';
import BlogPage from './pages/BlogPage'; 
import BlogDetailPage from './pages/BlogDetailPage';
import FaqPage from './pages/FaqPage';
import AboutUsPage from './pages/AboutUsPage';
import LoginPage from './pages/LoginPage';
import PaymentResultPage from './pages/PaymentResultPage';
import OrderInvoicePage from './pages/OrderInvoicePage';
// Dashboard Pages
import DashboardLayout from './pages/DashboardLayout';
import DashboardSummary from './pages/DashboardSummary';
import ProfileInfo from './pages/ProfileInfo';
import UserOrders from './pages/UserOrders';
import UserFavorites from './pages/UserFavorites';
import UserComments from './pages/UserComments';

const ScrollToTop = () => {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo({
      top: 0,
      left: 0,
      behavior: 'auto'
    });
  }, [pathname]);

  return null;
};

function App() {
  const location = useLocation();
  const isIsolatedPage = location.pathname === '/login' || location.pathname === '/payment/result';

  return (
    <div className="app-wrapper bg-light">
      <ScrollToTop />
      
      {!isIsolatedPage && <Header />}
      
      <div className="main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/shop" element={<ShopPage />} /> 
          <Route path="/category/:slug" element={<ShopPage />} /> 
          <Route path="/special-offers" element={<ShopPage />} /> 
          <Route path="/best-sellers" element={<ShopPage />} /> 
          <Route path="/categories" element={<CategoriesPage />} />
          <Route path="/brands" element={<BrandsPage />} />
          
          <Route path="/blog" element={<BlogPage />} /> 
          <Route path="/blog/:slug" element={<BlogDetailPage />} />
          
          <Route path="/faq" element={<FaqPage />} />
          <Route path="/about" element={<AboutUsPage />} />
          
          <Route path="/product/:slug" element={<ProductDetailPage />} />
          <Route path="/cart" element={<CartPage />} />
          <Route path="/checkout" element={<CheckoutPage />} />
          <Route path="/compare" element={<ComparePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/payment/result" element={<PaymentResultPage />} />
          
          <Route path="/profile" element={<Navigate to="/dashboard/profile" replace />} />
          <Route path="/orders" element={<Navigate to="/dashboard/orders" replace />} />
          
          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route index element={<DashboardSummary />} />
            <Route path="profile" element={<ProfileInfo />} />
            <Route path="orders" element={<UserOrders />} />
            <Route path="orders/:id" element={<OrderInvoicePage />} />
            <Route path="favorites" element={<UserFavorites />} />
            <Route path="comments" element={<UserComments />} />
          </Route>

          <Route path="*" element={
            <div className="container py-5 mt-5 text-center" style={{minHeight: '50vh'}}>
                <i className="bi bi-tools text-warning mb-3 d-block" style={{fontSize: '4rem'}}></i>
                <h3 className="fw-900 text-dark">این صفحه در حال ساخت است...</h3>
                <p className="text-muted mt-3">به زودی این بخش به سایت اضافه خواهد شد.</p>
            </div>
          } />
        </Routes>
      </div>

      {!isIsolatedPage && <Footer />}
    </div>
  );
}

export default App;