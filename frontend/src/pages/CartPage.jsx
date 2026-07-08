import React, { useState, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { CartContext } from '../context/CartContext';

const CartPage = () => {
    const navigate = useNavigate();
    const { cartItems, cartLoading, updateQuantity, removeFromCart } = useContext(CartContext);
    
    const [activeTab, setActiveTab] = useState('cart');
    
    const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
    const showToast = (message, type = 'success') => {
        setToast({ show: true, message, type });
        setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 3000);
    };

    const handleRemove = async (itemId) => {
        if (window.confirm("آیا از حذف این کالا اطمینان دارید؟")) {
            try {
                await removeFromCart(itemId);
                showToast("کالا از سبد خرید حذف شد.", "success");
            } catch (error) {
                showToast("خطا در حذف کالا.", "danger");
            }
        }
    };

    const handleUpdateQuantity = async (itemId, currentQty, type, inventory) => {
        let newQty = currentQty;
        if (type === 'increase' && currentQty < inventory) newQty += 1;
        if (type === 'decrease' && currentQty > 1) newQty -= 1;
        
        if (newQty !== currentQty) {
            try {
                await updateQuantity(itemId, newQty);
            } catch (error) {
                showToast("خطا در بروزرسانی تعداد.", "danger");
            }
        }
    };

    if (cartLoading) {
        return (
            <div className="text-center py-5 my-5 min-vh-100 d-flex align-items-center justify-content-center">
                <div className="spinner-border text-danger" style={{width: '4rem', height:'4rem'}}></div>
            </div>
        );
    }

    const totalItemsCount = cartItems.reduce((acc, item) => acc + item.quantity, 0);
    const totalPayableAmount = cartItems.reduce((acc, item) => acc + Number(item.total_price), 0);
    const totalRealValue = cartItems.reduce((acc, item) => acc + (Number(item.product_details.base_price) * item.quantity), 0);
    const totalDiscount = totalRealValue > totalPayableAmount ? totalRealValue - totalPayableAmount : 0;

    return (
        <React.Fragment>
            <div className={`custom-toast ${toast.show ? 'show' : ''} bg-${toast.type} shadow-lg d-flex align-items-center gap-3`}>
                <i className={`bi ${toast.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-circle-fill'} fs-3 text-white`}></i>
                <span className="font-14 fw-bold text-white lh-base">{toast.message}</span>
            </div>

            <section className="content min-vh-100">
                <div className="container-fluid">
                    <ul className="nav nav-tabs mt-xl-3 mt-5 pt-xl-0 pt-5 border-bottom border-light mb-4" role="tablist">
                        <li className="nav-item">
                            <button 
                                className={`nav-link bg-transparent fw-bold font-16 border-0 ${activeTab === 'cart' ? 'active text-danger border-danger border-bottom-2' : 'text-muted'}`} 
                                onClick={() => setActiveTab('cart')}
                            >
                                سبد خرید
                                <span className="badge bg-danger rounded-pill ms-2">{cartItems.length}</span>
                            </button>
                        </li>
                        <li className="nav-item">
                            <button 
                                className={`nav-link bg-transparent fw-bold font-16 border-0 ${activeTab === 'next' ? 'active text-danger border-danger border-bottom-2' : 'text-muted'}`} 
                                onClick={() => setActiveTab('next')}
                            >
                                خرید بعدی
                            </button>
                        </li>
                    </ul>

                    <div className="tab-content">
                        {activeTab === 'cart' && (
                            <div className="tab-pane fade show active animate-fade-in">
                                {cartItems.length === 0 ? (
                                    <div className="text-center py-5 my-5 d-flex flex-column align-items-center justify-content-center bg-white rounded-4 shadow-sm border border-ui content-box">
                                        <img src="/assets/image/cart/empty-cart.svg" alt="empty-cart" style={{width: '200px', opacity: '0.8'}} className="mb-4" />
                                        <h3 className="fw-900 text-dark mb-3">سبد خرید شما خالی است!</h3>
                                        <p className="text-muted font-15 mb-4">می‌توانید برای مشاهده محصولات به صفحه فروشگاه مراجعه کنید.</p>
                                        <Link to="/shop" className="btn btn-danger rounded-pill px-5 py-3 shadow-sm hover-lift fw-bold font-15">
                                            بازگشت به فروشگاه
                                        </Link>
                                    </div>
                                ) : (
                                    <div className="row gy-4 my-1">
                                        <div className="col-xl-9">
                                            <div className="content-box bg-white rounded-4 shadow-sm border border-ui p-4 p-md-5">
                                                <div className="row align-items-center border-bottom border-light pb-3 mb-4">
                                                    <div className="col-12 col-md-8">
                                                        <h2 className="h5 fw-900 text-dark m-0 d-flex align-items-center gap-2">
                                                            <i className="bi bi-cart3 text-danger fs-3"></i> سبد خرید شما
                                                            <small className="text-muted font-14 ms-2 fw-normal">({totalItemsCount} کالا)</small>
                                                        </h2>
                                                    </div>
                                                </div>

                                                {cartItems.map((item, index) => {
                                                    const product = item.product_details;
                                                    const variant = item.variant_details;
                                                    const maxInventory = variant ? variant.inventory : product.base_inventory;
                                                    const hasDiscount = Number(product.base_price) > Number(item.unit_price);

                                                    return (
                                                        <div key={item.id} className={`border-bottom border-light py-4 ${index === cartItems.length - 1 ? 'border-0 pb-0' : ''}`}>
                                                            <div className="row align-items-center">
                                                                <div className="col-12 col-md-3 col-xl-2 text-center mb-4 mb-md-0">
                                                                    <Link to={`/product/${product.slug}`}>
                                                                        <img src={product.gallery?.[0]?.url || '/assets/image/product/product-no-bg.png'} className="img-thumbnail rounded-4 border-ui object-fit-contain shadow-sm hover-lift transition" alt={product.title} style={{height: '140px', width: '140px'}} />
                                                                    </Link>
                                                                    
                                                                    <div className="d-flex align-items-center justify-content-center bg-light rounded-pill border border-ui p-1 mt-3 mx-auto shadow-sm" style={{maxWidth: '130px'}}>
                                                                        <button type="button" className="btn btn-sm btn-white rounded-circle shadow-sm border-0 d-flex align-items-center justify-content-center p-0" style={{width:'32px', height:'32px'}} onClick={() => handleUpdateQuantity(item.id, item.quantity, 'decrease', maxInventory)} disabled={item.quantity <= 1}>
                                                                            <i className="bi bi-dash text-danger fw-bold fs-5"></i>
                                                                        </button>
                                                                        <span className="fw-900 font-16 text-dark w-100 text-center">{item.quantity}</span>
                                                                        <button type="button" className="btn btn-sm btn-white rounded-circle shadow-sm border-0 d-flex align-items-center justify-content-center p-0" style={{width:'32px', height:'32px'}} onClick={() => handleUpdateQuantity(item.id, item.quantity, 'increase', maxInventory)} disabled={item.quantity >= maxInventory}>
                                                                            <i className="bi bi-plus text-success fw-bold fs-5"></i>
                                                                        </button>
                                                                    </div>
                                                                </div>
                                                                
                                                                <div className="col-12 col-md-9 col-xl-10 ps-md-4">
                                                                    <Link to={`/product/${product.slug}`} className="text-decoration-none text-dark hover-text-danger transition">
                                                                        <h3 className="mb-3 font-16 fw-bold lh-lg text-overflow-2">{product.title}</h3>
                                                                    </Link>
                                                                    
                                                                    <div className="cart-item-feature d-flex flex-column align-items-start gap-2">
                                                                        {variant && variant.attributes.map((attr, idx) => {
                                                                            const isColor = attr.attribute_name.includes('رنگ');
                                                                            return (
                                                                                <div key={idx} className="d-flex align-items-center text-muted font-13 bg-light px-3 py-1 rounded-pill">
                                                                                    {isColor && <span className="d-inline-block rounded-circle me-2 border border-ui shadow-sm" style={{width:'12px', height:'12px', backgroundColor: attr.value === 'مشکی' ? '#212529' : attr.value === 'سفید' ? '#f8f9fa' : '#ccc'}}></span>}
                                                                                    {attr.attribute_name}: <strong className="text-dark ms-1">{attr.value}</strong>
                                                                                </div>
                                                                            )
                                                                        })}

                                                                        <div className="d-flex align-items-center mt-1 text-muted font-13">
                                                                            <i className="bi bi-shield-check text-success me-2 fs-5"></i> گارانتی اصالت و سلامت فیزیکی
                                                                        </div>
                                                                        <div className="d-flex align-items-center text-muted font-13">
                                                                            <i className="bi bi-shop-window text-primary me-2 fs-5"></i> فروشنده: <strong className="text-dark ms-1">آرک کالا</strong>
                                                                        </div>
                                                                    </div>
                                                                    
                                                                    <div className="d-flex flex-column flex-md-row align-items-md-end justify-content-between mt-4">
                                                                        <button onClick={() => handleRemove(item.id)} className="btn btn-sm text-danger font-14 fw-bold px-0 d-flex align-items-center mb-3 mb-md-0 hover-lift w-fit-content">
                                                                            <i className="bi bi-trash3 me-1 fs-5"></i> حذف از سبد
                                                                        </button>
                                                                        
                                                                        <div className="product-box-suggest-price text-start text-md-end">
                                                                            {hasDiscount && (
                                                                                <div className="text-muted font-14 mb-1"><del>{(Number(product.base_price) * item.quantity).toLocaleString()}</del></div>
                                                                            )}
                                                                            <div className="font-22 fw-900 text-dark">
                                                                                {Number(item.total_price).toLocaleString()} <span className="font-13 fw-normal text-muted ms-1">تومان</span>
                                                                            </div>
                                                                        </div>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        </div>
                                                    )
                                                })}
                                            </div>
                                            <p className="text-muted mt-3 font-13 lh-lg text-center text-md-start">
                                                <i className="bi bi-info-circle-fill text-info me-1"></i> در صورت اتمام موجودی، کالاها به طور خودکار از سبد حذف می‌شوند.
                                            </p>
                                        </div>

                                        <div className="col-xl-3">
                                            <div className="cart-canvases position-sticky bg-white rounded-4 shadow-sm border border-ui p-4" style={{top: '100px'}}>
                                                <h5 className="fw-900 text-dark border-bottom border-light pb-3 mb-4"><i className="bi bi-receipt me-2 text-danger"></i> صورتحساب</h5>
                                                
                                                <div className="d-flex mb-3 align-items-center justify-content-between">
                                                    <span className="text-muted font-14">قیمت کالاها</span>
                                                    <span className="font-15 text-dark fw-bold">{totalRealValue.toLocaleString()} تومان</span>
                                                </div>

                                                {totalDiscount > 0 && (
                                                    <div className="d-flex mb-3 align-items-center justify-content-between">
                                                        <span className="text-muted font-14">سود شما از خرید</span>
                                                        <span className="font-15 text-danger fw-bold">{(totalDiscount).toLocaleString()} تومان</span>
                                                    </div>
                                                )}

                                                <div className="d-flex mb-4 pb-4 border-bottom border-dashed align-items-center justify-content-between">
                                                    <span className="text-muted font-14">هزینه ارسال</span>
                                                    <span className="font-13 text-primary fw-bold">مرحله بعد</span>
                                                </div>

                                                <div className="d-flex mb-4 align-items-center justify-content-between">
                                                    <h5 className="fw-bold mb-0 font-16 text-dark">مبلغ قابل پرداخت</h5>
                                                    <p className="mb-0 font-22 text-success fw-900">{totalPayableAmount.toLocaleString()} <span className="font-13 text-muted fw-normal">تومان</span></p>
                                                </div>

                                                <div className="mt-4">
                                                    <button onClick={() => navigate('/checkout')} className="btn main-color-two-bg text-white py-3 fw-bold rounded-pill d-block w-100 shadow hover-lift fs-5 d-flex align-items-center justify-content-center gap-2">
                                                        <i className="bi bi-bag-check-fill fs-4"></i> ادامه و تسویه حساب
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                        )}

                        {activeTab === 'next' && (
                            <div className="tab-pane fade show active animate-fade-in">
                                <div className="text-center py-5 my-5 bg-white rounded-4 shadow-sm border border-ui content-box">
                                    <i className="bi bi-bag-heart text-muted opacity-50 d-block mb-4" style={{fontSize: '5rem'}}></i>
                                    <h3 className="fw-900 text-dark mb-3">لیست خرید بعدی خالی است</h3>
                                    <p className="text-muted font-15 mb-0">شما کالایی را به لیست خرید بعدی اضافه نکرده‌اید.</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </section>

            <style jsx="true">{`
                .hover-shadow:hover { box-shadow: 0 1rem 2rem rgba(0,0,0,.08)!important; transform: translateY(-3px); }
                .hover-lift { transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s; }
                .hover-lift:hover { transform: translateY(-2px); box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important; }
                .hover-bg-light:hover { background-color: #f8f9fa!important; }
                .hover-text-danger:hover { color: #ef4056!important; }
                .transition { transition: all 0.3s ease; }
                .w-fit-content { width: fit-content; }
                
                .text-overflow-2 { overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
                .border-dashed { border-style: dashed !important; border-color: #dee2e6 !important;}
                .border-bottom-2 { border-bottom-width: 2px !important; }
                
                .animate-fade-in { animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }

                .custom-toast {
                    position: fixed;
                    bottom: 30px;
                    left: -400px;
                    min-width: 300px;
                    padding: 16px 24px;
                    border-radius: 16px;
                    z-index: 999999;
                    transition: left 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55);
                }
                .custom-toast.show { left: 30px; }
                
                @media (max-width: 768px) {
                    .custom-toast {
                        left: 50% !important;
                        transform: translateX(-50%);
                        bottom: -100px;
                        width: 90%;
                        min-width: unset;
                        transition: bottom 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
                    }
                    .custom-toast.show { 
                        bottom: 20px !important; 
                        left: 50% !important;
                    }
                }
            `}</style>
        </React.Fragment>
    );
};

export default CartPage;