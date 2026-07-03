import React from 'react';
import { Routes, Route } from 'react-router-dom';
import ProductDetailPage from './pages/ProductDetailPage';

function App() {
  return (
    <Routes>
      <Route path="/product/:id" element={<ProductDetailPage />} />
    </Routes>
  );
}

export default App;