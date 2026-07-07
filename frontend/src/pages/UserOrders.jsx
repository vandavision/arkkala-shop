import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getUserOrders } from '../api/cartApi';

const UserOrders = () => {
    const [orders, setOrders] = useState([]);
    const [activeTab, setActiveTab] = useState('all');
    const [loading, setLoading] = useState(true);

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

    const filteredOrders = orders.filter(order => {
        if (activeTab === 'all') return true;
        if (activeTab === 'processing' && ['pending', 'processing', 'shipped'].includes(order.status)) return true;
        if (activeTab === 'delivered' && order.status === 'delivered') return true;
        if (activeTab === 'cancelled' && order.status === 'cancelled') return true;
        return false;
    });

    const getStatusBadge = (status) => {
        switch(status) {
            case 'pending': return <span className="badge bg-warning text-dark px-3 py-2 rounded-pill font-12 fw-bold shadow-sm"><i className="bi bi-clock me-1"></i>در انتظار پرداخت</span>;
            case 'processing': return <span className="badge bg-info text-dark px-3 py-2 rounded-pill font-12 fw-bold shadow-sm"><i className="bi bi-gear me-1"></i>در حال پردازش</span>;
            case 'shipped': return <span className="badge bg-primary text-white px-3 py-2 rounded-pill font-12 fw-bold shadow-sm"><i className="bi bi-truck me-1"></i>ارسال شده</span>;
            case 'delivered': return <span className="badge bg-success text-white px-3 py-2 rounded-pill font-12 fw-bold shadow-sm"><i className="bi bi-check-circle me-1"></i>تحویل شده</span>;
            case 'cancelled': return <span className="badge bg-danger text-white px-3 py-2 rounded-pill font-12 fw-bold shadow-sm"><i className="bi bi-x-circle me-1"></i>لغو شده</span>;
            default: return <span className="badge bg-secondary text-white px-3 py-2 rounded-pill font-12 fw-bold shadow-sm">{status}</span>;
        }
    };

    return (
        <div className="user-orders">
            <div className="bg-white p-3 p-md-4 rounded-4 border border-ui shadow-sm mb-4 d-flex align-items-center gap-3">
                <div className="bg-danger bg-opacity-10 p-2 rounded-circle d-flex align-items-center justify-content-center">
                    <i className="bi bi-box-seam-fill text-danger fs-3"></i>
                </div>
                <h2 className="fw-900 h5 m-0 text-dark">تاریخچه <span className="text-danger">سفارشات</span></h2>
            </div>

            <div className="bg-white rounded-4 shadow-sm border border-ui p-4 mb-4 min-vh-50">
                <ul className="nav nav-pills gap-2 border-bottom border-light pb-3 mb-4 custom-scrollbar overflow-auto flex-nowrap">
                    <li className="nav-item flex-shrink-0">
                        <button className={`nav-link rounded-pill font-13 fw-bold px-4 transition ${activeTab === 'all' ? 'active bg-danger text-white shadow-sm' : 'text-muted bg-light border border-ui hover-bg-danger-light'}`} onClick={() => setActiveTab('all')}>همه سفارش‌ها</button>
                    </li>
                    <li className="nav-item flex-shrink-0">
                        <button className={`nav-link rounded-pill font-13 fw-bold px-4 transition ${activeTab === 'processing' ? 'active bg-info text-dark shadow-sm border-info' : 'text-muted bg-light border border-ui hover-bg-danger-light'}`} onClick={() => setActiveTab('processing')}>جاری / پردازش</button>
                    </li>
                    <li className="nav-item flex-shrink-0">
                        <button className={`nav-link rounded-pill font-13 fw-bold px-4 transition ${activeTab === 'delivered' ? 'active bg-success text-white shadow-sm' : 'text-muted bg-light border border-ui hover-bg-danger-light'}`} onClick={() => setActiveTab('delivered')}>تحویل شده</button>
                    </li>
                    <li className="nav-item flex-shrink-0">
                        <button className={`nav-link rounded-pill font-13 fw-bold px-4 transition ${activeTab === 'cancelled' ? 'active bg-danger text-white shadow-sm' : 'text-muted bg-light border border-ui hover-bg-danger-light'}`} onClick={() => setActiveTab('cancelled')}>لغو یا مرجوع شده</button>
                    </li>
                </ul>

                {loading ? (
                    <div className="text-center py-5">
                        <div className="spinner-border text-danger mb-3" style={{width: '3rem', height:'3rem'}}></div>
                        <p className="text-muted font-14 fw-bold">در حال بارگذاری لیست سفارشات...</p>
                    </div>
                ) : filteredOrders.length === 0 ? (
                    <div className="text-center py-5 my-3">
                        <i className="bi bi-cart-x text-muted opacity-25 d-block mb-3" style={{ fontSize: '5rem' }}></i>
                        <h5 className="fw-bold text-dark mb-2 font-16">سفارشی در این بخش وجود ندارد!</h5>
                        <p className="text-muted font-13 mb-4">می‌توانید برای ثبت اولین سفارش خود به فروشگاه مراجعه کنید.</p>
                        <Link to="/shop" className="btn btn-danger rounded-pill px-5 py-2 font-14 fw-bold shadow-sm hover-lift">شروع خرید</Link>
                    </div>
                ) : (
                    <div className="orders-list d-flex flex-column gap-3">
                        {filteredOrders.map((order) => (
                            <div className="order-card border border-ui rounded-4 p-3 p-md-4 bg-light shadow-sm hover-shadow transition" key={order.id}>
                                <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center border-bottom border-light pb-3 mb-3 gap-3">
                                    <div className="d-flex align-items-center gap-2 gap-md-4 flex-wrap">
                                        <div className="d-flex align-items-center gap-2">
                                            <i className="bi bi-hash text-muted fs-5"></i>
                                            <span className="font-14 fw-bold text-dark" dir="ltr">{order.id.slice(0, 8)}</span>
                                        </div>
                                        <div className="d-none d-md-block vr bg-secondary opacity-25" style={{width:'2px', height:'20px'}}></div>
                                        <div className="d-flex align-items-center gap-2">
                                            <i className="bi bi-calendar2-week text-muted"></i>
                                            <span className="font-13 text-muted">{new Date(order.created_at).toLocaleDateString('fa-IR')}</span>
                                        </div>
                                        <div className="d-none d-md-block vr bg-secondary opacity-25" style={{width:'2px', height:'20px'}}></div>
                                        <div className="d-flex align-items-center gap-2">
                                            <span className="font-13 text-muted">مبلغ کل:</span>
                                            <span className="font-15 fw-900 text-dark">{Number(order.payable_amount).toLocaleString()} <span className="font-11 text-muted fw-normal">تومان</span></span>
                                        </div>
                                    </div>
                                    <div className="d-flex align-items-center justify-content-between justify-content-md-end w-100 w-md-auto">
                                        {getStatusBadge(order.status)}
                                    </div>
                                </div>
                                
                                <div className="d-flex align-items-center justify-content-between mt-2">
                                    <div className="d-flex align-items-center gap-2 overflow-auto custom-scrollbar pb-1">
                                        {order.items && order.items.map((item) => (
                                            <div key={item.id} className="bg-white border border-ui rounded-3 p-1 shadow-sm flex-shrink-0" style={{width:'60px', height:'60px'}} title={item.product_title}>
                                                <img src={item.product_image || '/assets/image/product/product-no-bg.png'} alt={item.product_title} className="img-fluid w-100 h-100 object-fit-contain" />
                                            </div>
                                        ))}
                                    </div>
                                    <Link to={`/dashboard/orders/${order.id}`} className="btn btn-outline-danger rounded-pill px-3 py-1 font-12 fw-bold text-nowrap flex-shrink-0 ms-3 hover-lift">
                                        مشاهده فاکتور <i className="bi bi-chevron-left align-middle"></i>
                                    </Link>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            <style jsx="true">{`
                .hover-lift { transition: transform 0.2s ease, box-shadow 0.2s; }
                .hover-lift:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(239, 64, 86, 0.15) !important; }
                .hover-shadow:hover { box-shadow: 0 10px 25px rgba(0,0,0,0.06) !important; background-color: #fff !important; border-color: #dee2e6 !important;}
                .transition { transition: all 0.3s ease; }
                .hover-bg-danger-light:hover { background-color: #ffe6e9 !important; color: #ef4056 !important;}
                .custom-scrollbar::-webkit-scrollbar { height: 4px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #dee2e6; border-radius: 10px; }
            `}</style>
        </div>
    );
};

export default UserOrders;