import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { CompareContext } from '../context/CompareContext';
import CountdownTimer from './CountdownTimer';

const resolveImageUrl = (url) => {
    if (!url) return '/assets/image/product/product-no-bg.png';
    if (url.startsWith('http') || url.startsWith('data:')) return url;
    
    let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    baseUrl = baseUrl.replace(/\/api\/?$/, '');
    
    return `${baseUrl}${url.startsWith('/') ? '' : '/'}${url}`;
};

const ProductCard = ({ product }) => {
    const { addToCompare } = useContext(CompareContext);

    let currentPrice = product.is_variable && product.variants?.length > 0 
        ? product.variants[0].price 
        : product.base_price;
    
    let oldPrice = null;
    let discountAmount = 0;

    if (product.is_special_offer) {
        discountAmount = product.special_discount_percent;
        oldPrice = currentPrice;
        currentPrice = currentPrice * (1 - (discountAmount / 100));
    } else {
        discountAmount = product.discount_percent || 0; 
        if (discountAmount > 0) {
            oldPrice = currentPrice;
            currentPrice = currentPrice * (1 - (discountAmount / 100));
        }
    }

    const handleCompareClick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        addToCompare(product.uuid);
    };

    const mainImageRaw = product.image_url || (product.gallery && product.gallery.length > 0 ? product.gallery[0].url : '');
    const mainImage = resolveImageUrl(mainImageRaw);
    
    const secondImageRaw = product.gallery && product.gallery.length > 1 ? product.gallery[1].url : null;
    const secondImage = secondImageRaw ? resolveImageUrl(secondImageRaw) : null;

    return (
        <div className="product-box border-ui h-100 d-flex flex-column bg-white overflow-hidden">
            <div className="product-timer position-relative">
                <div className="product-header-btn flex-column position-absolute top-0" style={{zIndex: 10}}>
                    <button onClick={handleCompareClick} className="mb-1 border-ui btn p-0 d-flex align-items-center justify-content-center bg-white shadow-sm" title="مقایسه محصولات">
                        <i className="bi bi-shuffle text-muted"></i>
                    </button>
                    <button className="mb-1 border-ui btn p-0 d-flex align-items-center justify-content-center bg-white shadow-sm" title="افزودن به علاقه‌مندی">
                        <i className="bi bi-heart text-muted"></i>
                    </button>
                    <Link to={`/product/${product.slug}`} className="mb-1 border-ui btn p-0 d-flex align-items-center justify-content-center bg-white shadow-sm" title="نمایش سریع">
                        <i className="bi bi-eye text-muted"></i>
                    </Link>
                </div>
            </div>
            
            <Link to={`/product/${product.slug}`} className="d-flex flex-column flex-grow-1 text-decoration-none">
                <div className="product-image text-center pt-3 pb-2 position-relative">
                    {product.is_special_offer && (
                        <div className="position-absolute top-0 end-0 mt-2 ms-2 z-3 d-flex flex-column align-items-end">
                            <span className="badge bg-danger shadow-sm rounded-pill font-11 animate-pulse">شگفت‌انگیز</span>
                        </div>
                    )}

                    <img 
                        src={mainImage} 
                        loading="lazy" 
                        alt={product.title} 
                        className="img-fluid one-image object-fit-contain"
                        style={{ height: '180px', width: '100%' }}
                        onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/product/product-no-bg.png'; }}
                    />
                    {secondImage && (
                        <img 
                            src={secondImage} 
                            loading="lazy" 
                            alt={product.title} 
                            className="img-fluid two-image object-fit-contain"
                            style={{ height: '180px', width: '100%' }}
                            onError={(e) => { e.target.onerror = null; e.target.style.display = 'none'; }}
                        />
                    )}
                    
                    {product.is_special_offer && product.special_offer_end && (
                        <div className="position-absolute bottom-0 start-50 translate-middle-x mb-1 w-100 d-flex justify-content-center z-3">
                            <CountdownTimer endTime={product.special_offer_end} />
                        </div>
                    )}
                </div>
                
                <div className="d-flex h-80-px align-items-center justify-content-between px-3 mt-auto z-3 bg-white">
                    <h6 className="font-14 text-overflow-2 my-3 lh-lg text-dark">
                        {product.title}
                    </h6>
                </div>
                
                <div className="bs-bg-gray-200 p-2 border-ui rounded-3 mx-2 mb-3 mt-auto">
                    <div className="d-flex align-items-center justify-content-between">
                        <div className="discount mt-1">
                            <span className="btn main-color-one-bg d-flex align-items-center justify-content-center p-0 rounded-3 shadow-sm" style={{width: '38px', height: '38px'}}>
                                <i className="bi bi-cart text-white fs-5"></i>
                            </span>
                        </div>
                        <div className="price d-flex justify-content-end flex-column align-content-end text-end">
                            <p className="new-price me-0 text-end mb-1 text-dark">
                                <bdi>{Number(currentPrice).toLocaleString()}</bdi> <span className="fw-normal font-12">تومان</span>
                            </p>
                            {oldPrice && discountAmount > 0 && (
                                <p className="old-price mb-0 text-muted">
                                    <span className="badge bg-danger rounded-pill me-2">{discountAmount}%</span>
                                    <bdi><del>{Number(oldPrice).toLocaleString()}</del></bdi>
                                </p>
                            )}
                        </div>
                    </div>
                    {product.is_special_offer && (
                        <div className="progress bs-bg-gray-400 mt-2 mb-1 rounded-pill" role="progressbar" style={{ height: '4px' }}>
                            <div className="progress-bar bg-danger" style={{ width: '85%' }}></div>
                        </div>
                    )}
                </div>
            </Link>
            <style jsx="true">{`
                .animate-pulse { animation: pulse 2s infinite; }
                @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(220,53,69, 0.4); } 70% { box-shadow: 0 0 0 8px rgba(220,53,69, 0); } 100% { box-shadow: 0 0 0 0 rgba(220,53,69, 0); } }
            `}</style>
        </div>
    );
};

export default ProductCard;