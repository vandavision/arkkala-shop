// arkkala/frontend/src/App.jsx
import React from 'react';
import { Routes, Route } from 'react-router-dom';
import ProductDetailPage from './pages/ProductDetailPage';
import HomePage from './pages/HomePage';
import ShopPage from './pages/ShopPage'; // <--- صفحه جدید وارد شد
import Header from './components/Header';
import Footer from './components/Footer';

function App() {
  return (
    <div className="app-wrapper">
      <Header />
      <div className="main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/shop" element={<ShopPage />} /> {/* روت فروشگاه اصلی */}
          <Route path="/category/:slug" element={<ShopPage />} /> {/* روت اختصاصی هر دسته */}
          <Route path="/product/:id" element={<ProductDetailPage />} />
          
          <Route path="*" element={
            <div className="container py-5 mt-5 text-center" style={{minHeight: '50vh'}}>
                <i className="bi bi-tools text-warning mb-3 d-block" style={{fontSize: '4rem'}}></i>
                <h3 className="fw-900 text-dark">این صفحه در حال ساخت است...</h3>
                <p className="text-muted mt-3">به زودی این بخش به سایت اضافه خواهد شد.</p>
            </div>
          } />
        </Routes>
      </div>
      <Footer />
    </div>
  );
}

export default App;