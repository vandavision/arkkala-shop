import React, { useEffect, Suspense, lazy } from 'react';
import { Routes, Route, useLocation, Navigate } from 'react-router-dom';
import { Helmet } from 'react-helmet-async';

import Header from './components/Header';
import Footer from './components/Footer';

const PageLoader = () => (
    <div className="d-flex justify-content-center align-items-center min-vh-100 bg-light">
        <div className="spinner-border text-danger" style={{width: '3.5rem', height: '3.5rem', borderWidth: '0.25rem'}} role="status"></div>
    </div>
);

const HomePage = lazy(() => import('./pages/HomePage'));
const ShopPage = lazy(() => import('./pages/ShopPage'));
const ProductDetailPage = lazy(() => import('./pages/ProductDetailPage'));
const CartPage = lazy(() => import('./pages/CartPage'));
const CheckoutPage = lazy(() => import('./pages/CheckoutPage'));
const ComparePage = lazy(() => import('./pages/ComparePage'));
const CategoriesPage = lazy(() => import('./pages/CategoriesPage'));
const BrandsPage = lazy(() => import('./pages/BrandsPage'));
const BlogPage = lazy(() => import('./pages/BlogPage')); 
const BlogDetailPage = lazy(() => import('./pages/BlogDetailPage'));
const FaqPage = lazy(() => import('./pages/FaqPage'));
const AboutUsPage = lazy(() => import('./pages/AboutUsPage'));
const ContactPage = lazy(() => import('./pages/ContactPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const PaymentResultPage = lazy(() => import('./pages/PaymentResultPage'));
const OrderInvoicePage = lazy(() => import('./pages/OrderInvoicePage'));
const ReturnPolicyPage = lazy(() => import('./pages/ReturnPolicyPage'));

const DashboardLayout = lazy(() => import('./pages/DashboardLayout'));
const DashboardSummary = lazy(() => import('./pages/DashboardSummary'));
const ProfileInfo = lazy(() => import('./pages/ProfileInfo'));
const UserOrders = lazy(() => import('./pages/UserOrders'));
const UserFavorites = lazy(() => import('./pages/UserFavorites'));
const UserComments = lazy(() => import('./pages/UserComments'));

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
      <Helmet>
        <html lang="fa" dir="rtl" />
      </Helmet>
      
      {!isIsolatedPage && <Header />}
      
      <div className="main-content">
        <Suspense fallback={<PageLoader />}>
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
            <Route path="/contact" element={<ContactPage />} />
            <Route path="/return" element={<ReturnPolicyPage />} />
            
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
        </Suspense>
      </div>

      {!isIsolatedPage && <Footer />}
    </div>
  );
}

export default App;