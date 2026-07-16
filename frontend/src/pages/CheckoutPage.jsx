import React, { useState, useEffect, useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { getCart, getShippingMethods, checkout, validateCoupon } from '../api/cartApi';
import { getUserAddresses } from '../api/authApi';
import { requestPayment } from '../api/paymentApi';
import { SiteContext } from '../context/SiteContext';

const resolveImageUrl = (url) => {
    if (!url) return '/assets/image/product/product-no-bg.png';
    if (url.startsWith('http') || url.startsWith('data:')) return url;
    let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    baseUrl = baseUrl.replace(/\/api\/?$/, '');
    return `${baseUrl}${url.startsWith('/') ? '' : '/'}${url}`;
};

const getInitialFormData = () => {
    const defaultData = {
        guest_first_name: '', guest_last_name: '', guest_phone: '', guest_email: '', guest_password: '', 
        title: 'خانه', country: 'ایران', province: '', city: '', postal_address: '', postal_code: '', plaque: '', building_unit: '',
        shipping_method_id: '', coupon_code: ''
    };
    const savedData = localStorage.getItem('arkkala_checkout_form');
    if (savedData) {
        try {
            const parsedData = JSON.parse(savedData);
            return { ...defaultData, ...parsedData, country: 'ایران', title: 'خانه' };
        } catch (e) {}
    }
    return defaultData;
};

const CheckoutPage = () => {
    const navigate = useNavigate();
    const { user, authMode } = useContext(AuthContext);
    const { settings } = useContext(SiteContext);
    const isEmailMode = authMode === 'EMAIL';

    const [cartItems, setCartItems] = useState([]);
    const [shippingMethods, setShippingMethods] = useState([]);
    const [userAddresses, setUserAddresses] = useState([]);
    const [selectedAddressId, setSelectedAddressId] = useState('new');
    const [loading, setLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    
    const [formData, setFormData] = useState(getInitialFormData);
    const [couponInput, setCouponInput] = useState(formData.coupon_code || '');
    const [couponData, setCouponData] = useState(null);
    const [isApplyingCoupon, setIsApplyingCoupon] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    
    const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
    const showToast = (message, type = 'success') => {
        setToast({ show: true, message, type });
        setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 4000);
    };

    const isPickup = React.useMemo(() => {
        const method = shippingMethods.find(m => m.id === formData.shipping_method_id);
        return method ? method.name.includes('حضوری') : false;
    }, [shippingMethods, formData.shipping_method_id]);

    useEffect(() => {
        localStorage.setItem('arkkala_checkout_form', JSON.stringify(formData));
    }, [formData]);

    useEffect(() => {
        if (user) {
            setFormData(prev => ({
                ...prev,
                guest_first_name: user.first_name || prev.guest_first_name,
                guest_last_name: user.last_name || prev.guest_last_name,
                guest_phone: user.phone_number || prev.guest_phone,
                guest_email: user.email || prev.guest_email,
            }));
        }
    }, [user]);

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
                    const methodExists = shippingData.find(m => m.id === formData.shipping_method_id);
                    if (!methodExists) {
                        setFormData(prev => ({ ...prev, shipping_method_id: shippingData[0].id }));
                    }
                }

                if (user) {
                    const addressesResponse = await getUserAddresses();
                    const addrs = addressesResponse.results || addressesResponse || [];
                    setUserAddresses(addrs);
                    if (addrs.length > 0) {
                        const defaultAddr = addrs.find(a => a.is_default) || addrs[0];
                        setSelectedAddressId(defaultAddr.uuid || defaultAddr.id);
                    }
                }

                if (formData.coupon_code) {
                    try {
                        const data = await validateCoupon(formData.coupon_code);
                        setCouponData(data);
                    } catch (e) {
                        setFormData(prev => ({...prev, coupon_code: ''}));
                        setCouponInput('');
                    }
                }
            } catch (err) {
                showToast("خطا در دریافت اطلاعات اولیه سیستم.", "danger");
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [user]);

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
        
        if (!user) {
            if (isEmailMode && (!formData.guest_email || !formData.guest_password || !formData.guest_first_name || !formData.guest_last_name)) {
                return showToast("لطفاً نام، نام خانوادگی، ایمیل و رمز عبور خود را برای ساخت حساب وارد کنید.", "warning");
            } else if (!isEmailMode && (!formData.guest_phone || !formData.guest_first_name || !formData.guest_last_name)) {
                return showToast("لطفاً نام، نام خانوادگی و شماره موبایل خود را وارد کنید.", "warning");
            }
        }

        if (!formData.shipping_method_id) {
            return showToast("لطفاً یک روش ارسال انتخاب کنید.", "danger");
        }

        let finalSubmissionData = { ...formData, country: 'ایران' };

        if (isPickup) {
            finalSubmissionData = {
                ...finalSubmissionData,
                province: 'دریافت حضوری',
                city: 'فروشگاه',
                postal_address: 'تحویل در محل فروشگاه توسط شخص',
                postal_code: '1111111111',
                plaque: '0',
                title: 'دریافت حضوری'
            };
        } else {
            if (user && selectedAddressId !== 'new') {
                const addr = userAddresses.find(a => (a.uuid || a.id) === selectedAddressId);
                if (addr) {
                    finalSubmissionData = {
                        ...finalSubmissionData,
                        guest_first_name: addr.recipient_first_name,
                        guest_last_name: addr.recipient_last_name,
                        guest_phone: addr.recipient_phone,
                        province: addr.province,
                        city: addr.city,
                        postal_address: addr.postal_address,
                        postal_code: addr.postal_code,
                        plaque: addr.plaque,
                        building_unit: addr.building_unit,
                        title: addr.title,
                    };
                }
            } else {
                if (!finalSubmissionData.province || !finalSubmissionData.city || !finalSubmissionData.postal_address) {
                    return showToast("لطفا آدرس پستی را کامل کنید.", "warning");
                }
            }
        }

        setIsSubmitting(true);
        try {
            const order = await checkout(finalSubmissionData);
            const payment = await requestPayment(order.id, 'zarinpal');
            localStorage.removeItem('arkkala_checkout_form');
            window.location.href = payment.payment_url;
        } catch (error) {
            const resData = error.response?.data;
            let errorMsg = "خطا در ارتباط با سرور.";
            if (resData) {
                if (resData.error) errorMsg = resData.error;
                else if (typeof resData === 'object') {
                    const firstKey = Object.keys(resData)[0];
                    errorMsg = `خطا در فیلد (${firstKey}): ${resData[firstKey][0]}`;
                }
            }
            showToast(errorMsg, "danger");
            setIsSubmitting(false);
        }
    };

    if (loading) return <main className="text-center py-5 my-5 min-vh-100 d-flex align-items-center justify-content-center" aria-label="در حال بارگذاری"><div className="spinner-border text-danger" style={{width: '4rem', height:'4rem', borderWidth:'0.3rem'}}></div></main>;

    if (cartItems.length === 0) {
        return (
            <main className="text-center py-5 my-5 min-vh-100 d-flex flex-column align-items-center justify-content-center">
                <img src="/assets/image/cart/empty-cart.svg" alt="سبد خرید شما خالی است" style={{width: '250px', opacity: '0.8'}} className="mb-4" />
                <h1 className="fw-900 text-dark mb-4 h3">سبد خرید شما خالی است!</h1>
                <Link to="/shop" className="btn btn-danger rounded-pill px-5 py-3 shadow-sm hover-lift fw-bold font-15">بازگشت به فروشگاه</Link>
            </main>
        );
    }

    const totalItemsAmount = cartItems.reduce((acc, item) => acc + Number(item.total_price), 0);
    const totalWeight = cartItems.reduce((acc, item) => acc + (Number(item.product_details?.weight || 500) * item.quantity), 0);
    
    let shippingCost = 0;
    const selectedMethod = shippingMethods.find(m => m.id === formData.shipping_method_id);
    
    if (selectedMethod && !isPickup && !selectedMethod.is_pay_on_delivery) {
        const methodBaseCost = Number(selectedMethod.base_cost || 0);
        const basePostCost = 35000;
        const weightPenalty = Math.floor(totalWeight / 500) * 5000;
        const isTehran = formData.province ? formData.province.includes('تهران') : false;
        const distanceMultiplier = isTehran ? 1.0 : 1.35;
        shippingCost = methodBaseCost + Math.floor((basePostCost + weightPenalty) * distanceMultiplier);
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
        <main className="checkout-page py-5 bg-light min-vh-100">
            <div className={`custom-toast ${toast.show ? 'show' : ''} bg-${toast.type} shadow-lg d-flex align-items-center gap-3`} role="alert" aria-live="assertive" aria-atomic="true">
                <i className={`bi ${toast.type === 'success' ? 'bi-check-circle-fill' : toast.type === 'warning' ? 'bi-exclamation-triangle-fill' : 'bi-x-circle-fill'} fs-3 text-white`} aria-hidden="true"></i>
                <span className="font-14 fw-bold text-white lh-base">{toast.message}</span>
            </div>

            <div className="container-fluid">
                <div className="row gy-4">
                    <section className="col-lg-8" aria-label="اطلاعات ارسال کالا">
                        <div className="bg-white p-4 p-md-5 rounded-4 shadow-sm border border-ui h-100">
                            <header className="border-bottom border-light pb-3 mb-4">
                                <h1 className="h3 fw-900 text-dark d-flex align-items-center gap-2 m-0">
                                    <i className="bi bi-geo-alt-fill text-danger fs-3" aria-hidden="true"></i> اطلاعات ارسال
                                </h1>
                                {!user && <p className="text-muted mt-3 font-13 bg-info bg-opacity-10 border border-info border-opacity-25 rounded-3 p-3 mb-0"><i className="bi bi-info-circle-fill text-info me-1 fs-5 align-middle" aria-hidden="true"></i> شما به عنوان <strong>مهمان</strong> در حال خرید هستید. سیستم به صورت خودکار یک حساب کاربری برای خریدهای بعدی شما ایجاد خواهد کرد.</p>}
                            </header>

                            <form id="checkoutForm" onSubmit={handleCheckout}>
                                <div className="row gy-4 mb-5">
                                    <div className="col-12">
                                        <h2 className="h5 fw-900 text-dark mb-3"><i className="bi bi-truck text-primary fs-4 me-2" aria-hidden="true"></i> روش ارسال را انتخاب کنید</h2>
                                        {shippingMethods.length === 0 ? (
                                            <div className="alert alert-warning font-13 fw-bold rounded-4 py-3" role="alert">
                                                <i className="bi bi-exclamation-triangle-fill me-2" aria-hidden="true"></i> هیچ روش ارسالی فعال نیست.
                                            </div>
                                        ) : (
                                            <div className="row gy-3" role="radiogroup" aria-label="انتخاب روش ارسال">
                                                {shippingMethods.map(method => {
                                                    const isMethodPickup = method.name.includes('حضوری');
                                                    return (
                                                        <div className="col-md-6" key={method.id}>
                                                            <label htmlFor={`shipping_method_${method.id}`} className={`w-100 border rounded-4 p-3 cursor-pointer transition d-flex align-items-center justify-content-between ${formData.shipping_method_id === method.id ? 'border-danger bg-danger bg-opacity-10 shadow-sm' : 'border-ui bg-white hover-shadow'}`}>
                                                                <div className="d-flex align-items-center gap-3">
                                                                    <input type="radio" id={`shipping_method_${method.id}`} name="shipping_method_id" value={method.id} checked={formData.shipping_method_id === method.id} onChange={handleChange} className="form-check-input mt-0 shadow-none cursor-pointer" style={{width:'22px', height:'22px'}} aria-label={`روش ارسال ${method.name}`} />
                                                                    <div>
                                                                        <span className="d-block fw-bold font-14 text-dark mb-1">{method.name}</span>
                                                                        {method.description && <span className="font-12 text-muted">{method.description}</span>}
                                                                    </div>
                                                                </div>
                                                                <span className={`badge ${isMethodPickup ? 'bg-success text-white' : (method.is_pay_on_delivery ? 'bg-warning text-dark' : 'bg-primary')} font-12 py-2 px-3 rounded-pill`}>
                                                                    {isMethodPickup ? 'رایگان' : (method.is_pay_on_delivery ? 'پس کرایه' : 'پرداخت آنلاین')}
                                                                </span>
                                                            </label>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        )}
                                    </div>
                                </div>

                                <div className="row gy-4">
                                    {!user && (
                                        <>
                                            <div className="col-md-6">
                                                <label htmlFor="guest_first_name" className="fw-bold font-13 text-dark mb-2">نام <span className="text-danger">*</span></label>
                                                <input id="guest_first_name" type="text" name="guest_first_name" value={formData.guest_first_name} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light focus-white" placeholder="نام خود را وارد کنید" required aria-required="true" />
                                            </div>
                                            <div className="col-md-6">
                                                <label htmlFor="guest_last_name" className="fw-bold font-13 text-dark mb-2">نام خانوادگی <span className="text-danger">*</span></label>
                                                <input id="guest_last_name" type="text" name="guest_last_name" value={formData.guest_last_name} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light focus-white" placeholder="نام خانوادگی خود را وارد کنید" required aria-required="true" />
                                            </div>
                                            
                                            {isEmailMode ? (
                                                <>
                                                    <div className="col-md-6">
                                                        <label htmlFor="guest_email" className="fw-bold font-13 text-dark mb-2">آدرس ایمیل حساب کاربری <span className="text-danger">*</span></label>
                                                        <input id="guest_email" type="email" name="guest_email" value={formData.guest_email} onChange={handleChange} className="form-control border-ui py-3 font-14 rounded-3 text-start shadow-sm bg-light focus-white" placeholder="email@domain.com" dir="ltr" required aria-required="true" />
                                                    </div>
                                                    <div className="col-md-6">
                                                        <label htmlFor="guest_password" className="fw-bold font-13 text-dark mb-2">تعیین رمز عبور برای حساب جدید <span className="text-danger">*</span></label>
                                                        <div className="position-relative">
                                                            <input id="guest_password" type={showPassword ? "text" : "password"} name="guest_password" value={formData.guest_password} onChange={handleChange} className="form-control border-ui py-3 font-14 rounded-3 text-start shadow-sm bg-light focus-white pe-5" placeholder="حداقل ۸ کاراکتر" dir="ltr" required aria-required="true" />
                                                            <button type="button" aria-label={showPassword ? "مخفی کردن رمز عبور" : "نمایش رمز عبور"} className="btn border-0 position-absolute top-50 end-0 translate-middle-y text-muted px-3" onClick={() => setShowPassword(!showPassword)} style={{ zIndex: 10 }}>
                                                                <i className={`bi bi-eye${showPassword ? '-slash' : ''}`} aria-hidden="true"></i>
                                                            </button>
                                                        </div>
                                                    </div>
                                                </>
                                            ) : (
                                                <div className="col-12">
                                                    <label htmlFor="guest_phone" className="fw-bold font-13 text-dark mb-2">شماره تلفن همراه <span className="text-danger">*</span></label>
                                                    <input id="guest_phone" type="text" name="guest_phone" value={formData.guest_phone} onChange={handleChange} className="form-control border-ui py-3 font-14 rounded-3 text-start shadow-sm bg-light focus-white" placeholder="09123456789" dir="ltr" required aria-required="true" />
                                                </div>
                                            )}
                                            <div className="col-12"><hr className="border-light m-0"/></div>
                                        </>
                                    )}

                                    {isPickup ? (
                                        <div className="col-12">
                                            <div className="alert bg-success bg-opacity-10 border border-success border-opacity-25 rounded-4 p-4 text-center mt-2" role="alert">
                                                <i className="bi bi-shop fs-1 text-success d-block mb-3" aria-hidden="true"></i>
                                                <h2 className="h5 fw-bold text-dark mb-2">دریافت حضوری از فروشگاه (ارسال رایگان)</h2>
                                                <p className="text-muted font-14 m-0 lh-lg">شما روش دریافت حضوری را انتخاب کرده‌اید. نیازی به وارد کردن آدرس نیست. برای دریافت سفارش خود، پس از ثبت نهایی و پرداخت، با در دست داشتن کارت شناسایی به آدرس زیر مراجعه نمایید:</p>
                                                <p className="font-15 fw-900 text-dark mt-4 border-top border-success border-opacity-25 pt-4 d-inline-block mx-auto"><i className="bi bi-geo-alt-fill text-danger me-2" aria-hidden="true"></i>{settings?.seller_address || 'آدرس فروشگاه در تنظیمات سایت ثبت نشده است.'}</p>
                                            </div>
                                        </div>
                                    ) : (
                                        <>
                                            {user && userAddresses.length > 0 && (
                                                <div className="col-12 mb-2">
                                                    <h2 className="h5 fw-bold mb-3 text-dark">انتخاب آدرس از دفترچه</h2>
                                                    <div className="row gy-3" role="radiogroup" aria-label="انتخاب آدرس">
                                                        {userAddresses.map(addr => (
                                                            <div className="col-md-6" key={addr.uuid || addr.id}>
                                                                <label htmlFor={`address_${addr.uuid || addr.id}`} className={`w-100 border rounded-4 p-3 cursor-pointer transition h-100 ${selectedAddressId === (addr.uuid || addr.id) ? 'border-danger bg-danger bg-opacity-10 shadow-sm' : 'border-ui bg-light hover-shadow'}`}>
                                                                    <input type="radio" id={`address_${addr.uuid || addr.id}`} className="d-none" checked={selectedAddressId === (addr.uuid || addr.id)} onChange={() => setSelectedAddressId(addr.uuid || addr.id)} aria-label={`آدرس ${addr.title}`} />
                                                                    <div className="d-flex align-items-center justify-content-between mb-2">
                                                                        <span className="fw-bold text-dark font-14"><i className="bi bi-geo-alt text-danger me-1" aria-hidden="true"></i> {addr.title}</span>
                                                                        {addr.is_default && <span className="badge bg-success font-10 rounded-pill">پیش‌فرض</span>}
                                                                    </div>
                                                                    <p className="font-12 text-muted mb-2 text-truncate">{addr.province}، {addr.city}، {addr.postal_address}</p>
                                                                    <span className="font-12 text-dark fw-bold d-block"><i className="bi bi-person text-muted me-1" aria-hidden="true"></i> {addr.recipient_first_name} {addr.recipient_last_name}</span>
                                                                </label>
                                                            </div>
                                                        ))}
                                                        <div className="col-md-6">
                                                            <label htmlFor="address_new" className={`w-100 border rounded-4 p-3 cursor-pointer transition d-flex align-items-center justify-content-center h-100 ${selectedAddressId === 'new' ? 'border-danger bg-danger bg-opacity-10 shadow-sm' : 'border-ui bg-light hover-shadow'}`} onClick={() => setSelectedAddressId('new')}>
                                                                <input type="radio" id="address_new" className="d-none" checked={selectedAddressId === 'new'} onChange={() => setSelectedAddressId('new')} aria-label="ثبت آدرس جدید" />
                                                                <span className="fw-bold font-14 text-dark"><i className="bi bi-plus-circle-fill text-danger me-2 fs-5 align-middle" aria-hidden="true"></i> ثبت آدرس جدید</span>
                                                            </label>
                                                        </div>
                                                    </div>
                                                </div>
                                            )}

                                            {(!user || selectedAddressId === 'new') && (
                                                <>
                                                    <div className="col-md-6">
                                                        <label htmlFor="province" className="fw-bold font-13 text-dark mb-2">استان <span className="text-danger">*</span></label>
                                                        <input id="province" type="text" name="province" value={formData.province} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light focus-white" placeholder="مثال: تهران" required aria-required="true" />
                                                    </div>
                                                    <div className="col-md-6">
                                                        <label htmlFor="city" className="fw-bold font-13 text-dark mb-2">شهر <span className="text-danger">*</span></label>
                                                        <input id="city" type="text" name="city" value={formData.city} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light focus-white" placeholder="مثال: دزفول" required aria-required="true" />
                                                    </div>
                                                    <div className="col-12">
                                                        <label htmlFor="postal_address" className="fw-bold font-13 text-dark mb-2">آدرس دقیق پستی تحویل‌گیرنده <span className="text-danger">*</span></label>
                                                        <textarea id="postal_address" name="postal_address" value={formData.postal_address} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-4 shadow-sm bg-light focus-white lh-lg" rows="3" placeholder="نام خیابان، کوچه، فرعی، پلاک..." required aria-required="true"></textarea>
                                                    </div>
                                                    <div className="col-md-4">
                                                        <label htmlFor="postal_code" className="fw-bold font-13 text-dark mb-2">کد پستی (۱۰ رقمی) <span className="text-danger">*</span></label>
                                                        <input id="postal_code" type="text" name="postal_code" value={formData.postal_code} onChange={handleChange} className="form-control border-ui py-3 font-14 rounded-3 text-start shadow-sm bg-light focus-white" placeholder="1234567890" dir="ltr" required aria-required="true" />
                                                    </div>
                                                    <div className="col-md-4">
                                                        <label htmlFor="plaque" className="fw-bold font-13 text-dark mb-2">پلاک <span className="text-danger">*</span></label>
                                                        <input id="plaque" type="text" name="plaque" value={formData.plaque} onChange={handleChange} className="form-control border-ui py-3 font-14 rounded-3 shadow-sm bg-light focus-white text-start" placeholder="مثال: ۴" required aria-required="true" />
                                                    </div>
                                                    <div className="col-md-4">
                                                        <label htmlFor="building_unit" className="fw-bold font-13 text-dark mb-2">واحد</label>
                                                        <input id="building_unit" type="text" name="building_unit" value={formData.building_unit} onChange={handleChange} className="form-control border-ui py-3 font-14 rounded-3 shadow-sm bg-light focus-white text-start" placeholder="اختیاری" />
                                                    </div>
                                                </>
                                            )}
                                        </>
                                    )}
                                </div>
                            </form>
                        </div>
                    </section>

                    <aside className="col-lg-4" aria-label="صورتحساب و کد تخفیف">
                        <div className="position-sticky" style={{top: '100px'}}>
                            
                            <section className="bg-white p-4 rounded-4 shadow-sm border border-ui mb-4" aria-labelledby="coupon-heading">
                                <h2 id="coupon-heading" className="h6 fw-bold text-dark mb-3 d-flex align-items-center gap-2"><i className="bi bi-ticket-perforated text-danger fs-4" aria-hidden="true"></i> کد تخفیف دارید؟</h2>
                                <div className="input-group mb-2 shadow-sm rounded-3">
                                    <input 
                                        type="text" 
                                        className="form-control font-13 py-3 border-ui shadow-none rounded-start-3 bg-light focus-white text-center" 
                                        placeholder="مثال: DISCOUNT2026" 
                                        value={couponInput}
                                        onChange={(e) => setCouponInput(e.target.value)}
                                        disabled={couponData !== null}
                                        dir="ltr"
                                        aria-label="وارد کردن کد تخفیف"
                                    />
                                    <div className="input-group-append">
                                        {couponData ? (
                                            <button type="button" aria-label="حذف کد تخفیف اعمال شده" className="btn btn-danger text-white fw-bold px-4 rounded-end-3 h-100" onClick={() => {setCouponData(null); setFormData(p=>({...p, coupon_code:''})); setCouponInput('');}}>حذف</button>
                                        ) : (
                                            <button type="button" aria-label="اعمال کد تخفیف" className="btn btn-dark text-white fw-bold px-4 rounded-end-3 h-100" onClick={handleApplyCoupon} disabled={isApplyingCoupon}>
                                                {isApplyingCoupon ? <div className="spinner-border spinner-border-sm" aria-hidden="true"></div> : 'اعمال'}
                                            </button>
                                        )}
                                    </div>
                                </div>
                                {couponData && (
                                    <div className="mt-3 p-2 bg-success bg-opacity-10 border border-success border-opacity-25 rounded-3 text-center" role="status">
                                        <span className="font-12 fw-bold text-success"><i className="bi bi-check-circle-fill me-1" aria-hidden="true"></i> تخفیف روی فاکتور اعمال شد.</span>
                                    </div>
                                )}
                            </section>

                            <section className="bg-white p-4 p-md-5 rounded-4 shadow-sm border border-ui" aria-labelledby="invoice-heading">
                                <h2 id="invoice-heading" className="h5 fw-900 text-dark border-bottom border-light pb-3 mb-4 d-flex align-items-center gap-2"><i className="bi bi-receipt text-danger fs-4" aria-hidden="true"></i> صورتحساب نهایی</h2>
                                
                                <div className="d-flex flex-column gap-3 mb-4 overflow-auto custom-scrollbar pe-2" style={{maxHeight: '220px'}} aria-label="محصولات سبد خرید">
                                    {cartItems.map(item => {
                                        const product = item.product_details || {};
                                        const mainImageObj = product?.gallery?.find(img => img.is_main) || product?.gallery?.[0];
                                        const rawUrl = mainImageObj?.url || product?.image_url || product?.image;
                                        return (
                                            <article key={item.id} className="d-flex align-items-center gap-3 border-bottom border-light pb-3">
                                                <div className="bg-light rounded-3 p-1 border border-ui">
                                                    <img src={resolveImageUrl(rawUrl)} alt={`تصویر محصول ${product.title}`} style={{width:'45px', height:'45px', objectFit:'contain'}} onError={(e) => { e.target.src = '/assets/image/product/product-no-bg.png'; }} />
                                                </div>
                                                <div className="flex-grow-1">
                                                    <h3 className="h6 font-13 fw-bold text-dark text-overflow-1 m-0 mb-1">{product.title}</h3>
                                                    <div className="d-flex align-items-center justify-content-between">
                                                        <span className="font-12 text-muted px-2 py-1 bg-light rounded-pill border" aria-label={`تعداد: ${item.quantity} عدد`}>{item.quantity} عدد</span>
                                                        <span className="font-13 fw-bold text-dark">{Number(item.total_price).toLocaleString()} تومان</span>
                                                    </div>
                                                </div>
                                            </article>
                                        );
                                    })}
                                </div>

                                <ul className="list-unstyled p-0 m-0 border-top border-light pt-4">
                                    <li className="d-flex justify-content-between align-items-center mb-3">
                                        <span className="font-13 text-muted">مبلغ کل کالاها ({cartItems.reduce((acc, i) => acc + i.quantity, 0)} کالا)</span>
                                        <span className="font-15 text-dark fw-bold">{totalItemsAmount.toLocaleString()} <span className="font-11 text-muted fw-normal">تومان</span></span>
                                    </li>
                                    
                                    {discountAmount > 0 && (
                                        <li className="d-flex justify-content-between align-items-center mb-3">
                                            <span className="font-13 text-muted">سود شما از این خرید</span>
                                            <span className="font-15 text-danger fw-bold">{(discountAmount).toLocaleString()} تومان</span>
                                        </li>
                                    )}

                                    <li className="d-flex mb-4 pb-4 border-bottom border-dashed align-items-center justify-content-between">
                                        <span className="font-14 text-muted">هزینه ارسال</span>
                                        {isPickup ? (
                                            <span className="font-13 text-success fw-bold">رایگان</span>
                                        ) : shippingCost === 0 ? (
                                            <span className="font-13 text-success fw-bold">پس‌کرایه (پرداخت به پیک)</span>
                                        ) : (
                                            <span className="font-15 text-dark fw-bold">{shippingCost.toLocaleString()} <span className="font-11 text-muted fw-normal">تومان</span></span>
                                        )}
                                    </li>

                                    <li className="d-flex justify-content-between align-items-center mb-4 pb-4 border-bottom border-dashed">
                                        <span className="font-13 text-muted d-flex align-items-center gap-1" title="محاسبه شده بر اساس 10 درصد مالیات"><i className="bi bi-info-circle" aria-hidden="true"></i> مالیات (۱۰٪)</span>
                                        <span className="font-14 text-dark fw-bold">{taxAmount.toLocaleString()} <span className="font-11 text-muted fw-normal">تومان</span></span>
                                    </li>

                                    <li className="d-flex flex-column align-items-center mb-4 bg-light p-3 rounded-4 border border-light shadow-sm">
                                        <span className="font-14 text-dark fw-bold mb-2">مبلغ قابل پرداخت</span>
                                        <span className="font-26 text-danger fw-900">{payableAmount.toLocaleString()} <span className="font-14 fw-normal text-muted">تومان</span></span>
                                    </li>
                                </ul>

                                <button type="submit" form="checkoutForm" disabled={isSubmitting} aria-label="ثبت نهایی و اتصال به درگاه پرداخت" className="btn main-color-two-bg w-100 text-white rounded-pill py-3 fw-bold shadow hover-lift fs-5 d-flex align-items-center justify-content-center gap-2">
                                    {isSubmitting ? <div className="spinner-border spinner-border-sm text-white" aria-hidden="true"></div> : <i className="bi bi-credit-card-fill fs-4" aria-hidden="true"></i>}
                                    ثبت و اتصال به درگاه
                                </button>
                            </section>
                        </div>
                    </aside>
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
                .custom-scrollbar::-webkit-scrollbar { width: 5px; height: 5px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: #f8f9fa; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #dee2e6; border-radius: 10px; }
                .custom-toast { position: fixed; bottom: 30px; left: -400px; min-width: 300px; padding: 16px 24px; border-radius: 16px; z-index: 999999; transition: left 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
                .custom-toast.show { left: 30px; }
                @media (max-width: 768px) {
                    .custom-toast { left: 50% !important; transform: translateX(-50%); bottom: -100px; width: 90%; min-width: unset; transition: bottom 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
                    .custom-toast.show { bottom: 20px !important; left: 50% !important; }
                }
            `}</style>
        </main>
    );
};

export default CheckoutPage;