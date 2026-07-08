import React, { useState, useEffect, useContext } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { getOrderDetail } from '../api/cartApi';
import { SiteContext } from '../context/SiteContext';

const resolveImageUrl = (url) => {
    if (!url) return '/assets/image/product/product-no-bg.png';
    if (url.startsWith('http') || url.startsWith('data:')) return url;
    let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    baseUrl = baseUrl.replace(/\/api\/?$/, '');
    return `${baseUrl}${url.startsWith('/') ? '' : '/'}${url}`;
};

const OrderInvoicePage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { settings } = useContext(SiteContext);
    
    const [order, setOrder] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchOrder = async () => {
            try {
                const data = await getOrderDetail(id);
                setOrder(data);
            } catch (error) {
                console.error("Error fetching order details:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchOrder();
        window.scrollTo(0, 0);
    }, [id]);

    const handlePrint = () => {
        window.print();
    };

    const getStatusBadge = (status) => {
        switch(status) {
            case 'pending': return <span className="badge bg-warning bg-opacity-10 text-warning border border-warning border-opacity-50 px-3 py-2 rounded-pill font-13 fw-bold">در انتظار پرداخت</span>;
            case 'processing': return <span className="badge bg-info bg-opacity-10 text-info border border-info border-opacity-50 px-3 py-2 rounded-pill font-13 fw-bold">در حال پردازش</span>;
            case 'shipped': return <span className="badge bg-primary bg-opacity-10 text-primary border border-primary border-opacity-50 px-3 py-2 rounded-pill font-13 fw-bold">ارسال شده</span>;
            case 'delivered': return <span className="badge bg-success bg-opacity-10 text-success border border-success border-opacity-50 px-3 py-2 rounded-pill font-13 fw-bold">تحویل شده</span>;
            case 'cancelled': return <span className="badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-50 px-3 py-2 rounded-pill font-13 fw-bold">لغو شده</span>;
            default: return <span className="badge bg-secondary text-white px-3 py-2 rounded-pill font-13 fw-bold">{status}</span>;
        }
    };

    if (loading) {
        return (
            <div className="text-center py-5 d-flex flex-column align-items-center justify-content-center bg-white rounded-4 shadow-sm border border-ui min-vh-50">
                <div className="spinner-border text-danger mb-3" style={{width: '3rem', height:'3rem', borderWidth: '0.25rem'}}></div>
                <h6 className="font-14 fw-bold text-muted">در حال بارگذاری فاکتور سفارش...</h6>
            </div>
        );
    }

    if (!order) {
        return (
            <div className="text-center py-5 d-flex flex-column align-items-center justify-content-center bg-white rounded-4 shadow-sm border border-ui min-vh-50">
                <i className="bi bi-receipt text-muted opacity-25 d-block mb-3" style={{ fontSize: '5rem' }}></i>
                <h5 className="fw-bold text-dark mb-3">سفارش مورد نظر یافت نشد!</h5>
                <button onClick={() => navigate('/dashboard/orders')} className="btn btn-danger rounded-pill px-4 py-2 font-13 fw-bold shadow-sm hover-lift">
                    بازگشت به لیست سفارشات
                </button>
            </div>
        );
    }

    const shortOrderId = order.id.slice(0, 8).toUpperCase();
    const orderDate = new Date(order.created_at).toLocaleDateString('fa-IR');
    const orderTime = new Date(order.created_at).toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' });

    return (
        <div className="order-invoice-page position-relative">
            <div className="d-flex align-items-center justify-content-between mb-4 no-print">
                <div className="d-flex align-items-center gap-3">
                    <button onClick={() => navigate(-1)} className="btn btn-light rounded-circle shadow-sm border border-ui d-flex align-items-center justify-content-center hover-lift" style={{width: '45px', height: '45px'}}>
                        <i className="bi bi-arrow-right fs-5 text-dark"></i>
                    </button>
                    <h2 className="fw-900 h5 m-0 text-dark">جزئیات <span className="text-danger">سفارش</span></h2>
                </div>
                <button onClick={handlePrint} className="btn btn-primary rounded-pill px-4 py-2 font-13 fw-bold shadow-sm hover-lift d-flex align-items-center gap-2">
                    <i className="bi bi-printer-fill fs-5"></i> چاپ فاکتور
                </button>
            </div>

            <div className="invoice-print-area bg-white rounded-4 border border-ui shadow-sm p-4 p-md-5 mb-4">
                
                {/* Invoice Header */}
                <div className="d-flex flex-column flex-md-row align-items-center justify-content-between border-bottom border-dark border-opacity-25 pb-4 mb-4 gap-4">
                    <div className="d-flex align-items-center gap-3">
                        <img src={settings?.logo_url || "/assets/image/logo.png"} alt={settings?.site_name} style={{ maxHeight: '60px', objectFit: 'contain' }} />
                        <div className="vr bg-secondary opacity-25 d-none d-md-block" style={{width:'2px', height:'40px'}}></div>
                        <div className="d-none d-md-block">
                            <h4 className="fw-900 text-dark m-0 font-18 mb-1">فروشگاه {settings?.site_name || 'ارک کالا'}</h4>
                            <span className="font-12 text-muted">فاکتور فروش کالا و خدمات</span>
                        </div>
                    </div>
                    
                    <div className="text-center text-md-end">
                        <h5 className="fw-bold text-dark font-15 mb-2">شماره سفارش: <span className="font-monospace" dir="ltr">{shortOrderId}</span></h5>
                        <div className="d-flex align-items-center justify-content-center justify-content-md-end gap-3 text-muted font-13">
                            <span><i className="bi bi-calendar2-week me-1"></i> {orderDate}</span>
                            <span><i className="bi bi-clock me-1"></i> {orderTime}</span>
                        </div>
                    </div>
                </div>

                {/* Customer & Order Info */}
                <div className="row mb-5 border border-ui rounded-4 mx-0 overflow-hidden">
                    <div className="col-md-6 p-4 bg-light border-end-md border-ui">
                        <h6 className="fw-900 text-dark mb-3 font-14"><i className="bi bi-person-vcard text-danger me-2"></i> اطلاعات خریدار</h6>
                        <ul className="list-unstyled m-0 d-flex flex-column gap-3 font-13">
                            <li className="d-flex align-items-start gap-2">
                                <span className="text-muted min-w-80">تحویل گیرنده:</span>
                                <strong className="text-dark">{order.guest_first_name} {order.guest_last_name}</strong>
                            </li>
                            <li className="d-flex align-items-start gap-2">
                                <span className="text-muted min-w-80">شماره تماس:</span>
                                <strong className="text-dark font-monospace" dir="ltr">{order.guest_phone || '---'}</strong>
                            </li>
                            <li className="d-flex align-items-start gap-2">
                                <span className="text-muted min-w-80">کد پستی:</span>
                                <strong className="text-dark font-monospace" dir="ltr">{order.postal_code || '---'}</strong>
                            </li>
                            <li className="d-flex align-items-start gap-2">
                                <span className="text-muted min-w-80 flex-shrink-0">آدرس:</span>
                                <strong className="text-dark lh-lg text-justify">{order.province}، {order.city}، {order.postal_address} {order.plaque ? `پلاک ${order.plaque}` : ''} {order.building_unit ? `واحد ${order.building_unit}` : ''}</strong>
                            </li>
                        </ul>
                    </div>
                    <div className="col-md-6 p-4">
                        <h6 className="fw-900 text-dark mb-3 font-14"><i className="bi bi-info-circle text-primary me-2"></i> اطلاعات سفارش</h6>
                        <ul className="list-unstyled m-0 d-flex flex-column gap-3 font-13">
                            <li className="d-flex align-items-center gap-2">
                                <span className="text-muted min-w-80">وضعیت سفارش:</span>
                                {getStatusBadge(order.status)}
                            </li>
                            <li className="d-flex align-items-center gap-2">
                                <span className="text-muted min-w-80">روش ارسال:</span>
                                <strong className="text-dark">{order.shipping_method_name || 'پست پیشتاز'}</strong>
                            </li>
                            <li className="d-flex align-items-center gap-2">
                                <span className="text-muted min-w-80">کد پیگیری پرداخت:</span>
                                <strong className="text-dark font-monospace" dir="ltr">{order.tracking_code || '---'}</strong>
                            </li>
                            <li className="d-flex align-items-center gap-2">
                                <span className="text-muted min-w-80">وضعیت پرداخت:</span>
                                {order.is_paid ? (
                                    <span className="badge bg-success bg-opacity-10 text-success rounded-pill px-3 py-1"><i className="bi bi-check2-all me-1"></i> پرداخت شده</span>
                                ) : (
                                    <span className="badge bg-danger bg-opacity-10 text-danger rounded-pill px-3 py-1"><i className="bi bi-x-lg me-1"></i> پرداخت نشده</span>
                                )}
                            </li>
                        </ul>
                    </div>
                </div>

                {/* Order Items Table */}
                <h6 className="fw-900 text-dark mb-3 font-15"><i className="bi bi-cart-check text-success me-2"></i> لیست کالاهای سفارش</h6>
                <div className="table-responsive border border-ui rounded-4 mb-4">
                    <table className="table table-hover align-middle mb-0 text-center font-13">
                        <thead className="table-light text-muted">
                            <tr>
                                <th className="py-3 fw-bold border-0">ردیف</th>
                                <th className="py-3 fw-bold border-0 text-start">شرح کالا</th>
                                <th className="py-3 fw-bold border-0">تعداد</th>
                                <th className="py-3 fw-bold border-0">مبلغ واحد (تومان)</th>
                                <th className="py-3 fw-bold border-0">مبلغ کل (تومان)</th>
                            </tr>
                        </thead>
                        <tbody className="border-top-0">
                            {order.items && order.items.map((item, index) => (
                                <tr key={item.id} className="border-bottom border-light">
                                    <td className="py-3 text-muted fw-bold">{index + 1}</td>
                                    <td className="py-3 text-start">
                                        <div className="d-flex align-items-center gap-3">
                                            <div className="bg-white border border-light shadow-sm rounded-3 p-1 flex-shrink-0" style={{width: '50px', height: '50px'}}>
                                                <img src={resolveImageUrl(item.product_image)} alt={item.product_title} className="img-fluid w-100 h-100 object-fit-contain" onError={(e) => { e.target.src = '/assets/image/product/product-no-bg.png'; }} />
                                            </div>
                                            <div className="d-flex flex-column justify-content-center">
                                                <span className="fw-bold text-dark d-block mb-1 text-overflow-1">{item.product_title}</span>
                                                {item.variant_details && item.variant_details.attributes && (
                                                    <div className="d-flex gap-2 font-11 text-muted">
                                                        {item.variant_details.attributes.map((attr, idx) => (
                                                            <span key={idx} className="bg-light px-2 py-1 rounded-pill">{attr.attribute_name}: {attr.value}</span>
                                                        ))}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    </td>
                                    <td className="py-3 fw-bold text-dark">{item.quantity}</td>
                                    <td className="py-3 text-muted">{Number(item.unit_price).toLocaleString()}</td>
                                    <td className="py-3 fw-bold text-dark">{Number(item.total_price).toLocaleString()}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Order Financial Summary */}
                <div className="row justify-content-end mx-0">
                    <div className="col-12 col-md-6 col-lg-5 p-0">
                        <div className="bg-light border border-ui rounded-4 p-4 d-flex flex-column gap-3 font-14">
                            <div className="d-flex justify-content-between align-items-center">
                                <span className="text-muted">مجموع مبلغ کالاها:</span>
                                <strong className="text-dark">{Number(order.total_items_amount).toLocaleString()} تومان</strong>
                            </div>
                            
                            {Number(order.discount_amount) > 0 && (
                                <div className="d-flex justify-content-between align-items-center">
                                    <span className="text-danger fw-bold"><i className="bi bi-tag-fill me-1"></i> سود شما از خرید:</span>
                                    <strong className="text-danger fw-bold">{Number(order.discount_amount).toLocaleString()} تومان</strong>
                                </div>
                            )}

                            <div className="d-flex justify-content-between align-items-center">
                                <span className="text-muted">هزینه ارسال:</span>
                                <strong className="text-dark">{Number(order.shipping_cost) === 0 ? 'پس‌کرایه / رایگان' : `${Number(order.shipping_cost).toLocaleString()} تومان`}</strong>
                            </div>

                            <div className="d-flex justify-content-between align-items-center border-bottom border-dark border-opacity-10 pb-3 mb-1">
                                <span className="text-muted">مالیات (۱۰٪):</span>
                                <strong className="text-dark">
                                    {Number((order.total_items_amount - order.discount_amount) * 0.10).toLocaleString()} تومان
                                </strong>
                            </div>

                            <div className="d-flex justify-content-between align-items-center pt-2">
                                <span className="fw-900 text-dark font-15">مبلغ نهایی قابل پرداخت:</span>
                                <strong className="fw-900 text-success font-20">{Number(order.payable_amount).toLocaleString()} <span className="font-12 text-muted fw-normal">تومان</span></strong>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Print Footer Notice */}
                <div className="mt-5 pt-4 border-top border-light text-center no-screen d-none print-only">
                    <p className="font-12 text-muted mb-0">این فاکتور به صورت سیستمی تولید شده و بدون مهر و امضا فاقد اعتبار قانونی جهت ارائه به مراجع ذی‌صلاح می‌باشد.</p>
                </div>
            </div>

            <style jsx="true">{`
                .hover-lift { transition: transform 0.2s ease, box-shadow 0.2s; }
                .hover-lift:hover { transform: translateY(-3px); box-shadow: 0 5px 15px rgba(0,0,0,0.08) !important; }
                .min-w-80 { min-width: 90px; display: inline-block; }
                .text-overflow-1 { overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; }
                
                @media (min-width: 768px) {
                    .border-end-md { border-left: 1px solid #dee2e6; border-right: none; }
                }

                @media print {
                    body { background-color: #fff !important; margin: 0; padding: 0; }
                    body * { visibility: hidden; }
                    .invoice-print-area, .invoice-print-area * { visibility: visible; }
                    .invoice-print-area { position: absolute; left: 0; top: 0; width: 100%; border: none !important; box-shadow: none !important; padding: 0 !important; }
                    .no-print { display: none !important; }
                    .print-only { display: block !important; }
                    
                    .bg-light { background-color: #f8f9fa !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
                    .table-light { background-color: #f8f9fa !important; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
                    .badge { border: 1px solid #dee2e6 !important; color: #000 !important; background: transparent !important; }
                }
            `}</style>
        </div>
    );
};

export default OrderInvoicePage;