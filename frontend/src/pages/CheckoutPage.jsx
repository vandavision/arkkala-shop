import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { getCart, getShippingMethods, checkout, validateCoupon } from '../api/cartApi';
import { requestPayment } from '../api/paymentApi';

const resolveImageUrl = (url) => {
    if (!url) return '/assets/image/product/product-no-bg.png';
    if (url.startsWith('http') || url.startsWith('data:')) return url;
    
    let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    baseUrl = baseUrl.replace(/\/api\/?$/, '');
    
    return `${baseUrl}${url.startsWith('/') ? '' : '/'}${url}`;
};

const CheckoutPage = () => {
    const { user } = useContext(AuthContext);
    const [cartItems, setCartItems] = useState([]);
    const [shippingMethods, setShippingMethods] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    
    const [formData, setFormData] = useState({
        guest_first_name: '', 
        guest_last_name: '',  
        guest_phone: '',
        title: 'خانه',
        province: '',
        city: '',
        postal_address: '',
        postal_code: '',
        plaque: '',
        building_unit: '',
        shipping_method_id: '',
        coupon_code: ''
    });

    const [couponInput, setCouponInput] = useState('');
    const [couponData, setCouponData] = useState(null);
    const [isApplyingCoupon, setIsApplyingCoupon] = useState(false);
    
    const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
    const showToast = (message, type = 'success') => {
        setToast({ show: true, message, type });
        setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 4000);
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [cartData, shippingData] = await Promise.all([
                    getCart(),
                    getShippingMethods()
                ]);
                setCartItems(cartData);
                setShippingMethods(shippingData);
                if (shippingData && shippingData.length > 0) {
                    setFormData(prev => ({ ...prev, shipping_method_id: shippingData[0].id }));
                }
            } catch (err) {
                console.error(err);
                alert("خطا در دریافت اطلاعات. لطفا صفحه را مجددا بارگذاری کنید.");
            } finally {
                setLoading(false);
            }
        };
        fetchData();
        window.scrollTo(0,0);
    }, []);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleApplyCoupon = async () => {
        if (!couponInput.trim()) return showToast("لطفا کد تخفیف را وارد کنید.", "warning");
        setIsApplyingCoupon(true);
        try {
            const data = await validateCoupon(couponInput.trim());
            setCouponData(data);
            setFormData(prev => ({...prev, coupon_code: couponInput.trim()}));
            showToast("کد تخفیف با موفقیت اعمال شد.", "success");
        } catch (error) {
            showToast(error.response?.data?.error || "کد تخفیف نامعتبر است یا منقضی شده است.", "danger");
            setCouponData(null);
            setFormData(prev => ({...prev, coupon_code: ''}));
        } finally {
            setIsApplyingCoupon(false);
        }
    };

    const handleCheckout = async (e) => {
        e.preventDefault();
        
        if (!user && (!formData.guest_phone || !formData.guest_first_name || !formData.guest_last_name)) {
            return showToast("لطفا نام، نام خانوادگی و شماره موبایل خود را وارد کنید.", "warning");
        }

        setIsSubmitting(true);
        try {
            const order = await checkout(formData);
            const payment = await requestPayment(order.id, 'zarinpal');
            window.location.href = payment.payment_url;
        } catch (error) {
            showToast(error.response?.data?.error || "خطا در برقراری ارتباط با سرور.", "danger");
            setIsSubmitting(false);
        }
    };

    if (loading) return <div className="text-center py-5 my-5 min-vh-100 d-flex align-items-center justify-content-center"><div className="spinner-border text-danger" style={{width: '4rem', height:'4rem', borderWidth:'0.3rem'}}></div></div>;

    if (cartItems.length === 0) {
        return (
            <div className="text-center py-5 my-5 min-vh-100 d-flex flex-column align-items-center justify-content-center">
                <img src="/assets/image/cart/empty-cart.svg" alt="empty-cart" style={{width: '250px', opacity: '0.8'}} className="mb-4" />
                <h3 className="fw-900 text-dark mb-4">سبد خرید شما خالی است!</h3>
                <Link to="/shop" className="btn btn-danger rounded-pill px-5 py-3 shadow-sm hover-lift fw-bold font-15">بازگشت به فروشگاه</Link>
            </div>
        );
    }

    const totalItemsAmount = cartItems.reduce((acc, item) => acc + Number(item.total_price), 0);
    const totalWeight = cartItems.reduce((acc, item) => acc + (Number(item.product_details?.weight || 500) * item.quantity), 0);
    
    let shippingCost = 0;
    const selectedMethod = shippingMethods.find(m => m.id === formData.shipping_method_id);
    if (selectedMethod && !selectedMethod.is_pay_on_delivery) {
        const methodBaseCost = Number(selectedMethod.base_cost);
        const basePostCost = 35000;
        const weightPenalty = Math.floor(totalWeight / 500) * 5000;
        const isTehran = formData.province.includes('تهران');
        const distanceMultiplier = isTehran ? 1.0 : 1.35;
        const estimatedDynamicCost = Math.floor((basePostCost + weightPenalty) * distanceMultiplier);
        
        shippingCost = methodBaseCost + estimatedDynamicCost;
    }
    
    let discountAmount = 0;
    if (couponData) {
        discountAmount = (totalItemsAmount * couponData.discount_percent) / 100;
        if (couponData.max_discount_amount && discountAmount > Number(couponData.max_discount_amount)) {
            discountAmount = Number(couponData.max_discount_amount);
        }
    }
    
    const taxRate = 0.10; 
    const subtotal = totalItemsAmount - discountAmount;
    const taxAmount = subtotal * taxRate;
    const payableAmount = subtotal + taxAmount + shippingCost;

    return (
        <section className="checkout-page py-5 bg-light min-vh-100">
            <div className={`custom-toast ${toast.show ? 'show' : ''} bg-${toast.type} shadow-lg d-flex align-items-center gap-3`}>
                <i className={`bi ${toast.type === 'success' ? 'bi-check-circle-fill' : toast.type === 'warning' ? 'bi-exclamation-triangle-fill' : 'bi-x-circle-fill'} fs-3 text-white`}></i>
                <span className="font-14 fw-bold text-white lh-base">{toast.message}</span>
            </div>

            <div className="container-fluid">
                <div className="row gy-4">
                    
                    <div className="col-lg-8">
                        <div className="bg-white p-4 p-md-5 rounded-4 shadow-sm border border-ui h-100">
                            <div className="border-bottom border-light pb-3 mb-4">
                                <h3 className="fw-900 text-dark d-flex align-items-center gap-2 m-0"><i className="bi bi-geo-alt-fill text-danger fs-3"></i> اطلاعات ارسال</h3>
                                {!user && <p className="text-muted mt-3 font-13 bg-info bg-opacity-10 border border-info border-opacity-25 rounded-3 p-3 mb-0"><i className="bi bi-info-circle-fill text-info me-1 fs-5 align-middle"></i> شما به عنوان <strong>مهمان</strong> در حال خرید هستید. جهت ارسال و پیگیری سفارش، پر کردن مشخصات الزامی است.</p>}
                            </div>

                            <form id="checkoutForm" onSubmit={handleCheckout}>
                                <div className="row gy-4">
                                    {!user && (
                                        <>
                                            <div className="col-md-6">
                                                <label className="fw-bold font-13 text-dark mb-2">نام <span className="text-danger">*</span></label>
                                                <input type="text" name="guest_first_name" value={formData.guest_first_name} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light focus-white" placeholder="نام خود را وارد کنید" required />
                                            </div>
                                            <div className="col-md-6">
                                                <label className="fw-bold font-13 text-dark mb-2">نام خانوادگی <span className="text-danger">*</span></label>
                                                <input type="text" name="guest_last_name" value={formData.guest_last_name} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light focus-white" placeholder="نام خانوادگی خود را وارد کنید" required />
                                            </div>
                                            <div className="col-12">
                                                <label className="fw-bold font-13 text-dark mb-2">شماره موبایل <span className="text-danger">*</span></label>
                                                <input type="text" name="guest_phone" value={formData.guest_phone} onChange={handleChange} className="form-control border-ui py-3 font-14 rounded-3 text-start shadow-sm bg-light focus-white" placeholder="09123456789" required />
                                            </div>
                                        </>
                                    )}
                                    
                                    <div className="col-12"><hr className="border-light m-0"/></div>

                                    <div className="col-md-6">
                                        <label className="fw-bold font-13 text-dark mb-2">استان <span className="text-danger">*</span></label>
                                        <input type="text" name="province" value={formData.province} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light focus-white" placeholder="مثال: تهران" required />
                                    </div>
                                    <div className="col-md-6">
                                        <label className="fw-bold font-13 text-dark mb-2">شهر <span className="text-danger">*</span></label>
                                        <input type="text" name="city" value={formData.city} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light focus-white" placeholder="مثال: تهران" required />
                                    </div>
                                    <div className="col-12">
                                        <label className="fw-bold font-13 text-dark mb-2">آدرس دقیق پستی <span className="text-danger">*</span></label>
                                        <textarea name="postal_address" value={formData.postal_address} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-4 shadow-sm bg-light focus-white lh-lg" rows="3" placeholder="محله، خیابان اصلی، کوچه..." required></textarea>
                                    </div>
                                    <div className="col-md-4">
                                        <label className="fw-bold font-13 text-dark mb-2">کد پستی (۱۰ رقمی) <span className="text-danger">*</span></label>
                                        <input type="text" name="postal_code" value={formData.postal_code} onChange={handleChange} className="form-control border-ui py-3 font-14 rounded-3 text-start shadow-sm bg-light focus-white" placeholder="1234567890" required />
                                    </div>
                                    <div className="col-md-4">
                                        <label className="fw-bold font-13 text-dark mb-2">پلاک <span className="text-danger">*</span></label>
                                        <input type="text" name="plaque" value={formData.plaque} onChange={handleChange} className="form-control border-ui py-3 font-14 rounded-3 shadow-sm bg-light focus-white text-start" placeholder="12" required />
                                    </div>
                                    <div className="col-md-4">
                                        <label className="fw-bold font-13 text-dark mb-2">واحد</label>
                                        <input type="text" name="building_unit" value={formData.building_unit} onChange={handleChange} className="form-control border-ui py-3 font-14 rounded-3 shadow-sm bg-light focus-white text-start" placeholder="اختیاری" />
                                    </div>

                                    <div className="col-12 mt-5">
                                        <h5 className="fw-900 text-dark mb-3"><i className="bi bi-truck text-primary fs-4 me-2"></i> روش ارسال را انتخاب کنید</h5>
                                        <div className="row gy-3">
                                            {shippingMethods.map(method => (
                                                <div className="col-md-6" key={method.id}>
                                                    <label className={`w-100 border rounded-4 p-3 cursor-pointer transition d-flex align-items-center justify-content-between ${formData.shipping_method_id === method.id ? 'border-danger bg-danger bg-opacity-10 shadow-sm' : 'border-ui bg-white hover-shadow'}`}>
                                                        <div className="d-flex align-items-center gap-3">
                                                            <input type="radio" name="shipping_method_id" value={method.id} checked={formData.shipping_method_id === method.id} onChange={handleChange} className="form-check-input mt-0 shadow-none cursor-pointer" style={{width:'22px', height:'22px'}} />
                                                            <div>
                                                                <span className="d-block fw-bold font-14 text-dark mb-1">{method.name}</span>
                                                                {method.description && <span className="font-12 text-muted">{method.description}</span>}
                                                            </div>
                                                        </div>
                                                        <span className={`badge ${method.is_pay_on_delivery ? 'bg-warning text-dark' : 'bg-primary'} font-12 py-2 px-3 rounded-pill`}>
                                                            {method.is_pay_on_delivery ? 'پس کرایه' : `پرداخت آنلاین`}
                                                        </span>
                                                    </label>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>

                    <div className="col-lg-4">
                        <div className="position-sticky" style={{top: '100px'}}>
                            
                            <div className="bg-white p-4 rounded-4 shadow-sm border border-ui mb-4">
                                <h6 className="fw-bold text-dark mb-3 d-flex align-items-center gap-2"><i className="bi bi-ticket-perforated text-danger fs-4"></i> کد تخفیف دارید؟</h6>
                                <div className="input-group mb-2 shadow-sm rounded-3">
                                    <input 
                                        type="text" 
                                        className="form-control font-13 py-3 border-ui shadow-none rounded-start-3 bg-light focus-white text-center" 
                                        placeholder="مثال: SPRING1403" 
                                        value={couponInput}
                                        onChange={(e) => setCouponInput(e.target.value)}
                                        disabled={couponData !== null}
                                        autoComplete="off"
                                    />
                                    {couponData ? (
                                        <button type="button" className="btn btn-danger text-white fw-bold px-4 rounded-end-3" onClick={() => {setCouponData(null); setFormData(p=>({...p, coupon_code:''})); setCouponInput('');}}>حذف</button>
                                    ) : (
                                        <button type="button" className="btn btn-dark text-white fw-bold px-4 rounded-end-3" onClick={handleApplyCoupon} disabled={isApplyingCoupon}>
                                            {isApplyingCoupon ? <div className="spinner-border spinner-border-sm"></div> : 'اعمال'}
                                        </button>
                                    )}
                                </div>
                                {couponData && (
                                    <div className="mt-3 p-2 bg-success bg-opacity-10 border border-success border-opacity-25 rounded-3 text-center">
                                        <span className="font-12 fw-bold text-success"><i className="bi bi-check-circle-fill me-1"></i> تخفیف روی فاکتور اعمال شد.</span>
                                    </div>
                                )}
                            </div>

                            <div className="bg-white p-4 p-md-5 rounded-4 shadow-sm border border-ui">
                                <h5 className="fw-900 text-dark border-bottom border-light pb-3 mb-4 d-flex align-items-center gap-2"><i className="bi bi-receipt text-danger fs-4"></i> صورتحساب نهایی</h5>
                                
                                <div className="d-flex flex-column gap-3 mb-4 overflow-auto custom-scrollbar pe-2" style={{maxHeight: '220px'}}>
                                    {cartItems.map(item => {
                                        const product = item.product_details || {};
                                        
                                        const mainImageObj = product?.gallery?.find(img => img.is_main) || product?.gallery?.[0];
                                        const rawUrl = mainImageObj?.url || product?.image_url || product?.image;
                                        const imageUrl = resolveImageUrl(rawUrl);
                                        
                                        return (
                                            <div key={item.id} className="d-flex align-items-center gap-3 border-bottom border-light pb-3">
                                                <div className="bg-light rounded-3 p-1 border border-ui">
                                                    <img src={imageUrl} alt={product.title || 'محصول'} style={{width:'45px', height:'45px', objectFit:'contain'}} onError={(e) => { e.target.src = '/assets/image/product/product-no-bg.png'; }} />
                                                </div>
                                                <div className="flex-grow-1">
                                                    <h6 className="font-13 fw-bold text-dark text-overflow-1 m-0 mb-1">{product.title}</h6>
                                                    <div className="d-flex align-items-center justify-content-between">
                                                        <span className="font-12 text-muted px-2 py-1 bg-light rounded-pill border">{item.quantity} عدد</span>
                                                        <span className="font-13 fw-bold text-dark">{Number(item.total_price).toLocaleString()} تومان</span>
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>

                                <ul className="list-unstyled p-0 m-0 border-top border-light pt-4">
                                    <li className="d-flex justify-content-between align-items-center mb-3">
                                        <span className="font-13 text-muted">مبلغ کل کالاها ({cartItems.reduce((acc, i) => acc + i.quantity, 0)} کالا)</span>
                                        <span className="font-15 text-dark fw-bold">{totalItemsAmount.toLocaleString()} <span className="font-11 text-muted fw-normal">تومان</span></span>
                                    </li>
                                    
                                    {discountAmount > 0 && (
                                        <li className="d-flex justify-content-between align-items-center mb-3 animate-fade-in">
                                            <span className="font-13 text-danger fw-bold d-flex align-items-center gap-1"><i className="bi bi-tag-fill"></i> تخفیف اعمال شده</span>
                                            <span className="font-15 text-danger fw-bold">- {discountAmount.toLocaleString()} <span className="font-11 fw-normal">تومان</span></span>
                                        </li>
                                    )}

                                    <li className="d-flex justify-content-between align-items-center mb-3">
                                        <span className="font-13 text-muted">هزینه ارسال <span className="font-11">({(totalWeight / 1000).toFixed(1)} کیلوگرم)</span></span>
                                        {shippingCost > 0 ? (
                                            <span className="font-14 text-dark fw-bold">{shippingCost.toLocaleString()} <span className="font-11 text-muted fw-normal">تومان</span></span>
                                        ) : (
                                            <span className="font-13 text-primary fw-bold px-2 py-1 bg-primary bg-opacity-10 rounded-pill">{selectedMethod?.is_pay_on_delivery ? 'پس‌کرایه (هنگام تحویل)' : 'رایگان'}</span>
                                        )}
                                    </li>

                                    <li className="d-flex justify-content-between align-items-center mb-4 pb-4 border-bottom border-dashed">
                                        <span className="font-13 text-muted d-flex align-items-center gap-1" title="محاسبه شده بر اساس 10 درصد مالیات"><i className="bi bi-info-circle"></i> مالیات (۱۰٪)</span>
                                        <span className="font-14 text-dark fw-bold">{taxAmount.toLocaleString()} <span className="font-11 text-muted fw-normal">تومان</span></span>
                                    </li>

                                    <li className="d-flex flex-column align-items-center mb-4 bg-light p-3 rounded-4 border border-light shadow-sm">
                                        <span className="font-14 text-dark fw-bold mb-2">مبلغ قابل پرداخت</span>
                                        <span className="font-26 text-danger fw-900">{payableAmount.toLocaleString()} <span className="font-14 fw-normal text-muted">تومان</span></span>
                                    </li>
                                </ul>

                                <button type="submit" form="checkoutForm" disabled={isSubmitting} className="btn main-color-two-bg w-100 text-white rounded-pill py-3 fw-bold shadow hover-lift fs-5 d-flex align-items-center justify-content-center gap-2">
                                    {isSubmitting ? <div className="spinner-border spinner-border-sm text-white"></div> : <i className="bi bi-credit-card-fill fs-4"></i>}
                                    ثبت و اتصال به درگاه
                                </button>
                            </div>
                        </div>
                    </div>

                </div>
            </div>

            <style jsx="true">{`
                .cursor-pointer { cursor: pointer; }
                .hover-shadow:hover { box-shadow: 0 1rem 2rem rgba(0,0,0,.08)!important; transform: translateY(-3px); }
                .hover-lift { transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s; }
                .hover-lift:hover { transform: translateY(-2px); box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important; }
                .transition { transition: all 0.3s ease; }
                .text-overflow-1 { overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; }
                .border-dashed { border-style: dashed !important; border-color: #dee2e6 !important;}
                
                .focus-white:focus { background-color: #ffffff !important; box-shadow: 0 0 0 4px rgba(239, 64, 86, 0.1) !important; border-color: #ef4056 !important;}
                
                .animate-fade-in { animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(-10px); } to { opacity: 1; transform: translateY(0); } }

                .custom-scrollbar::-webkit-scrollbar { width: 5px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: #f8f9fa; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #dee2e6; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #ced4da; }
                
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
        </section>
    );
};

export default CheckoutPage;