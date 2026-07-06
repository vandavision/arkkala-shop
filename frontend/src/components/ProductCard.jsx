import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { CompareContext } from '../context/CompareContext';

const ProductCard = ({ product }) => {
    const { addToCompare } = useContext(CompareContext);

    const currentPrice = product.is_variable && product.variants?.length > 0 
        ? product.variants[0].price 
        : product.base_price;
    
    const discountAmount = product.discount_percent || 15; 
    const oldPrice = Math.round(currentPrice * (1 + (discountAmount / 100)));

    const handleCompareClick = (e) => {
        e.preventDefault();
        e.stopPropagation();
        addToCompare(product.uuid);
    };

    return (
        <div className="product-box border-ui h-100 d-flex flex-column bg-white">
            <div className="product-timer position-relative">
                <div className="product-header-btn flex-column position-absolute top-0">
                    <button onClick={handleCompareClick} className="mb-1 border-ui btn p-0 d-flex align-items-center justify-content-center bg-white shadow-sm" title="افزودن به لیست مقایسه">
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
                <div className="product-image text-center pt-3 pb-2">
                    <img 
                        src={product.gallery?.[0]?.url || '/assets/image/product/television1.jpg'} 
                        loading="lazy" 
                        alt={product.title} 
                        className="img-fluid one-image object-fit-contain"
                        style={{ height: '180px', width: '100%' }}
                    />
                    {product.gallery?.[1]?.url && (
                        <img 
                            src={product.gallery[1].url} 
                            loading="lazy" 
                            alt={product.title} 
                            className="img-fluid two-image object-fit-contain"
                            style={{ height: '180px', width: '100%' }}
                        />
                    )}
                </div>
                
                <div className="d-flex h-80-px align-items-center justify-content-between px-3 mt-auto">
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
                            <p className="old-price mb-0 text-muted">
                                <span className="badge bg-danger rounded-pill me-2">{discountAmount}%</span>
                                <bdi>{Number(oldPrice).toLocaleString()}</bdi>
                            </p>
                        </div>
                    </div>
                    <div className="progress bs-bg-gray-400 mt-2 mb-1" role="progressbar" style={{ height: '4px' }}>
                        <div className="progress-bar main-color-one-bg" style={{ width: '63%' }}></div>
                    </div>
                </div>
            </Link>
        </div>
    );
};

export default ProductCard;