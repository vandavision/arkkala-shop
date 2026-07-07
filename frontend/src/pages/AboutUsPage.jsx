import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { getAboutUsData } from '../api/homeApi';
import { SiteContext } from '../context/SiteContext';

const AboutUsPage = () => {
    const { settings } = useContext(SiteContext);
    const [aboutData, setAboutUsData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getAboutUsData().then(data => {
            setAboutUsData(data);
            setLoading(false);
        });
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, []);

    if (loading) {
        return (
            <div className="d-flex flex-column justify-content-center align-items-center min-vh-100 bg-light">
                <div className="spinner-border text-danger mb-3" style={{width: '3.5rem', height:'3.5rem', borderWidth: '0.25rem'}} role="status"></div>
                <h5 className="fw-bold text-muted font-14">در حال بارگذاری اطلاعات صفحه...</h5>
            </div>
        );
    }

    const title = aboutData?.title || `درباره فروشگاه ${settings?.site_name || 'ارک کالا'}`;
    const content = aboutData?.content || "توضیحاتی برای این بخش در سیستم ثبت نشده است.";
    const imageUrl = aboutData?.image_url || "/assets/image/about/rtl-theme.jpg";

    return (
        <main className="about-us-page bg-light min-vh-100 pb-5">
            <section className="bread-crumb py-3 mb-5 bg-white shadow-sm border-bottom border-light">
                <div className="container-fluid container-xl">
                    <nav aria-label="breadcrumb">
                        <ol className="breadcrumb mb-0 px-2">
                            <li className="breadcrumb-item"><Link to="/" className="font-14 text-muted text-decoration-none hover-text-danger transition"><i className="bi bi-house me-1"></i>خانه</Link></li>
                            <li className="breadcrumb-item active text-danger font-14 fw-bold" aria-current="page">درباره ما</li>
                        </ol>
                    </nav>
                </div>
            </section>

            <div className="container-fluid container-xl">
                <div className="bg-white rounded-5 shadow-sm border border-ui p-4 p-md-5 overflow-hidden animate-fade-in position-relative">
                    
                    <div className="position-absolute top-0 end-0 bg-danger opacity-5 rounded-circle translate-middle" style={{width:'400px', height:'400px', filter:'blur(40px)'}}></div>

                    <div className="row gy-5 align-items-center position-relative z-1">
                        <div className="col-lg-6 order-2 order-lg-1">
                            <div className="about-content pe-lg-4">
                                <h1 className="fw-900 h2 text-dark mb-4 heading-bar position-relative pb-3">{title}</h1>
                                <div 
                                    className="font-15 text-muted lh-lg text-justify text-editor-content"
                                    dangerouslySetInnerHTML={{ __html: content.replace(/\n/g, '<br/>') }}
                                ></div>
                                
                                <div className="mt-5 row g-3 text-center">
                                    <div className="col-6 col-sm-4">
                                        <div className="bg-light p-3 rounded-4 border border-light shadow-2xs">
                                            <i className="bi bi-shield-check text-success fs-3 mb-2 d-block"></i>
                                            <span className="font-12 fw-bold text-dark">تضمین اصالت</span>
                                        </div>
                                    </div>
                                    <div className="col-6 col-sm-4">
                                        <div className="bg-light p-3 rounded-4 border border-light shadow-2xs">
                                            <i className="bi bi-truck text-primary fs-3 mb-2 d-block"></i>
                                            <span className="font-12 fw-bold text-dark">ارسال سریع</span>
                                        </div>
                                    </div>
                                    <div className="col-12 col-sm-4">
                                        <div className="bg-light p-3 rounded-4 border border-light shadow-2xs">
                                            <i className="bi bi-emoji-smile text-warning fs-3 mb-2 d-block"></i>
                                            <span className="font-12 fw-bold text-dark">رضایت مشتری</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="col-lg-6 order-1 order-lg-2">
                            <div className="about-img-box text-center position-relative">
                                <div className="position-absolute w-100 h-100 bg-danger opacity-10 rounded-5 translate-middle-x top-0 start-50 rotate-3 z-0" style={{transform: 'scale(1.02)'}}></div>
                                <img 
                                    src={imageUrl} 
                                    alt={title} 
                                    className="img-fluid rounded-5 shadow-md w-100 object-fit-cover position-relative z-1 border border-ui transition" 
                                    style={{maxHeight: '400px'}}
                                    onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/about/rtl-theme.jpg'; }}
                                />
                            </div>
                        </div>
                    </div>

                </div>
            </div>

            <style jsx="true">{`
                .transition { transition: all 0.3s ease-in-out; }
                .shadow-2xs { box-shadow: 0 2px 8px rgba(0,0,0,0.02); }
                .heading-bar::after { content: ''; position: absolute; bottom: 0; right: 0; width: 70px; height: 4px; background-color: #ef4056; border-radius: 5px; }
                .about-img-box:hover img { transform: scale(1.01) translateY(-2px); }
                .text-editor-content p { margin-bottom: 1.5rem; }
                .animate-fade-in { animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
            `}</style>
        </main>
    );
};

export default AboutUsPage;