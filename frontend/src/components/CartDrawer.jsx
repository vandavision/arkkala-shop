import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CartContext } from '../context/CartContext';

const resolveImageUrl = (url) => {
    if (!url) return '/assets/image/product/product-no-bg.png';
    if (url.startsWith('http') || url.startsWith('data:')) return url;
    
    let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    baseUrl = baseUrl.replace(/\/api\/?$/, '');
    
    return `${baseUrl}${url.startsWith('/') ? '' : '/'}${url}`;
};

const CartDrawer = () => {
    const { cartItems, removeFromCart, updateQuantity } = useContext(CartContext);
    const navigate = useNavigate();

    const handleRemove = (itemId) => {
        removeFromCart(itemId);
    };

    const handleUpdateQuantity = (itemId, currentQty, type, inventory) => {
        let newQty = currentQty;
        if (type === 'increase' && currentQty < inventory) newQty += 1;
        if (type === 'decrease' && currentQty > 1) newQty -= 1;
        if (newQty !== currentQty) {
            updateQuantity(itemId, newQty);
        }
    };

    const closeOffcanvas = () => {
        const closeBtn = document.querySelector('#offcanvasCart .btn-close');
        if (closeBtn) closeBtn.click();
    };

    const totalItemsCount = cartItems.reduce((acc, item) => acc + item.quantity, 0);
    const totalPayableAmount = cartItems.reduce((acc, item) => acc + Number(item.total_price), 0);
    const totalRealValue = cartItems.reduce((acc, item) => acc + (Number(item.product_details?.base_price || 0) * item.quantity), 0);
    const totalDiscount = totalRealValue > totalPayableAmount ? totalRealValue - totalPayableAmount : 0;

    return (
        <section className="offcanvas offcanvas-end py-2" tabIndex="-1" id="offcanvasCart" aria-labelledby="offcanvasCartLabel">
            <div className="offcanvas-header shadow-sm border-bottom border-light pb-3">
                <h5 className="offcanvas-title fw-bold" id="offcanvasCartLabel">سبد خرید 
                    <small className="text-muted fw-bold font-14 ms-2">({totalItemsCount} کالا)</small>
                </h5>
                <button type="button" className="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
            </div>
            
            <div className="offcanvas-body d-flex flex-column p-0 bg-light">
                <ul className="navbar-nav cart-canvas-parent flex-grow-1 overflow-auto custom-scrollbar p-3 m-0">
                    {cartItems.length === 0 ? (
                        <div className="text-center mt-5">
                            <img src="/assets/image/cart/empty-cart.svg" alt="empty" width="150" className="mb-4 opacity-75 mx-auto d-block" />
                            <h5 className="fw-bold text-dark font-16">سبد خرید شما خالی است</h5>
                            <button onClick={() => { closeOffcanvas(); navigate('/shop'); }} className="btn btn-outline-danger rounded-pill px-4 py-2 mt-3 font-14 fw-bold shadow-sm hover-lift">بازگشت به فروشگاه</button>
                        </div>
                    ) : (
                        cartItems.map((item, index) => {
                            const product = item.product_details || {};
                            const variant = item.variant_details;
                            const maxInventory = variant ? variant.inventory : product.base_inventory || 0;
                            const hasDiscount = Number(product.base_price || 0) > Number(item.unit_price || 0);
                            
                            const mainImageObj = product?.gallery?.find(img => img.is_main) || product?.gallery?.[0];
                            const rawUrl = mainImageObj?.url || product?.image_url || product?.image;
                            const imageUrl = resolveImageUrl(rawUrl);

                            return (
                                <li className={`nav-item bg-white p-3 rounded-4 shadow-sm border border-ui ${index !== cartItems.length - 1 ? 'mb-3' : ''}`} key={item.id}>
                                    <div className="cart-canvas">
                                        <div className="row align-items-start">
                                            <div className="col-4 ps-0 text-center">
                                                <Link to={`/product/${product.slug}`} onClick={closeOffcanvas}>
                                                    <img 
                                                        src={imageUrl} 
                                                        alt={product.title || 'تصویر کالا'} 
                                                        className="img-thumbnail border-ui rounded-4 w-100 object-fit-contain shadow-sm p-2 bg-light mb-3 hover-lift transition" 
                                                        style={{height: '110px'}} 
                                                        onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/product/product-no-bg.png'; }} 
                                                    />
                                                </Link>
                                            </div>
                                            <div className="col-8 pe-2">
                                                <h3 className="text-overflow-2 font-13 fw-bold lh-lg mb-2">
                                                    <Link to={`/product/${product.slug}`} onClick={closeOffcanvas} className="text-dark text-decoration-none hover-text-danger transition">
                                                        {product.title}
                                                    </Link>
                                                </h3>
                                                
                                                <div className="cart-item-feature d-flex flex-column align-items-start mt-2 mb-3 gap-1">
                                                    <div className="font-11 text-muted d-flex align-items-center"><i className="bi bi-shield-check text-success me-1 fs-6"></i> گارانتی اصالت کالا</div>
                                                    
                                                    {variant && variant.attributes && variant.attributes.map((attr, idx) => {
                                                        const isColor = attr.attribute_name.includes('رنگ');
                                                        return (
                                                            <div key={idx} className="font-12 text-muted d-flex align-items-center mt-1">
                                                                {isColor ? (
                                                                    <>
                                                                        <span className="d-inline-block rounded-circle me-1 border border-ui shadow-sm" style={{width:'10px', height:'10px', backgroundColor: attr.value === 'مشکی' ? '#212529' : attr.value === 'سفید' ? '#f8f9fa' : '#ccc'}}></span>
                                                                        رنگ: <span className="text-dark fw-bold ms-1">{attr.value}</span>
                                                                    </>
                                                                ) : (
                                                                    <><i className="bi bi-check2-circle text-muted me-1"></i> {attr.attribute_name}: <span className="text-dark fw-bold ms-1">{attr.value}</span></>
                                                                )}
                                                            </div>
                                                        );
                                                    })}
                                                </div>

                                                <div className="product-box-suggest-price d-flex flex-column align-items-end justify-content-start border-top border-light pt-2">
                                                    {hasDiscount && (
                                                        <del className="font-12 text-muted mb-1">{(Number(product.base_price) * item.quantity).toLocaleString()}</del>
                                                    )}
                                                    <ins className="font-16 text-dark fw-900 text-decoration-none">
                                                        {Number(item.total_price).toLocaleString()} <span className="font-11 fw-normal text-muted">تومان</span>
                                                    </ins>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div className="cart-canvas-foot d-flex align-items-center justify-content-between mt-3 bg-light rounded-pill p-2 border border-ui">
                                            <div className="cart-canvas-count d-flex align-items-center gap-2 px-2">
                                                <button type="button" className="btn btn-sm btn-white rounded-circle shadow-sm border-0 d-flex align-items-center justify-content-center p-0 hover-lift" style={{width:'26px', height:'26px'}} onClick={() => handleUpdateQuantity(item.id, item.quantity, 'decrease', maxInventory)} disabled={item.quantity <= 1}><i className="bi bi-dash text-danger fw-bold"></i></button>
                                                <span className="fw-900 font-14 text-dark">{item.quantity}</span>
                                                <button type="button" className="btn btn-sm btn-white rounded-circle shadow-sm border-0 d-flex align-items-center justify-content-center p-0 hover-lift" style={{width:'26px', height:'26px'}} onClick={() => handleUpdateQuantity(item.id, item.quantity, 'increase', maxInventory)} disabled={item.quantity >= maxInventory}><i className="bi bi-plus text-success fw-bold"></i></button>
                                            </div>
                                            <div className="cart-canvas-delete">
                                                <button onClick={() => handleRemove(item.id)} className="btn btn-sm btn-outline-danger rounded-pill px-3 py-1 font-12 fw-bold shadow-sm hover-lift"><i className="bi bi-trash3 me-1"></i> حذف کالا</button>
                                            </div>
                                        </div>
                                        
                                    </div>
                                </li>
                            );
                        })
                    )}
                </ul>

                {cartItems.length > 0 && (
                    <div className="cart-canvas-foots bg-white shadow-lg p-3 border-top border-ui mt-auto rounded-top-4" style={{ zIndex: 10 }}>
                        <div className="row align-items-center mb-3">
                            <div className="col-6">
                                <div className="cart-canvas-foot-sum">
                                    <p className="text-muted mb-1 font-13">مبلغ قابل پرداخت</p>
                                    <h5 className="font-18 fw-900 text-dark m-0">{totalPayableAmount.toLocaleString()} <span className="font-12 fw-normal text-muted">تومان</span></h5>
                                </div>
                            </div>
                            <div className="col-6">
                                <div className="cart-canvas-foot-link text-end">
                                    <button onClick={() => { closeOffcanvas(); navigate('/checkout'); }} className="btn border-0 main-color-two-bg text-white fw-bold font-14 px-3 rounded-pill py-2 shadow-sm w-100 d-flex justify-content-center align-items-center gap-2 hover-lift">
                                        تکمیل خرید <i className="bi bi-arrow-left fs-5"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                        {totalDiscount > 0 && (
                            <div className="bg-danger bg-opacity-10 border border-danger border-opacity-25 rounded-pill p-2 text-center mt-2 d-flex justify-content-center align-items-center gap-2">
                                <i className="bi bi-tags text-danger"></i>
                                <span className="font-12 fw-bold text-danger">شما در این خرید {totalDiscount.toLocaleString()} تومان سود کردید!</span>
                            </div>
                        )}
                    </div>
                )}
            </div>
            <style jsx="true">{`
                .hover-lift { transition: transform 0.2s ease; }
                .hover-lift:hover { transform: translateY(-3px); }
                .text-overflow-2 { overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
                .custom-scrollbar::-webkit-scrollbar { width: 4px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #dee2e6; border-radius: 10px; }
            `}</style>
        </section>
    );
};

export default CartDrawer;