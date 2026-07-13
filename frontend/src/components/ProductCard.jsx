import React, { useContext, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CartContext } from '../context/CartContext';
import { AuthContext } from '../context/AuthContext';
import { toggleFavorite } from '../api/shopApi';

const resolveImageUrl = (url) => {
    if (!url) return '/assets/image/product/product-no-bg.png';
    if (url.startsWith('http') || url.startsWith('data:')) return url;
    let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    baseUrl = baseUrl.replace(/\/api\/?$/, '');
    return `${baseUrl}${url.startsWith('/') ? '' : '/'}${url}`;
};

const ProductCard = ({ product }) => {
    const navigate = useNavigate();
    const { addToCart } = useContext(CartContext);
    const { user } = useContext(AuthContext);
    const [isFav, setIsFav] = useState(product.is_favorite || false);
    const [isAdding, setIsAdding] = useState(false);

    const mainImageObj = product.gallery?.find(img => img.is_main) || product.gallery?.[0];
    const mainImage = mainImageObj?.url || '/assets/image/product/product-no-bg.png';
    const mainImageAlt = mainImageObj?.image_alt || product.title;
    
    const discountPercent = product.special_discount_percent || 0;
    const originalPrice = product.base_price || 0;
    const finalPrice = discountPercent > 0 ? originalPrice - (originalPrice * discountPercent / 100) : originalPrice;

    const handleFavorite = async (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (!user) {
            navigate('/login');
            return;
        }
        try {
            const res = await toggleFavorite(product.slug || product.uuid);
            setIsFav(res.is_favorite);
        } catch (error) {
            console.error("Error toggling favorite", error);
        }
    };

    const handleAddToCart = async (e) => {
        e.preventDefault();
        e.stopPropagation();
        
        if (product.is_variable) {
            navigate(`/product/${product.slug}`);
            return;
        }
        
        setIsAdding(true);
        try {
            await addToCart(product.uuid, null, 1);
        } catch (error) {
            console.error("Error adding to cart", error);
        } finally {
            setIsAdding(false);
        }
    };

    return (
        <div className="product-card bg-white rounded-4 shadow-sm border border-ui p-3 position-relative hover-shadow transition h-100 d-flex flex-column">
            
            <div className="position-absolute top-0 start-0 p-3 z-2 d-flex flex-column gap-2">
                {product.is_special_offer && (
                    <span className="badge bg-danger rounded-pill shadow-sm fw-bold font-11 px-2 py-1">شگفت‌انگیز</span>
                )}
                {discountPercent > 0 && (
                    <span className="badge bg-danger rounded-pill shadow-sm fw-bold font-12 px-2 py-1">{discountPercent}٪ تخفیف</span>
                )}
            </div>

            <div className="position-absolute top-0 end-0 p-3 z-2 d-flex flex-column gap-2">
                <button onClick={handleFavorite} className={`btn btn-sm rounded-circle shadow-sm d-flex align-items-center justify-content-center transition ${isFav ? 'bg-danger text-white border-danger' : 'bg-white text-muted border-ui hover-text-danger'}`} style={{width: '35px', height: '35px'}} aria-label="افزودن به علاقه‌مندی‌ها">
                    <i className={isFav ? "bi bi-heart-fill font-14" : "bi bi-heart font-14"}></i>
                </button>
            </div>

            <Link to={`/product/${product.slug}`} className="d-block text-center mb-3 pt-4 pb-2 text-decoration-none">
                <img 
                    src={resolveImageUrl(mainImage)} 
                    alt={mainImageAlt} 
                    title={mainImageAlt}
                    className="img-fluid object-fit-contain transition hover-scale" 
                    style={{ height: '180px', width: '100%' }} 
                    loading="lazy"
                    decoding="async"
                    onError={(e)=>{e.target.src='/assets/image/product/product-no-bg.png'}} 
                />
            </Link>

            <div className="product-details d-flex flex-column flex-grow-1">
                {product.brand && (
                    <span className="text-muted font-11 mb-1 d-block fw-bold">{product.brand.title}</span>
                )}
                
                <Link to={`/product/${product.slug}`} className="text-decoration-none">
                    <h3 className="font-14 fw-bold text-dark text-overflow-2 mb-3 lh-base hover-text-danger transition">
                        {product.title}
                    </h3>
                </Link>

                <div className="mt-auto">
                    <div className="d-flex align-items-end justify-content-between mb-3">
                        <div className="rating text-warning font-12 d-flex align-items-center bg-warning bg-opacity-10 px-2 py-1 rounded-pill">
                            <i className="bi bi-star-fill me-1"></i>
                            <span className="text-dark fw-bold pt-1">{Number(product.average_rating || 0).toFixed(1)}</span>
                        </div>
                        <div className="price-box text-end">
                            {discountPercent > 0 ? (
                                <>
                                    <div className="text-muted text-decoration-line-through font-12">{Number(originalPrice).toLocaleString()}</div>
                                    <div className="text-danger fw-900 font-16">{Number(finalPrice).toLocaleString()} <span className="font-11 fw-normal">تومان</span></div>
                                </>
                            ) : (
                                <div className="text-dark fw-900 font-16">{Number(finalPrice).toLocaleString()} <span className="font-11 text-muted fw-normal">تومان</span></div>
                            )}
                        </div>
                    </div>

                    {(product.base_inventory > 0 || product.variants?.some(v => v.inventory > 0)) ? (
                        <button 
                            onClick={handleAddToCart}
                            disabled={isAdding}
                            className="btn btn-danger w-100 rounded-pill py-2 font-13 fw-bold shadow-sm hover-lift d-flex align-items-center justify-content-center gap-2"
                        >
                            {isAdding ? (
                                <div className="spinner-border spinner-border-sm text-white"></div>
                            ) : (
                                <>
                                    <i className={product.is_variable ? "bi bi-sliders" : "bi bi-cart-plus fs-5"}></i>
                                    {product.is_variable ? 'انتخاب ویژگی‌ها' : 'افزودن به سبد خرید'}
                                </>
                            )}
                        </button>
                    ) : (
                        <button disabled className="btn btn-light w-100 rounded-pill py-2 font-13 fw-bold text-muted border border-ui">
                            ناموجود در انبار
                        </button>
                    )}
                </div>
            </div>

            <style jsx="true">{`
                .hover-shadow:hover { box-shadow: 0 10px 25px rgba(0,0,0,0.08) !important; border-color: #dee2e6 !important; z-index: 10;}
                .transition { transition: all 0.3s ease; }
                .hover-scale:hover { transform: scale(1.05); }
                .hover-text-danger:hover { color: #ef4056 !important; }
                .hover-lift:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(239, 64, 86, 0.3) !important; }
                .text-overflow-2 { overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; min-height: 44px;}
            `}</style>
        </div>
    );
};

export default ProductCard;