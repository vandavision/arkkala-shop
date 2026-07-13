import React, { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getOrderDetail } from '../api/cartApi';
import { SiteContext } from '../context/SiteContext';

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

    if (loading) {
        return (
            <div className="text-center py-5 d-flex flex-column align-items-center justify-content-center bg-white min-vh-100 rounded-4 shadow-sm border border-ui">
                <div className="spinner-border text-danger mb-3" style={{width: '3rem', height:'3rem', borderWidth: '0.25rem'}}></div>
                <h6 className="font-14 fw-bold text-muted">در حال بارگذاری صورتحساب...</h6>
            </div>
        );
    }

    if (!order) {
        return (
            <div className="text-center py-5 d-flex flex-column align-items-center justify-content-center bg-white min-vh-100 rounded-4 shadow-sm border border-ui">
                <i className="bi bi-receipt text-muted opacity-25 d-block mb-3" style={{ fontSize: '5rem' }}></i>
                <h5 className="fw-bold text-dark mb-3">سفارش مورد نظر یافت نشد!</h5>
                <button onClick={() => navigate('/dashboard/orders')} className="btn btn-danger rounded-pill px-4 py-2 font-13 fw-bold shadow-sm">
                    بازگشت به لیست سفارشات
                </button>
            </div>
        );
    }

    const shortOrderId = order.id.slice(0, 8).toUpperCase();
    const orderDate = new Date(order.created_at).toLocaleDateString('fa-IR');
    
    const totalItemsAmount = Number(order.total_items_amount) || 0;
    const discountAmount = Number(order.discount_amount) || 0;
    const subtotalAfterDiscount = totalItemsAmount - discountAmount;
    
    const taxAmount = subtotalAfterDiscount * 0.10; 
    const finalAmountWithoutShipping = subtotalAfterDiscount + taxAmount;
    const shippingCost = Number(order.shipping_cost) || 0;

    return (
        <div className="invoice-page-wrapper px-2 px-md-4 py-4">
            
            <div className="d-flex align-items-center justify-content-between mb-4 d-print-none max-w-a4 mx-auto">
                <button onClick={() => navigate(-1)} className="btn btn-light rounded-circle shadow-sm border border-ui d-flex align-items-center justify-content-center hover-lift" style={{width: '45px', height: '45px'}} title="بازگشت">
                    <i className="bi bi-arrow-right fs-5 text-dark"></i>
                </button>
                <button onClick={handlePrint} className="btn btn-dark rounded-pill px-4 py-2 font-14 fw-bold shadow-sm d-flex align-items-center gap-2 hover-lift">
                    <i className="bi bi-printer-fill fs-5"></i> پرینت صورتحساب
                </button>
            </div>

            <div className="invoice-scroll-wrapper overflow-auto custom-scrollbar w-100 pb-3">
                <div className="invoice-a4-container bg-white p-4 p-md-5 rounded-4 shadow-sm border border-ui mx-auto">
                    
                    <div className="row align-items-center mb-4">
                        <div className="col-3 text-start">
                            {settings?.logo_url ? (
                                <img src={settings.logo_url} alt="لوگو" style={{ maxHeight: '60px', objectFit: 'contain' }} />
                            ) : (
                                <div style={{width:'60px', height:'60px'}}></div>
                            )}
                        </div>
                        <div className="col-6 text-center">
                            <h3 className="fw-900 fs-4 m-0 text-dark">صورتحساب فروش کالا و خدمات</h3>
                        </div>
                        <div className="col-3 text-end text-dark font-13 fw-bold lh-lg">
                            <div className="d-flex justify-content-end gap-2">
                                <span className="text-muted">شماره سفارش:</span>
                                <span dir="ltr">{shortOrderId}</span>
                            </div>
                            <div className="d-flex justify-content-end gap-2">
                                <span className="text-muted">تاریخ سفارش:</span>
                                <span>{orderDate}</span>
                            </div>
                        </div>
                    </div>

                    <table className="table table-bordered border-dark m-0 font-12 text-dark align-middle mb-3 invoice-table">
                        <tbody>
                            <tr>
                                <th className="text-center bg-light fw-bold fs-6 py-2" colSpan="3">مشخصات فروشنده</th>
                            </tr>
                            <tr>
                                <td className="w-50 py-3 px-3 align-top">
                                    <div className="d-flex mb-2"><strong className="min-w-140">نام شخص حقوقی/حقیقی:</strong> {settings?.seller_legal_name || settings?.site_name || 'ثبت نشده'}</div>
                                    <div className="d-flex mb-0"><strong className="min-w-140">آدرس کامل:</strong> {settings?.seller_address || 'ثبت نشده'}</div>
                                </td>
                                <td className="w-25 py-3 px-3 align-top">
                                    <div className="d-flex mb-2"><strong className="min-w-100">شماره اقتصادی:</strong> {settings?.seller_economic_code || '---'}</div>
                                    <div className="d-flex mb-0"><strong className="min-w-100">کد پستی:</strong> <span dir="ltr">{settings?.seller_postal_code || '---'}</span></div>
                                </td>
                                <td className="w-25 py-3 px-3 align-top">
                                    <div className="d-flex mb-2"><strong className="min-w-140">شماره ثبت/شناسه ملی:</strong> {settings?.seller_registration_number || '---'}</div>
                                    <div className="d-flex mb-0"><strong className="min-w-140">تلفن/نمابر:</strong> <span dir="ltr">{settings?.phone_number || '---'}</span></div>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                    
                    <table className="table table-bordered border-dark m-0 font-12 text-dark align-middle mb-4 invoice-table">
                        <tbody>
                            <tr>
                                <th className="text-center bg-light fw-bold fs-6 py-2" colSpan="3">مشخصات خریدار</th>
                            </tr>
                            <tr>
                                <td className="w-50 py-3 px-3 align-top">
                                    <div className="d-flex mb-2"><strong className="min-w-140">نام شخص حقوقی/حقیقی:</strong> {order.customer_first_name} {order.customer_last_name}</div>
                                    <div className="d-flex mb-0"><strong className="min-w-140">آدرس کامل:</strong> {order.province}، {order.city}، {order.postal_address} {order.plaque ? `پلاک ${order.plaque}` : ''} {order.building_unit ? `واحد ${order.building_unit}` : ''}</div>
                                </td>
                                <td className="w-25 py-3 px-3 align-top">
                                    <div className="d-flex mb-2"><strong className="min-w-100">شماره اقتصادی:</strong> ---</div>
                                    <div className="d-flex mb-0"><strong className="min-w-100">کد پستی:</strong> <span dir="ltr">{order.postal_code || '---'}</span></div>
                                </td>
                                <td className="w-25 py-3 px-3 align-top">
                                    <div className="d-flex mb-2"><strong className="min-w-140">شماره ثبت/شناسه ملی:</strong> ---</div>
                                    <div className="d-flex mb-0"><strong className="min-w-140">شماره تماس:</strong> <span dir="ltr">{order.customer_phone || '---'}</span></div>
                                </td>
                            </tr>
                        </tbody>
                    </table>

                    <table className="table table-bordered border-dark m-0 font-12 text-dark align-middle text-center invoice-table">
                        <thead className="bg-light">
                            <tr>
                                <th className="fw-bold fs-6 py-2" colSpan="11">مشخصات کالا یا خدمات مورد معامله</th>
                            </tr>
                            <tr className="font-11 fw-bold align-middle">
                                <th style={{width: '3%'}}>ردیف</th>
                                <th style={{width: '7%'}}>کد کالا</th>
                                <th style={{width: '30%'}} className="text-start pe-2">شرح کالا یا خدمات</th>
                                <th style={{width: '6%'}}>تعداد</th>
                                <th style={{width: '6%'}}>واحد</th>
                                <th style={{width: '10%'}}>مبلغ واحد <br/>(تومان)</th>
                                <th style={{width: '10%'}}>مبلغ کل <br/>(تومان)</th>
                                <th style={{width: '7%'}}>تخفیف <br/>(تومان)</th>
                                <th style={{width: '11%'}}>مبلغ پس از تخفیف <br/>(تومان)</th>
                                <th style={{width: '10%'}}>مالیات و عوارض <br/>(تومان)</th>
                                <th style={{width: '12%'}}>جمع کل به علاوه مالیات <br/>(تومان)</th>
                            </tr>
                        </thead>
                        <tbody className="fw-semibold">
                            {order.items?.map((item, index) => {
                                const itemTotal = Number(item.total_price);
                                return (
                                    <tr key={item.id}>
                                        <td>{index + 1}</td>
                                        <td dir="ltr" className="font-11 text-muted">{item.id.slice(0, 5).toUpperCase()}</td>
                                        <td className="text-start pe-2">
                                            {item.product_title} 
                                            {item.variant_details?.attributes && item.variant_details.attributes.length > 0 && (
                                                <span className="text-muted font-10 ms-1">
                                                    ({item.variant_details.attributes.map(a => `${a.attribute_name}: ${a.value}`).join(' - ')})
                                                </span>
                                            )}
                                        </td>
                                        <td>{item.quantity}</td>
                                        <td>عدد</td>
                                        <td>{Number(item.unit_price).toLocaleString()}</td>
                                        <td>{itemTotal.toLocaleString()}</td>
                                        <td className="text-muted">-</td>
                                        <td>{itemTotal.toLocaleString()}</td>
                                        <td className="text-muted">-</td>
                                        <td>{itemTotal.toLocaleString()}</td>
                                    </tr>
                                );
                            })}

                            <tr className="bg-light fw-bold font-12">
                                <td colSpan="6" className="text-end pe-3">جمع کل</td>
                                <td>{totalItemsAmount.toLocaleString()}</td>
                                <td className="text-danger">{discountAmount.toLocaleString()}</td>
                                <td>{subtotalAfterDiscount.toLocaleString()}</td>
                                <td>{taxAmount.toLocaleString()}</td>
                                <td className="text-success">{finalAmountWithoutShipping.toLocaleString()}</td>
                            </tr>
                            
                            {shippingCost > 0 && (
                                <tr className="bg-light fw-bold font-12">
                                    <td colSpan="10" className="text-end pe-3">هزینه ارسال ({order.shipping_method_name || 'سرویس پستی'})</td>
                                    <td>{shippingCost.toLocaleString()}</td>
                                </tr>
                            )}
                            {shippingCost === 0 && (
                                <tr className="bg-light fw-bold font-12">
                                    <td colSpan="10" className="text-end pe-3">هزینه ارسال ({order.shipping_method_name || 'سرویس پستی'})</td>
                                    <td className="text-danger">پس کرایه / رایگان</td>
                                </tr>
                            )}

                            <tr className="bg-dark text-white fw-bold font-14 print-bg-dark">
                                <td colSpan="10" className="text-end pe-3 py-3 print-text-white">مبلغ نهایی قابل پرداخت (تومان)</td>
                                <td className="py-3 print-text-white fs-6">{Number(order.payable_amount).toLocaleString()}</td>
                            </tr>

                            <tr>
                                <td colSpan="5" className="text-start py-3 pe-3 fw-bold align-middle">
                                    شرایط و نحوه فروش: &nbsp;&nbsp;&nbsp;
                                    {order.is_paid ? <i className="bi bi-check-square-fill text-success fs-5 align-middle"></i> : <i className="bi bi-square fs-5 align-middle"></i>} نقدی &nbsp;&nbsp;&nbsp;
                                    {!order.is_paid ? <i className="bi bi-check-square-fill text-success fs-5 align-middle"></i> : <i className="bi bi-square fs-5 align-middle"></i>} غیرنقدی
                                </td>
                                <td colSpan="6" className="text-start py-3 pe-3 fw-bold align-middle">
                                    توضیحات: {order.tracking_code ? `کد پیگیری تراکنش بانکی: ${order.tracking_code}` : '---'}
                                </td>
                            </tr>
                            <tr style={{ height: '140px' }} className="align-top">
                                <td colSpan="5" className="text-start pt-4 pe-4 fw-bold font-13 position-relative">
                                    مهر و امضاء فروشنده
                                    {order.is_paid && <div className="position-absolute text-success" style={{top: '60px', right: '40px', border: '3px solid #198754', padding: '5px 15px', transform: 'rotate(-10deg)', borderRadius: '10px', fontSize: '18px'}}>پرداخت شده</div>}
                                </td>
                                <td colSpan="6" className="text-start pt-4 pe-4 fw-bold font-13">
                                    مهر و امضاء خریدار
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

            <style jsx="true">{`
                .hover-lift { transition: transform 0.2s ease, box-shadow 0.2s; }
                .hover-lift:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important; }
                
                .min-w-100 { min-width: 100px; display: inline-block; }
                .min-w-120 { min-width: 120px; display: inline-block; }
                .min-w-140 { min-width: 140px; display: inline-block; }
                
                .invoice-table th, .invoice-table td {
                    border-color: #000 !important;
                }

                .max-w-a4 {
                    max-width: 210mm;
                }

                .invoice-a4-container {
                    max-width: 210mm;
                    min-width: 850px;
                    margin: 0 auto;
                }

                .invoice-scroll-wrapper {
                    -webkit-overflow-scrolling: touch;
                }

                .custom-scrollbar::-webkit-scrollbar { height: 8px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #c1c1c1; border-radius: 10px; }

                @media print {
                    @page { 
                        size: A4 portrait; 
                        margin: 10mm; 
                    }
                    
                    * {
                        -webkit-print-color-adjust: exact !important;
                        print-color-adjust: exact !important;
                    }

                    html, body, #root, .app-wrapper, .dashboard-layout, .main-content {
                        background-color: #fff !important;
                        margin: 0 !important;
                        padding: 0 !important;
                        width: 100% !important;
                    }

                    body * {
                        visibility: hidden;
                    }
                    
                    .invoice-page-wrapper, .invoice-page-wrapper * {
                        visibility: visible;
                    }
                    
                    .invoice-scroll-wrapper { overflow: visible !important; }

                    .invoice-page-wrapper {
                        position: absolute;
                        left: 0;
                        top: 0;
                        width: 100%;
                        margin: 0 !important;
                        padding: 0 !important;
                    }

                    .invoice-a4-container {
                        width: 100% !important;
                        max-width: 100% !important;
                        min-width: 100% !important;
                        border: none !important;
                        box-shadow: none !important;
                        padding: 0 !important;
                        margin: 0 !important;
                    }

                    .d-print-none, .d-print-none * {
                        display: none !important;
                        height: 0 !important;
                    }

                    .table {
                        page-break-inside: auto;
                        width: 100% !important;
                    }
                    tr {
                        page-break-inside: avoid;
                        page-break-after: auto;
                    }
                    th, td {
                        border: 1px solid #000 !important;
                        color: #000 !important;
                        padding: 6px 4px !important;
                    }
                    
                    .bg-light { background-color: #f1f3f5 !important; }
                    .print-bg-dark { background-color: #212529 !important; }
                    .print-text-white { color: #fff !important; }
                }
            `}</style>
        </div>
    );
};

export default OrderInvoicePage;