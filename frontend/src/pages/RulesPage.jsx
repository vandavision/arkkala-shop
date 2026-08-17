import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { getStaticPageSeo } from '../api/homeApi';
import { SiteContext } from '../context/SiteContext';
import SeoMeta from '../components/SeoMeta';

const RulesPage = () => {
    const { settings } = useContext(SiteContext);
    const [seoData, setSeoData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const meta = await getStaticPageSeo('RulesPage');
                setSeoData(meta);
            } catch (error) {
                console.error(error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, []);

    if (loading) {
        return (
            <div className="d-flex flex-column justify-content-center align-items-center min-vh-100 bg-light">
                <div className="spinner-border text-danger mb-3" style={{width: '3.5rem', height:'3.5rem', borderWidth: '0.25rem'}} role="status"></div>
            </div>
        );
    }

    return (
        <main className="rules-page bg-light min-vh-100 pb-5">
            <SeoMeta seoData={seoData} fallbackTitle={`شرایط و قوانین | ${settings?.site_name || 'فروشگاه'}`} />
            
            <section className="bread-crumb py-3 mb-5 bg-white shadow-sm border-bottom border-light">
                <div className="container-fluid container-xl">
                    <nav aria-label="breadcrumb">
                        <ol className="breadcrumb mb-0 px-2">
                            <li className="breadcrumb-item"><Link to="/" className="font-14 text-muted text-decoration-none hover-text-danger transition"><i className="bi bi-house me-1"></i>خانه</Link></li>
                            <li className="breadcrumb-item active text-danger font-14 fw-bold" aria-current="page">شرایط و قوانین</li>
                        </ol>
                    </nav>
                </div>
            </section>

            <div className="container-fluid container-xl">
                <div className="bg-white rounded-5 shadow-sm border border-ui p-4 p-md-5 position-relative overflow-hidden animate-fade-in">
                    <div className="position-absolute top-0 end-0 bg-danger opacity-5 rounded-circle translate-middle" style={{width:'300px', height:'300px', filter:'blur(40px)'}}></div>
                    
                    <div className="position-relative z-1">
                        <div className="text-center mb-5">
                            <div className="bg-danger bg-opacity-10 d-inline-flex p-3 rounded-circle mb-3">
                                <i className="bi bi-shield-check text-danger display-5"></i>
                            </div>
                            <h1 className="fw-900 h3 text-dark mb-2">شرایط و قوانین استفاده از سایت</h1>
                        </div>

                        <div className="row justify-content-center">
                            <div className="col-lg-10 col-xl-9">
                                <div className="policy-content font-15 text-dark lh-lg text-justify">
                                    <h4 className="fw-900 text-dark mb-4 mt-5 border-end border-danger border-4 pe-3">قوانین عمومی</h4>
                                    <p>توجه داشته باشید کلیه اصول و رویه‌های فروشگاه منطبق با قوانین جمهوری اسلامی ایران، قانون تجارت الکترونیک و قانون حمایت از حقوق مصرف کننده است.</p>
                                    
                                    <h4 className="fw-900 text-dark mb-4 mt-5 border-end border-danger border-4 pe-3">سیاست‌های حریم خصوصی</h4>
                                    <p>فروشگاه به اطلاعات خصوصی اشخاصى که از خدمات سایت استفاده می‏‌کنند، احترام گذاشته و از آن محافظت می‏‌کند. ما متعهد می‌شویم در حد توان از حریم شخصی شما دفاع کنیم.</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <style jsx="true">{`
                .transition { transition: all 0.3s ease-in-out; }
                .animate-fade-in { animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
                .policy-content p { margin-bottom: 1.5rem; color: #495057; }
            `}</style>
        </main>
    );
};

export default RulesPage;