import React, { useState } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import { requestPayment } from '../api/paymentApi';

const PaymentResultPage = () => {
    const [searchParams] = useSearchParams();
    const navigate = useNavigate();
    
    const status = searchParams.get('status');
    const refId = searchParams.get('ref_id');
    const orderId = searchParams.get('order_id');
    
    const [isRetrying, setIsRetrying] = useState(false);
    const [errorMsg, setErrorMsg] = useState('');

    const isSuccess = status === 'successful';
    const isCanceled = status === 'canceled';
    
    const handleRetryPayment = async () => {
        if (!orderId) {
            setErrorMsg("شناسه سفارش یافت نشد. لطفاً از پنل کاربری اقدام کنید.");
            return;
        }
        
        setIsRetrying(true);
        setErrorMsg('');
        
        try {
            const response = await requestPayment(orderId, 'zarinpal');
            window.location.href = response.payment_url;
        } catch (error) {
            setErrorMsg(error.response?.data?.error || 'خطا در برقراری ارتباط با درگاه پرداخت. لطفاً دقایقی دیگر تلاش کنید.');
            setIsRetrying(false);
        }
    };

    return (
        <main className="payment-result-page bg-light min-vh-100 d-flex align-items-center justify-content-center py-5">
            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-12 col-md-8 col-lg-6 col-xl-5">
                        <div className="bg-white rounded-5 shadow-sm border border-ui p-4 p-md-5 text-center position-relative overflow-hidden animate-fade-in">
                            
                            <div className={`position-absolute top-0 start-50 translate-middle-x w-100 rounded-circle blur-blob opacity-25 ${isSuccess ? 'bg-success' : 'bg-danger'}`} style={{ height: '150px', zIndex: 0, filter: 'blur(50px)' }}></div>

                            <div className="position-relative z-1">
                                {isSuccess ? (
                                    <>
                                        <div className="icon-box bg-success bg-opacity-10 text-success rounded-circle d-flex align-items-center justify-content-center mx-auto mb-4" style={{ width: '100px', height: '100px' }}>
                                            <i className="bi bi-check-circle-fill" style={{ fontSize: '3.5rem' }}></i>
                                        </div>
                                        <h2 className="fw-900 text-dark mb-3">پرداخت با موفقیت انجام شد</h2>
                                        <p className="text-muted font-14 lh-lg mb-4">
                                            سفارش شما با موفقیت ثبت شد و در اسرع وقت پردازش و ارسال خواهد شد. از خرید شما سپاسگزاریم.
                                        </p>
                                        
                                        {refId && (
                                            <div className="bg-light border border-ui rounded-4 p-3 mb-4 d-flex justify-content-between align-items-center mx-md-4">
                                                <span className="font-13 text-muted fw-bold">کد پیگیری تراکنش:</span>
                                                <span className="font-15 text-dark fw-900 font-monospace">{refId}</span>
                                            </div>
                                        )}
                                        
                                        <div className="d-flex flex-column gap-3 mt-5">
                                            <Link to="/dashboard/orders" className="btn btn-success rounded-pill py-3 fw-bold shadow-sm hover-lift text-white w-100">
                                                پیگیری سفارش در پنل کاربری
                                            </Link>
                                            <Link to="/shop" className="btn btn-light rounded-pill py-3 fw-bold border border-ui text-muted hover-bg-light transition w-100">
                                                بازگشت به فروشگاه
                                            </Link>
                                        </div>
                                    </>
                                ) : (
                                    <>
                                        <div className="icon-box bg-danger bg-opacity-10 text-danger rounded-circle d-flex align-items-center justify-content-center mx-auto mb-4" style={{ width: '100px', height: '100px' }}>
                                            <i className={isCanceled ? "bi bi-x-circle-fill" : "bi bi-exclamation-triangle-fill"} style={{ fontSize: '3.5rem' }}></i>
                                        </div>
                                        <h2 className="fw-900 text-dark mb-3">
                                            {isCanceled ? 'پرداخت لغو شد' : 'پرداخت ناموفق بود'}
                                        </h2>
                                        <p className="text-muted font-14 lh-lg mb-4">
                                            {isCanceled 
                                                ? 'شما از پرداخت انصراف دادید. نگران نباشید، سفارش شما تا ۲ ساعت آینده محفوظ است.' 
                                                : 'در فرآیند پرداخت خطایی رخ داد. چنانچه مبلغی از حساب شما کسر شده است، تا ۷۲ ساعت آینده به حساب شما بازمی‌گردد.'}
                                        </p>
                                        
                                        {errorMsg && (
                                            <div className="alert alert-danger font-13 fw-bold rounded-4 mb-4 text-justify lh-base">
                                                <i className="bi bi-info-circle-fill me-2"></i>{errorMsg}
                                            </div>
                                        )}
                                        
                                        <div className="d-flex flex-column gap-3 mt-5">
                                            {orderId && (
                                                <button onClick={handleRetryPayment} disabled={isRetrying} className="btn main-color-two-bg text-white rounded-pill py-3 fw-bold shadow hover-lift w-100 d-flex align-items-center justify-content-center gap-2">
                                                    {isRetrying ? (
                                                        <div className="spinner-border spinner-border-sm text-white"></div>
                                                    ) : (
                                                        <><i className="bi bi-arrow-clockwise fs-5"></i> تلاش مجدد برای پرداخت</>
                                                    )}
                                                </button>
                                            )}
                                            <Link to="/dashboard/orders" className="btn btn-outline-danger rounded-pill py-3 fw-bold shadow-sm hover-lift text-danger w-100">
                                                مشاهده سفارش در پنل
                                            </Link>
                                            <Link to="/shop" className="btn btn-light rounded-pill py-3 fw-bold border border-ui text-muted hover-bg-light transition w-100">
                                                بازگشت به فروشگاه
                                            </Link>
                                        </div>
                                    </>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <style jsx="true">{`
                .animate-fade-in { animation: fadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1); }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
                .hover-lift { transition: transform 0.2s ease, box-shadow 0.2s; }
                .hover-lift:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important; }
                .transition { transition: all 0.3s ease; }
            `}</style>
        </main>
    );
};

export default PaymentResultPage;