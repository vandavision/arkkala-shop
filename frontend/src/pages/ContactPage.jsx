import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { getStaticPageSeo, submitContactMessage } from '../api/homeApi';
import { SiteContext } from '../context/SiteContext';
import SeoMeta from '../components/SeoMeta';

const ContactPage = () => {
    const { settings } = useContext(SiteContext);
    const [seoData, setSeoData] = useState(null);
    const [loading, setLoading] = useState(true);

    const [formData, setFormData] = useState({
        full_name: '',
        phone_number: '',
        email: '',
        subject: '',
        message: ''
    });
    const [isSubmitting, setIsSubmitting] = useState(false);

    const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
    const showToast = (message, type = 'success') => {
        setToast({ show: true, message, type });
        setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 4000);
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const meta = await getStaticPageSeo('ContactPage');
                setSeoData(meta);
            } catch (error) {
                console.error("Error fetching Contact SEO:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, []);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        
        if (!formData.full_name.trim() || !formData.phone_number.trim() || !formData.message.trim()) {
            return showToast("لطفاً فیلدهای ستاره‌دار را تکمیل کنید.", "warning");
        }

        setIsSubmitting(true);
        try {
            await submitContactMessage(formData);
            showToast("پیام شما با موفقیت ارسال شد. در اسرع وقت پاسخگوی شما خواهیم بود.", "success");
            setFormData({ full_name: '', phone_number: '', email: '', subject: '', message: '' });
        } catch (error) {
            const errorMsg = error.response?.data?.error || "خطا در ارسال پیام. لطفاً دقایقی دیگر تلاش کنید.";
            showToast(errorMsg, "danger");
        } finally {
            setIsSubmitting(false);
        }
    };

    if (loading) {
        return (
            <div className="d-flex flex-column justify-content-center align-items-center min-vh-100 bg-light">
                <div className="spinner-border text-danger mb-3" style={{width: '3.5rem', height:'3.5rem', borderWidth: '0.25rem'}} role="status"></div>
                <h5 className="fw-bold text-muted font-14">در حال بارگذاری...</h5>
            </div>
        );
    }

    return (
        <main className="contact-page bg-light min-vh-100 pb-5">
            <SeoMeta seoData={seoData} fallbackTitle={`تماس با ما | ${settings?.site_name || 'فروشگاه'}`} />
            
            <div className={`custom-toast ${toast.show ? 'show' : ''} bg-${toast.type} shadow-lg d-flex align-items-center gap-3`}>
                <i className={`bi ${toast.type === 'success' ? 'bi-check-circle-fill' : toast.type === 'warning' ? 'bi-exclamation-triangle-fill' : 'bi-x-circle-fill'} fs-3 text-white`}></i>
                <span className="font-14 fw-bold text-white lh-base">{toast.message}</span>
            </div>

            <section className="bread-crumb py-3 mb-4 mb-lg-5 bg-white shadow-sm border-bottom border-light position-relative z-3">
                <div className="container-fluid container-xl">
                    <nav aria-label="breadcrumb">
                        <ol className="breadcrumb mb-0 px-2">
                            <li className="breadcrumb-item"><Link to="/" className="font-14 text-muted text-decoration-none hover-text-danger transition"><i className="bi bi-house me-1"></i>خانه</Link></li>
                            <li className="breadcrumb-item active text-danger font-14 fw-bold" aria-current="page">تماس با ما</li>
                        </ol>
                    </nav>
                </div>
            </section>

            <div className="container-fluid container-xl">
                
                {/* Header Section */}
                <div className="text-center mb-5 animate-fade-in">
                    <div className="bg-danger bg-opacity-10 d-inline-flex p-3 rounded-circle mb-3">
                        <i className="bi bi-headset text-danger display-5"></i>
                    </div>
                    <h1 className="fw-900 h3 text-dark mb-2">تماس با {settings?.site_name || 'ما'}</h1>
                    <p className="text-muted font-14">مشتاق شنیدن صدای شما هستیم؛ نظرات، پیشنهادات و سوالات خود را با ما در میان بگذارید.</p>
                </div>

                <div className="row gy-4 gx-lg-5">
                    
                    {/* اطلاعات تماس (سمت راست در RTL) */}
                    <div className="col-lg-5 order-2 order-lg-1 animate-fade-in" style={{ animationDelay: '0.1s' }}>
                        <div className="bg-white rounded-5 shadow-sm border border-ui p-4 p-md-5 h-100 position-relative overflow-hidden">
                            <div className="position-absolute top-0 end-0 bg-danger opacity-5 rounded-circle translate-middle" style={{width:'250px', height:'250px', filter:'blur(40px)'}}></div>
                            
                            <h3 className="fw-900 text-dark mb-4 pb-3 border-bottom border-light font-16 position-relative z-1">
                                <i className="bi bi-geo-alt-fill text-danger me-2"></i> راه‌های ارتباطی
                            </h3>

                            <div className="contact-info-list d-flex flex-column gap-4 position-relative z-1 mb-5">
                                <div className="d-flex align-items-start gap-3">
                                    <div className="bg-light rounded-circle d-flex align-items-center justify-content-center flex-shrink-0 border border-ui shadow-sm" style={{width: '50px', height: '50px'}}>
                                        <i className="bi bi-telephone-fill text-danger fs-5"></i>
                                    </div>
                                    <div>
                                        <span className="d-block font-12 fw-bold text-muted mb-1">شماره تماس پشتیبانی:</span>
                                        <a href={`tel:${settings?.phone_number}`} className="font-16 fw-900 text-dark text-decoration-none hover-text-danger transition d-inline-block" dir="ltr">
                                            {settings?.phone_number || 'در حال حاضر ثبت نشده'}
                                        </a>
                                    </div>
                                </div>

                                <div className="d-flex align-items-start gap-3">
                                    <div className="bg-light rounded-circle d-flex align-items-center justify-content-center flex-shrink-0 border border-ui shadow-sm" style={{width: '50px', height: '50px'}}>
                                        <i className="bi bi-envelope-fill text-danger fs-5"></i>
                                    </div>
                                    <div>
                                        <span className="d-block font-12 fw-bold text-muted mb-1">پست الکترونیک:</span>
                                        <a href={`mailto:${settings?.email || 'info@arkkala.com'}`} className="font-15 fw-bold text-dark text-decoration-none hover-text-danger transition d-inline-block" dir="ltr">
                                            {settings?.email || 'info@arkkala.com'}
                                        </a>
                                    </div>
                                </div>

                                <div className="d-flex align-items-start gap-3">
                                    <div className="bg-light rounded-circle d-flex align-items-center justify-content-center flex-shrink-0 border border-ui shadow-sm" style={{width: '50px', height: '50px'}}>
                                        <i className="bi bi-clock-fill text-danger fs-5"></i>
                                    </div>
                                    <div>
                                        <span className="d-block font-12 fw-bold text-muted mb-1">ساعات کاری:</span>
                                        <span className="font-14 fw-bold text-dark lh-base">
                                            {settings?.working_hours || 'شنبه تا پنجشنبه، ساعت ۹ صبح الی ۱۸'}
                                        </span>
                                    </div>
                                </div>

                                <div className="d-flex align-items-start gap-3">
                                    <div className="bg-light rounded-circle d-flex align-items-center justify-content-center flex-shrink-0 border border-ui shadow-sm" style={{width: '50px', height: '50px'}}>
                                        <i className="bi bi-map-fill text-danger fs-5"></i>
                                    </div>
                                    <div>
                                        <span className="d-block font-12 fw-bold text-muted mb-1">آدرس دفتر مرکزی:</span>
                                        <span className="font-14 fw-bold text-dark lh-lg text-justify d-block">
                                            {settings?.seller_address || 'آدرس فروشگاه هنوز در تنظیمات سیستم ثبت نشده است.'}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <h3 className="fw-900 text-dark mb-4 pb-3 border-bottom border-light font-16 position-relative z-1">
                                <i className="bi bi-share-fill text-danger me-2"></i> شبکه‌های اجتماعی
                            </h3>
                            
                            <div className="d-flex align-items-center gap-3 position-relative z-1 flex-wrap">
                                {settings?.instagram && (
                                    <a href={settings.instagram} target="_blank" rel="noreferrer" className="btn btn-light border border-ui rounded-circle d-flex align-items-center justify-content-center shadow-sm hover-lift text-danger" style={{width: '45px', height: '45px'}} aria-label="اینستاگرام">
                                        <i className="bi bi-instagram fs-5"></i>
                                    </a>
                                )}
                                {settings?.telegram && (
                                    <a href={settings.telegram} target="_blank" rel="noreferrer" className="btn btn-light border border-ui rounded-circle d-flex align-items-center justify-content-center shadow-sm hover-lift text-primary" style={{width: '45px', height: '45px'}} aria-label="تلگرام">
                                        <i className="bi bi-telegram fs-5"></i>
                                    </a>
                                )}
                                {settings?.whatsapp && (
                                    <a href={settings.whatsapp} target="_blank" rel="noreferrer" className="btn btn-light border border-ui rounded-circle d-flex align-items-center justify-content-center shadow-sm hover-lift text-success" style={{width: '45px', height: '45px'}} aria-label="واتساپ">
                                        <i className="bi bi-whatsapp fs-5"></i>
                                    </a>
                                )}
                                {settings?.linkedin && (
                                    <a href={settings.linkedin} target="_blank" rel="noreferrer" className="btn btn-light border border-ui rounded-circle d-flex align-items-center justify-content-center shadow-sm hover-lift text-info" style={{width: '45px', height: '45px'}} aria-label="لینکدین">
                                        <i className="bi bi-linkedin fs-5"></i>
                                    </a>
                                )}
                                {settings?.twitter && (
                                    <a href={settings.twitter} target="_blank" rel="noreferrer" className="btn btn-light border border-ui rounded-circle d-flex align-items-center justify-content-center shadow-sm hover-lift text-dark" style={{width: '45px', height: '45px'}} aria-label="توییتر">
                                        <i className="bi bi-twitter-x fs-5"></i>
                                    </a>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* فرم تماس با ما (سمت چپ در RTL) */}
                    <div className="col-lg-7 order-1 order-lg-2 animate-fade-in" style={{ animationDelay: '0.2s' }}>
                        <div className="bg-white rounded-5 shadow-sm border border-ui p-4 p-md-5 h-100">
                            <h3 className="fw-900 text-dark mb-3 font-18 d-flex align-items-center gap-2">
                                <i className="bi bi-envelope-paper-fill text-danger fs-4"></i> ارسال پیام
                            </h3>
                            <p className="text-muted font-13 mb-4 pb-3 border-bottom border-light">نظرات، پیشنهادات و انتقادات خود را فرم زیر برای ما ارسال کنید.</p>
                            
                            <form onSubmit={handleSubmit}>
                                <div className="row gy-4">
                                    <div className="col-md-6">
                                        <label className="fw-bold font-13 text-dark mb-2">نام و نام خانوادگی <span className="text-danger">*</span></label>
                                        <input 
                                            type="text" 
                                            name="full_name" 
                                            value={formData.full_name} 
                                            onChange={handleChange} 
                                            className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light focus-danger" 
                                            placeholder="مثال: علی رضایی" 
                                            required 
                                        />
                                    </div>
                                    <div className="col-md-6">
                                        <label className="fw-bold font-13 text-dark mb-2">شماره تماس <span className="text-danger">*</span></label>
                                        <input 
                                            type="text" 
                                            name="phone_number" 
                                            value={formData.phone_number} 
                                            onChange={handleChange} 
                                            className="form-control border-ui py-3 font-14 rounded-3 shadow-sm bg-light focus-danger text-start" 
                                            placeholder="09123456789" 
                                            dir="ltr"
                                            required 
                                        />
                                    </div>
                                    <div className="col-md-6">
                                        <label className="fw-bold font-13 text-dark mb-2">پست الکترونیک</label>
                                        <input 
                                            type="email" 
                                            name="email" 
                                            value={formData.email} 
                                            onChange={handleChange} 
                                            className="form-control border-ui py-3 font-14 rounded-3 shadow-sm bg-light focus-danger text-start" 
                                            placeholder="email@domain.com" 
                                            dir="ltr"
                                        />
                                    </div>
                                    <div className="col-md-6">
                                        <label className="fw-bold font-13 text-dark mb-2">موضوع پیام</label>
                                        <input 
                                            type="text" 
                                            name="subject" 
                                            value={formData.subject} 
                                            onChange={handleChange} 
                                            className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light focus-danger" 
                                            placeholder="مثال: پیگیری سفارش، پیشنهاد و..." 
                                        />
                                    </div>
                                    <div className="col-12">
                                        <label className="fw-bold font-13 text-dark mb-2">متن پیام <span className="text-danger">*</span></label>
                                        <textarea 
                                            name="message" 
                                            value={formData.message} 
                                            onChange={handleChange} 
                                            className="form-control border-ui py-3 px-4 font-13 rounded-4 shadow-sm bg-light focus-danger lh-lg text-justify" 
                                            rows="5" 
                                            placeholder="متن کامل پیام خود را اینجا بنویسید..." 
                                            required
                                        ></textarea>
                                    </div>
                                    <div className="col-12 mt-4 text-end">
                                        <button type="submit" disabled={isSubmitting} className="btn btn-danger px-5 py-3 rounded-pill fw-bold font-14 shadow hover-lift w-100 w-md-auto d-flex align-items-center justify-content-center gap-2 ms-auto">
                                            {isSubmitting ? (
                                                <div className="spinner-border spinner-border-sm text-white" role="status"></div>
                                            ) : (
                                                <><i className="bi bi-send-fill fs-5"></i> ارسال پیام به پشتیبانی</>
                                            )}
                                        </button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>

            <style jsx="true">{`
                .transition { transition: all 0.3s ease-in-out; }
                .hover-lift { transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.3s; }
                .hover-lift:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important; }
                
                .hover-text-danger:hover { color: #ef4056 !important; }
                .focus-danger:focus { background-color: #fff !important; box-shadow: 0 0 0 4px rgba(239, 64, 86, 0.1) !important; border-color: #ef4056 !important; outline: none; }
                
                .animate-fade-in { animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) both; }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
                
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

export default ContactPage;