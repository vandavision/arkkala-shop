import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getUserOrders, submitOrderRequest, getOrderRequests } from '../api/cartApi';
import { requestPayment } from '../api/paymentApi';
import CountdownTimer from '../components/CountdownTimer';

const RETURN_DEADLINE_DAYS = 7;

const UserOrders = () => {
    const [orders, setOrders] = useState([]);
    const [orderRequests, setOrderRequests] = useState([]);
    const [activeTab, setActiveTab] = useState('all');
    const [loading, setLoading] = useState(true);
    const [payingOrderId, setPayingOrderId] = useState(null);

    const [requestModalOpen, setRequestModalOpen] = useState(false);
    const [selectedOrderId, setSelectedOrderId] = useState(null);
    const [requestType, setRequestType] = useState('return');
    const [requestReason, setRequestReason] = useState('');
    const [isSubmittingRequest, setIsSubmittingRequest] = useState(false);

    const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
    const showToast = (message, type = 'danger') => {
        setToast({ show: true, message, type });
        setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 4000);
    };

    const fetchOrdersData = async () => {
        setLoading(true);
        try {
            const [ordersData, requestsData] = await Promise.all([
                getUserOrders(),
                getOrderRequests()
            ]);
            setOrders(ordersData.results || ordersData || []);
            setOrderRequests(requestsData.results || requestsData || []);
        } catch (error) {
            console.error("Error fetching user orders data:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchOrdersData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

    const openRequestModal = (orderId, type) => {
        setSelectedOrderId(orderId);
        setRequestType(type);
        setRequestReason('');
        setRequestModalOpen(true);
    };

    const handleRequestSubmit = async (e) => {
        e.preventDefault();
        if (!requestReason.trim()) {
            return showToast("لطفاً علت درخواست خود را مشخص کنید.", "warning");
        }
        setIsSubmittingRequest(true);
        try {
            await submitOrderRequest(selectedOrderId, requestReason, requestType);
            showToast("درخواست شما با موفقیت ثبت شد و در اسرع وقت بررسی می‌شود.", "success");
            setRequestModalOpen(false);
            fetchOrdersData(); 
        } catch (error) {
            showToast(error.response?.data?.error || "خطا در ثبت درخواست.", "danger");
        } finally {
            setIsSubmittingRequest(false);
        }
    };

    const filteredOrders = orders.filter(order => {
        if (activeTab === 'all') return true;
        if (activeTab === 'processing' && ['pending', 'paid', 'processing', 'shipped'].includes(order.status)) return true;
        if (activeTab === 'delivered' && order.status === 'delivered') return true;
        if (activeTab === 'cancelled' && order.status === 'cancelled') return true;
        if (activeTab === 'returned' && order.status === 'returned') return true;
        return false;
    });

    const getStatusBadge = (status) => {
        switch(status) {
            case 'pending': return <span className="badge bg-warning bg-opacity-10 text-warning border border-warning border-opacity-50 px-3 py-2 rounded-pill font-13 fw-bold shadow-sm"><i className="bi bi-clock-history me-1"></i>در انتظار پرداخت</span>;
            case 'paid': return <span className="badge bg-success bg-opacity-10 text-success border border-success border-opacity-50 px-3 py-2 rounded-pill font-13 fw-bold shadow-sm"><i className="bi bi-credit-card-fill me-1"></i>پرداخت شده</span>;
            case 'processing': return <span className="badge bg-info bg-opacity-10 text-info border border-info border-opacity-50 px-3 py-2 rounded-pill font-13 fw-bold shadow-sm"><i className="bi bi-gear-fill me-1"></i>در حال پردازش</span>;
            case 'shipped': return <span className="badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-50 px-3 py-2 rounded-pill font-13 fw-bold shadow-sm"><i className="bi bi-truck me-1"></i>ارسال شده</span>;
            case 'delivered': return <span className="badge bg-success bg-opacity-10 text-success border border-success border-opacity-50 px-3 py-2 rounded-pill font-13 fw-bold shadow-sm"><i className="bi bi-check-circle-fill me-1"></i>تحویل شده</span>;
            case 'cancelled': return <span className="badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-50 px-3 py-2 rounded-pill font-13 fw-bold shadow-sm"><i className="bi bi-x-circle-fill me-1"></i>لغو شده</span>;
            case 'returned': return <span className="badge bg-secondary bg-opacity-10 text-secondary border border-secondary border-opacity-50 px-3 py-2 rounded-pill font-13 fw-bold shadow-sm"><i className="bi bi-arrow-return-left me-1"></i>مرجوع شده</span>;
            default: return <span className="badge bg-dark text-white px-3 py-2 rounded-pill font-13 fw-bold shadow-sm">{status}</span>;
        }
    };

    const getRequestStatusBadge = (request) => {
        let badgeClass = "bg-dark text-dark border-dark";
        if (request.status === 'pending') badgeClass = "bg-warning text-warning border-warning";
        if (request.status === 'approved') badgeClass = "bg-success text-success border-success";
        if (request.status === 'rejected') badgeClass = "bg-danger text-danger border-danger";

        return (
            <span className={`badge ${badgeClass} bg-opacity-10 border border-opacity-25 px-3 py-2 rounded-pill font-12 fw-bold shadow-sm`}>
                <i className={request.request_type === 'cancel' ? "bi bi-x-circle me-1" : "bi bi-arrow-return-left me-1"}></i> 
                درخواست {request.request_type_display}: {request.status_display}
            </span>
        );
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
                        <button className={`nav-link rounded-pill font-13 fw-bold px-4 py-2 transition ${activeTab === 'cancelled' ? 'active bg-danger text-white shadow-sm' : 'text-muted bg-white border border-ui hover-bg-danger-light'}`} onClick={() => setActiveTab('cancelled')}>لغو شده</button>
                    </li>
                    <li className="nav-item flex-shrink-0">
                        <button className={`nav-link rounded-pill font-13 fw-bold px-4 py-2 transition ${activeTab === 'returned' ? 'active bg-secondary text-white shadow-sm' : 'text-muted bg-white border border-ui hover-bg-danger-light'}`} onClick={() => setActiveTab('returned')}>مرجوعی</button>
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
                            const isPaymentExpired = new Date() > expiryTime;
                            
                            const deliveryDate = new Date(order.modified_at || order.created_at);
                            const daysSinceDelivery = (new Date() - deliveryDate) / (1000 * 60 * 60 * 24);
                            const isReturnWindowOpen = daysSinceDelivery <= RETURN_DEADLINE_DAYS;

                            const orderRequest = orderRequests.find(r => r.order === order.id);
                            
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
                                    <div className="d-flex align-items-center justify-content-between justify-content-lg-end w-100 w-lg-auto gap-2 flex-wrap">
                                        {getStatusBadge(order.status)}
                                        {orderRequest && getRequestStatusBadge(orderRequest)}
                                    </div>
                                </div>
                                
                                <div className="p-3 p-md-4">
                                    {orderRequest && orderRequest.admin_note && (
                                        <div className="alert bg-light border border-ui rounded-4 p-3 d-flex align-items-start gap-3 mb-4 shadow-sm">
                                            <div className="bg-secondary bg-opacity-10 rounded-circle p-2 d-flex align-items-center justify-content-center flex-shrink-0" style={{width: '40px', height: '40px'}}>
                                                <i className="bi bi-chat-dots-fill text-secondary fs-5"></i>
                                            </div>
                                            <div>
                                                <span className="font-13 text-dark fw-bold d-block mb-1">پاسخ پشتیبانی به درخواست شما:</span>
                                                <p className="font-13 text-muted m-0 lh-lg text-justify">{orderRequest.admin_note}</p>
                                            </div>
                                        </div>
                                    )}

                                    {order.status === 'pending' && (
                                        <div className="alert bg-warning bg-opacity-10 border border-warning border-opacity-25 rounded-4 p-3 d-flex flex-column flex-md-row align-items-center justify-content-between mb-4 shadow-sm">
                                            <div className="d-flex align-items-center mb-3 mb-md-0">
                                                <i className="bi bi-info-circle-fill text-warning fs-3 me-3"></i>
                                                <div>
                                                    <span className="font-14 text-dark fw-bold d-block mb-1">پرداخت این سفارش هنوز انجام نشده است.</span>
                                                    <span className="font-12 text-muted">در صورت عدم پرداخت در مهلت مقرر، سفارش لغو می‌شود.</span>
                                                </div>
                                            </div>
                                            
                                            {!isPaymentExpired ? (
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

                                    <div className="d-flex flex-column flex-md-row align-items-md-center justify-content-between mt-3">
                                        <div className="d-flex align-items-center gap-2 overflow-auto custom-scrollbar pb-2">
                                            {order.items && order.items.map((item) => (
                                                <div key={item.id} className="bg-white border border-ui rounded-4 p-2 shadow-sm flex-shrink-0 hover-lift transition" style={{width:'75px', height:'75px'}} title={item.product_title}>
                                                    <img src={item.product_image || '/assets/image/product/product-no-bg.png'} alt={item.product_title} className="img-fluid w-100 h-100 object-fit-contain" />
                                                </div>
                                            ))}
                                        </div>
                                        <div className="d-flex align-items-center justify-content-end gap-2 mt-3 mt-md-0 ms-md-3 flex-wrap">
                                            
                                            {['pending', 'paid', 'processing'].includes(order.status) && !orderRequest && (
                                                <button onClick={() => openRequestModal(order.id, 'cancel')} className="btn btn-outline-warning rounded-pill px-4 py-2 font-13 fw-bold text-nowrap flex-shrink-0 hover-lift d-flex align-items-center justify-content-center gap-2">
                                                    <i className="bi bi-x-circle align-middle"></i> درخواست لغو سفارش
                                                </button>
                                            )}

                                            {order.status === 'delivered' && !orderRequest && isReturnWindowOpen && (
                                                <button onClick={() => openRequestModal(order.id, 'return')} className="btn btn-outline-secondary rounded-pill px-4 py-2 font-13 fw-bold text-nowrap flex-shrink-0 hover-lift d-flex align-items-center justify-content-center gap-2">
                                                    <i className="bi bi-arrow-return-left align-middle"></i> درخواست مرجوعی
                                                </button>
                                            )}
                                            
                                            {order.status === 'delivered' && !orderRequest && !isReturnWindowOpen && (
                                                <span className="badge bg-light text-muted border border-ui px-3 py-2 font-11 rounded-pill">
                                                    مهلت ۷ روزه مرجوعی پایان یافته است
                                                </span>
                                            )}

                                            <Link to={`/dashboard/orders/${order.id}`} className="btn btn-outline-danger rounded-pill px-4 py-2 font-13 fw-bold text-nowrap flex-shrink-0 hover-lift d-flex align-items-center justify-content-center gap-2">
                                                مشاهده فاکتور کامل <i className="bi bi-chevron-left align-middle"></i>
                                            </Link>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )})}
                    </div>
                )}
            </div>

            {requestModalOpen && (
                <>
                    <div className="modal-backdrop fade show" style={{ zIndex: 1050 }} onClick={() => setRequestModalOpen(false)}></div>
                    <div className="modal fade show d-block" tabIndex="-1" style={{ zIndex: 1055 }}>
                        <div className="modal-dialog modal-dialog-centered">
                            <div className="modal-content border-0 rounded-4 shadow-lg overflow-hidden">
                                <div className="modal-header bg-light border-bottom border-ui px-4 py-3">
                                    <h5 className="modal-title fw-900 font-16 text-dark d-flex align-items-center gap-2">
                                        <i className={`bi ${requestType === 'cancel' ? 'bi-x-circle' : 'bi-arrow-return-left'} text-danger fs-4`}></i> 
                                        ثبت درخواست {requestType === 'cancel' ? 'لغو سفارش' : 'مرجوعی کالا'}
                                    </h5>
                                    <button type="button" className="btn-close shadow-none" onClick={() => setRequestModalOpen(false)}></button>
                                </div>
                                <div className="modal-body p-4">
                                    {requestType === 'return' && (
                                        <div className="alert bg-primary bg-opacity-10 border border-primary border-opacity-25 rounded-3 mb-4 font-13 text-dark">
                                            <i className="bi bi-info-circle-fill text-primary me-2"></i>
                                            طبق قوانین، شما تا <strong>۷ روز</strong> پس از تحویل کالا فرصت ثبت درخواست مرجوعی دارید.
                                        </div>
                                    )}
                                    <form onSubmit={handleRequestSubmit}>
                                        <div className="mb-4">
                                            <label className="form-label font-14 fw-bold text-dark mb-3">
                                                لطفاً دلیل {requestType === 'cancel' ? 'لغو' : 'مرجوعی'} را کامل شرح دهید <span className="text-danger">*</span>
                                            </label>
                                            <textarea 
                                                className="form-control border-ui py-3 px-4 font-13 rounded-4 shadow-sm bg-light focus-danger lh-lg text-justify" 
                                                rows="5" 
                                                placeholder={requestType === 'cancel' ? "چرا قصد لغو سفارش را دارید؟ در صورت پرداخت، مبلغ عودت داده می‌شود." : "نام محصول مورد نظر و دلیل عدم رضایت، مغایرت با سایت یا نقص فنی را اینجا بنویسید..."} 
                                                value={requestReason} 
                                                onChange={(e) => setRequestReason(e.target.value)} 
                                                required
                                            ></textarea>
                                        </div>
                                        <div className="d-flex align-items-center justify-content-end gap-2">
                                            <button type="button" className="btn btn-light px-4 py-2 rounded-pill fw-bold font-13" onClick={() => setRequestModalOpen(false)}>انصراف</button>
                                            <button type="submit" disabled={isSubmittingRequest} className="btn btn-danger px-5 py-2 rounded-pill fw-bold font-13 shadow-sm hover-lift d-flex align-items-center gap-2">
                                                {isSubmittingRequest ? <div className="spinner-border spinner-border-sm text-white"></div> : <i className="bi bi-send-check"></i>}
                                                ثبت درخواست
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            )}

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
                .focus-danger:focus { background-color: #fff !important; box-shadow: 0 0 0 4px rgba(239, 64, 86, 0.1) !important; border-color: #ef4056 !important; outline: none; }
                
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