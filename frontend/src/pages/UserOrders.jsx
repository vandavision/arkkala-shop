import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getUserOrders } from '../api/cartApi';
import { requestPayment } from '../api/paymentApi';
import CountdownTimer from '../components/CountdownTimer';

const UserOrders = () => {
    const [orders, setOrders] = useState([]);
    const [activeTab, setActiveTab] = useState('all');
    const [loading, setLoading] = useState(true);
    const [payingOrderId, setPayingOrderId] = useState(null);

    const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
    const showToast = (message, type = 'danger') => {
        setToast({ show: true, message, type });
        setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 4000);
    };

    useEffect(() => {
        const fetchOrders = async () => {
            setLoading(true);
            try {
                const data = await getUserOrders();
                setOrders(data.results || data || []);
            } catch (error) {
                console.error("Error fetching user orders:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchOrders();
    }, []);

    const handlePayOrder = async (orderId) => {
        setPayingOrderId(orderId);
        try {
            const payment = await requestPayment(orderId, 'zarinpal');
            window.location.href = payment.payment_url;
        } catch (error) {
            showToast(error.response?.data?.error || "خطا در اتصال به درگاه پرداخت.");
            setPayingOrderId(null);
        }
    };

    const filteredOrders = orders.filter(order => {
        if (activeTab === 'all') return true;
        if (activeTab === 'processing' && ['pending', 'processing', 'shipped'].includes(order.status)) return true;
        if (activeTab === 'delivered' && order.status === 'delivered') return true;
        if (activeTab === 'cancelled' && order.status === 'cancelled') return true;
        return false;
    });

    const getStatusBadge = (status) => {
        switch(status) {
            case 'pending': return <span className="badge bg-warning bg-opacity-10 text-warning border border-warning border-opacity-50 px-3 py-2 rounded-pill font-13 fw-bold shadow-sm"><i className="bi bi-clock-history me-1"></i>در انتظار پرداخت</span>;
            case 'processing': return <span className="badge bg-info bg-opacity-10 text-info border border-info border-opacity-50 px-3 py-2 rounded-pill font-13 fw-bold shadow-sm"><i className="bi bi-gear-fill me-1"></i>در حال پردازش</span>;
            case 'shipped': return <span className="badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-50 px-3 py-2 rounded-pill font-13 fw-bold shadow-sm"><i className="bi bi-truck me-1"></i>ارسال شده</span>;
            case 'delivered': return <span className="badge bg-success bg-opacity-10 text-success border border-success border-opacity-50 px-3 py-2 rounded-pill font-13 fw-bold shadow-sm"><i className="bi bi-check-circle-fill me-1"></i>تحویل شده</span>;
            case 'cancelled': return <span className="badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-50 px-3 py-2 rounded-pill font-13 fw-bold shadow-sm"><i className="bi bi-x-circle-fill me-1"></i>لغو شده</span>;
            default: return <span className="badge bg-secondary text-white px-3 py-2 rounded-pill font-13 fw-bold shadow-sm">{status}</span>;
        }
    };

    return (
        <div className="user-orders position-relative">
            <div className={`custom-toast ${toast.show ? 'show' : ''} bg-${toast.type} shadow-lg d-flex align-items-center gap-3`}>
                <i className={`bi ${toast.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill'} fs-3 text-white`}></i>
                <span className="font-14 fw-bold text-white lh-base">{toast.message}</span>
            </div>

            <div className="bg-white p-3 p-md-4 rounded-4 border border-ui shadow-sm mb-4 d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-3">
                <div className="d-flex align-items-center gap-3">
                    <div className="bg-danger bg-opacity-10 p-3 rounded-circle d-flex align-items-center justify-content-center">
                        <i className="bi bi-box-seam-fill text-danger fs-3"></i>
                    </div>
                    <div>
                        <h2 className="fw-900 h5 m-0 text-dark mb-1">تاریخچه <span className="text-danger">سفارشات</span></h2>
                        <span className="text-muted font-12">پیگیری سریع خریدهای شما</span>
                    </div>
                </div>
            </div>

            <div className="bg-transparent mb-4 min-vh-50">
                <ul className="nav nav-pills gap-2 pb-3 mb-4 custom-scrollbar overflow-auto flex-nowrap border-bottom border-light">
                    <li className="nav-item flex-shrink-0">
                        <button className={`nav-link rounded-pill font-13 fw-bold px-4 py-2 transition ${activeTab === 'all' ? 'active bg-danger text-white shadow-sm' : 'text-muted bg-white border border-ui hover-bg-danger-light'}`} onClick={() => setActiveTab('all')}>همه سفارش‌ها</button>
                    </li>
                    <li className="nav-item flex-shrink-0">
                        <button className={`nav-link rounded-pill font-13 fw-bold px-4 py-2 transition ${activeTab === 'processing' ? 'active bg-info text-dark shadow-sm border-info' : 'text-muted bg-white border border-ui hover-bg-danger-light'}`} onClick={() => setActiveTab('processing')}>جاری / پردازش</button>
                    </li>
                    <li className="nav-item flex-shrink-0">
                        <button className={`nav-link rounded-pill font-13 fw-bold px-4 py-2 transition ${activeTab === 'delivered' ? 'active bg-success text-white shadow-sm' : 'text-muted bg-white border border-ui hover-bg-danger-light'}`} onClick={() => setActiveTab('delivered')}>تحویل شده</button>
                    </li>
                    <li className="nav-item flex-shrink-0">
                        <button className={`nav-link rounded-pill font-13 fw-bold px-4 py-2 transition ${activeTab === 'cancelled' ? 'active bg-danger text-white shadow-sm' : 'text-muted bg-white border border-ui hover-bg-danger-light'}`} onClick={() => setActiveTab('cancelled')}>لغو یا مرجوع شده</button>
                    </li>
                </ul>

                {loading ? (
                    <div className="text-center py-5 bg-white rounded-4 shadow-sm border border-ui min-h-300 d-flex flex-column align-items-center justify-content-center">
                        <div className="spinner-border text-danger mb-3" style={{width: '3rem', height:'3rem', borderWidth: '0.25rem'}}></div>
                        <p className="text-dark font-14 fw-bold m-0">در حال بارگذاری لیست سفارشات...</p>
                    </div>
                ) : filteredOrders.length === 0 ? (
                    <div className="text-center py-5 my-3 bg-white rounded-4 shadow-sm border border-ui min-h-300 d-flex flex-column align-items-center justify-content-center">
                        <i className="bi bi-cart-x text-muted opacity-25 d-block mb-3" style={{ fontSize: '5rem' }}></i>
                        <h5 className="fw-bold text-dark mb-2 font-16">سفارشی در این بخش وجود ندارد!</h5>
                        <p className="text-muted font-13 mb-4">می‌توانید برای ثبت اولین سفارش خود به فروشگاه مراجعه کنید.</p>
                        <Link to="/shop" className="btn btn-danger rounded-pill px-5 py-3 font-14 fw-bold shadow-sm hover-lift">شروع خرید</Link>
                    </div>
                ) : (
                    <div className="orders-list d-flex flex-column gap-4">
                        {filteredOrders.map((order) => {
                            const expiryTime = new Date(new Date(order.created_at).getTime() + 2 * 60 * 60 * 1000);
                            const isExpired = new Date() > expiryTime;
                            
                            return (
                            <div className="order-card border border-ui rounded-4 bg-white shadow-sm hover-shadow transition overflow-hidden" key={order.id}>
                                <div className="d-flex flex-column flex-lg-row justify-content-between align-items-lg-center bg-light p-3 p-md-4 border-bottom border-light gap-3">
                                    
                                    <div className="d-flex align-items-center gap-3 gap-md-4 flex-wrap">
                                        <div className="d-flex align-items-center gap-2">
                                            <div className="bg-white rounded-circle shadow-sm border border-ui d-flex align-items-center justify-content-center" style={{width: '40px', height: '40px'}}><i className="bi bi-hash text-muted fs-5"></i></div>
                                            <div>
                                                <span className="d-block font-11 text-muted mb-1">کد پیگیری</span>
                                                <span className="font-14 fw-bold text-dark" dir="ltr">{order.id.slice(0, 8).toUpperCase()}</span>
                                            </div>
                                        </div>
                                        <div className="d-none d-md-block vr bg-secondary opacity-25" style={{width:'2px', height:'30px'}}></div>
                                        <div className="d-flex align-items-center gap-2">
                                            <div className="bg-white rounded-circle shadow-sm border border-ui d-flex align-items-center justify-content-center" style={{width: '40px', height: '40px'}}><i className="bi bi-calendar2-week text-muted fs-5"></i></div>
                                            <div>
                                                <span className="d-block font-11 text-muted mb-1">تاریخ ثبت</span>
                                                <span className="font-13 fw-bold text-dark">{new Date(order.created_at).toLocaleDateString('fa-IR')}</span>
                                            </div>
                                        </div>
                                        <div className="d-none d-md-block vr bg-secondary opacity-25" style={{width:'2px', height:'30px'}}></div>
                                        <div className="d-flex align-items-center gap-2">
                                            <div className="bg-white rounded-circle shadow-sm border border-ui d-flex align-items-center justify-content-center" style={{width: '40px', height: '40px'}}><i className="bi bi-wallet2 text-muted fs-5"></i></div>
                                            <div>
                                                <span className="d-block font-11 text-muted mb-1">مبلغ کل</span>
                                                <span className="font-15 fw-900 text-dark">{Number(order.payable_amount).toLocaleString()} <span className="font-10 text-muted fw-normal">تومان</span></span>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="d-flex align-items-center justify-content-between justify-content-lg-end w-100 w-lg-auto">
                                        {getStatusBadge(order.status)}
                                    </div>
                                </div>
                                
                                <div className="p-3 p-md-4">
                                    {order.status === 'pending' && (
                                        <div className="alert bg-warning bg-opacity-10 border border-warning border-opacity-25 rounded-4 p-3 d-flex flex-column flex-md-row align-items-center justify-content-between mb-4 shadow-sm">
                                            <div className="d-flex align-items-center mb-3 mb-md-0">
                                                <i className="bi bi-info-circle-fill text-warning fs-3 me-3"></i>
                                                <div>
                                                    <span className="font-14 text-dark fw-bold d-block mb-1">پرداخت این سفارش هنوز انجام نشده است.</span>
                                                    <span className="font-12 text-muted">در صورت عدم پرداخت در مهلت مقرر، سفارش لغو می‌شود.</span>
                                                </div>
                                            </div>
                                            
                                            {!isExpired ? (
                                                <div className="d-flex align-items-center gap-3 w-100 w-md-auto flex-column flex-md-row">
                                                    <div className="bg-white px-3 py-2 rounded-pill shadow-sm border border-warning">
                                                        <CountdownTimer endTime={expiryTime.toISOString()} variant="warning" />
                                                    </div>
                                                    <button onClick={() => handlePayOrder(order.id)} disabled={payingOrderId === order.id} className="btn btn-warning fw-bold px-4 py-2 rounded-pill shadow-sm hover-lift w-100 w-md-auto d-flex align-items-center justify-content-center gap-2">
                                                        {payingOrderId === order.id ? <div className="spinner-border spinner-border-sm"></div> : <i className="bi bi-credit-card-fill"></i>}
                                                        پرداخت آنلاین
                                                    </button>
                                                </div>
                                            ) : (
                                                <span className="badge bg-secondary px-3 py-2 rounded-pill font-13 shadow-sm">مهلت منقضی شده</span>
                                            )}
                                        </div>
                                    )}

                                    <div className="d-flex flex-column flex-md-row align-items-md-center justify-content-between">
                                        <div className="d-flex align-items-center gap-2 overflow-auto custom-scrollbar pb-2">
                                            {order.items && order.items.map((item) => (
                                                <div key={item.id} className="bg-white border border-ui rounded-4 p-2 shadow-sm flex-shrink-0 hover-lift transition" style={{width:'75px', height:'75px'}} title={item.product_title}>
                                                    <img src={item.product_image || '/assets/image/product/product-no-bg.png'} alt={item.product_title} className="img-fluid w-100 h-100 object-fit-contain" />
                                                </div>
                                            ))}
                                        </div>
                                        <Link to={`/dashboard/orders/${order.id}`} className="btn btn-outline-danger rounded-pill px-4 py-2 font-13 fw-bold text-nowrap flex-shrink-0 mt-3 mt-md-0 ms-md-3 hover-lift d-flex align-items-center justify-content-center gap-2">
                                            مشاهده فاکتور کامل <i className="bi bi-chevron-left align-middle"></i>
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        )})}
                    </div>
                )}
            </div>

            <style jsx="true">{`
                .hover-lift { transition: transform 0.2s ease, box-shadow 0.2s; }
                .hover-lift:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important; }
                .hover-shadow:hover { box-shadow: 0 15px 30px rgba(0,0,0,0.06) !important; border-color: #dee2e6 !important;}
                .transition { transition: all 0.3s ease; }
                .hover-bg-danger-light:hover { background-color: #ffe6e9 !important; color: #ef4056 !important;}
                .min-h-300 { min-height: 300px; }
                .custom-scrollbar::-webkit-scrollbar { height: 6px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #dee2e6; border-radius: 10px; }
                
                .custom-toast { position: fixed; bottom: 30px; left: -400px; min-width: 300px; padding: 16px 24px; border-radius: 16px; z-index: 999999; transition: left 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
                .custom-toast.show { left: 30px; }
                @media (max-width: 768px) {
                    .custom-toast { left: 50% !important; transform: translateX(-50%); bottom: -100px; width: 90%; min-width: unset; transition: bottom 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
                    .custom-toast.show { bottom: 20px !important; left: 50% !important; }
                }
            `}</style>
        </div>
    );
};

export default UserOrders;