import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import ProductCard from '../components/ProductCard';
import { getFavoritesList } from '../api/shopApi';

const UserFavorites = () => {
    const [favorites, setFavorites] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchFavorites = async () => {
            try {
                const data = await getFavoritesList();
                setFavorites(data.results || data || []);
            } catch (error) {
                console.error("Error fetching favorites:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchFavorites();
    }, []);

    if (loading) {
        return (
            <div className="text-center py-5 d-flex flex-column align-items-center justify-content-center bg-white rounded-4 shadow-sm border border-ui" style={{ minHeight: '400px' }}>
                <div className="spinner-border text-danger mb-3" style={{width: '3rem', height:'3rem'}}></div>
                <h6 className="font-14 fw-bold text-muted">در حال دریافت علاقه‌مندی‌ها...</h6>
            </div>
        );
    }

    return (
        <div className="user-favorites">
            <div className="bg-white p-3 p-md-4 rounded-4 border border-ui shadow-sm mb-4 d-flex align-items-center gap-3">
                <div className="bg-danger bg-opacity-10 p-2 rounded-circle d-flex align-items-center justify-content-center">
                    <i className="bi bi-heart-fill text-danger fs-3"></i>
                </div>
                <h2 className="fw-900 h5 m-0 text-dark">لیست <span className="text-danger">علاقه‌مندی‌ها</span></h2>
            </div>

            <div className="bg-light rounded-4 shadow-sm border border-ui p-4 min-vh-50">
                {favorites.length === 0 ? (
                    <div className="text-center py-5 my-3 bg-white border border-light rounded-4">
                        <i className="bi bi-heartbreak text-muted opacity-25 d-block mb-3" style={{ fontSize: '5rem' }}></i>
                        <h5 className="fw-bold text-dark mb-2 font-16">لیست علاقه‌مندی شما خالی است!</h5>
                        <p className="text-muted font-13 mb-4">با کلیک روی قلب محصولات، آن‌ها را به این لیست اضافه کنید.</p>
                        <Link to="/shop" className="btn btn-danger rounded-pill px-5 py-2 font-14 fw-bold shadow-sm hover-lift">مشاهده محصولات فروشگاه</Link>
                    </div>
                ) : (
                    <div className="row gy-4 gx-3">
                        {favorites.map(product => (
                            <div className="col-12 col-sm-6 col-lg-4" key={product.uuid || product.id}>
                                <ProductCard product={product} />
                            </div>
                        ))}
                    </div>
                )}
            </div>
            <style jsx="true">{`
                .hover-lift { transition: transform 0.2s ease, box-shadow 0.2s; }
                .hover-lift:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(239, 64, 86, 0.15) !important; }
            `}</style>
        </div>
    );
};

export default UserFavorites;