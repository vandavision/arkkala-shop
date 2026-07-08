import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { getFaqsList, getStaticPageSeo } from '../api/homeApi';
import { SiteContext } from '../context/SiteContext';
import SeoMeta from '../components/SeoMeta';

const FaqPage = () => {
    const { settings } = useContext(SiteContext);
    const [faqs, setFaqs] = useState([]);
    const [filteredFaqs, setFilteredFaqs] = useState([]);
    const [seoData, setSeoData] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [loading, setLoading] = useState(true);
    const [activeIndex, setActiveIndex] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [faqData, meta] = await Promise.all([
                    getFaqsList(),
                    getStaticPageSeo('FaqPage')
                ]);
                setFaqs(faqData || []);
                setFilteredFaqs(faqData || []);
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

    useEffect(() => {
        if (!searchQuery.trim()) {
            setFilteredFaqs(faqs);
        } else {
            const query = searchQuery.toLowerCase();
            const filtered = faqs.filter(f => 
                f.question.toLowerCase().includes(query) || 
                f.answer.toLowerCase().includes(query)
            );
            setFilteredFaqs(filtered);
        }
        setActiveIndex(null);
    }, [searchQuery, faqs]);

    const toggleAccordion = (index) => {
        setActiveIndex(activeIndex === index ? null : index);
    };

    if (loading) {
        return (
            <div className="d-flex flex-column justify-content-center align-items-center min-vh-100 bg-light">
                <div className="spinner-border text-danger mb-3" style={{width: '3.5rem', height:'3.5rem', borderWidth: '0.25rem'}} role="status"></div>
                <h5 className="fw-bold text-muted font-14">در حال بارگذاری سوالات متداول...</h5>
            </div>
        );
    }

    return (
        <main className="faq-page pb-5 bg-light min-vh-100">
            <SeoMeta seoData={seoData} fallbackTitle="سوالات متداول" />
            
            <section className="bread-crumb py-3 mb-4 bg-white shadow-sm border-bottom border-light">
                <div className="container-fluid container-xl">
                    <nav aria-label="breadcrumb">
                        <ol className="breadcrumb mb-0 px-2">
                            <li className="breadcrumb-item"><Link to="/" className="font-14 text-muted text-decoration-none hover-text-danger transition"><i className="bi bi-house me-1"></i>خانه</Link></li>
                            <li className="breadcrumb-item active text-danger font-14 fw-bold" aria-current="page">سوالات متداول</li>
                        </ol>
                    </nav>
                </div>
            </section>

            <div className="container-fluid container-xl">
                <div className="row justify-content-center">
                    <div className="col-12 col-lg-9 col-xl-8">
                        
                        <div className="text-center mb-5 animate-fade-in">
                            <div className="bg-danger bg-opacity-10 d-inline-flex p-3 rounded-circle mb-3">
                                <i className="bi bi-patch-question text-danger display-5"></i>
                            </div>
                            <h1 className="fw-900 h3 text-dark mb-2">پاسخ به سوالات شما</h1>
                            <p className="text-muted font-14">اگر سوالی دارید، احتمالاً پاسخ آن را در زیر پیدا خواهید کرد.</p>
                            
                            <div className="mt-4 max-w-500 mx-auto position-relative shadow-sm rounded-pill overflow-hidden border border-ui bg-white p-1">
                                <input 
                                    type="text" 
                                    className="form-control border-0 py-3 px-4 font-13 text-dark fw-bold shadow-none" 
                                    placeholder="جستجوی موضوع یا کلمه کلیدی..." 
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                />
                                <span className="position-absolute end-0 top-50 translate-middle-y me-4 text-muted"><i className="bi bi-search fs-5"></i></span>
                            </div>
                        </div>

                        {filteredFaqs.length > 0 ? (
                            <div className="accordion d-flex flex-column gap-3">
                                {filteredFaqs.map((faq, index) => {
                                    const isOpen = activeIndex === index;
                                    return (
                                        <div className="accordion-item border border-ui rounded-4 overflow-hidden shadow-sm bg-white transition animate-fade-in" key={faq.uuid || faq.id}>
                                            <h2 className="accordion-header m-0">
                                                <button 
                                                    type="button" 
                                                    className={`accordion-button shadow-none bg-white font-14 fw-bold py-4 px-4 text-start d-flex justify-content-between align-items-center w-100 border-0 ${isOpen ? 'text-danger' : 'text-dark'}`}
                                                    onClick={() => toggleAccordion(index)}
                                                >
                                                    <span className="pe-3">{faq.question}</span>
                                                    <i className={`bi bi-chevron-down transition fs-5 flex-shrink-0 ${isOpen ? 'rotate-180 text-danger' : 'text-muted'}`}></i>
                                                </button>
                                            </h2>
                                            <div className={`accordion-collapse overflow-hidden transition-all ${isOpen ? 'show-panel' : 'hide-panel'}`}>
                                                <div className="accordion-body px-4 pb-4 pt-2 text-muted font-14 lh-lg border-top border-light text-justify">
                                                    {faq.answer}
                                                </div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        ) : (
                            <div className="text-center py-5 bg-white rounded-4 shadow-sm border border-ui">
                                <i className="bi bi-search-heart display-1 text-muted opacity-25 d-block mb-3"></i>
                                <h5 className="text-dark fw-bold mb-2">نتیجه‌ای یافت نشدی</h5>
                                <p className="text-muted font-13">هیچ سوالی متناسب با عبارت جستجو شده پیدا نشد.</p>
                                <button className="btn btn-danger rounded-pill px-4 py-2 mt-2 font-13 fw-bold shadow-sm hover-lift" onClick={() => setSearchQuery('')}>مشاهده همه سوالات</button>
                            </div>
                        )}

                    </div>
                </div>
            </div>

            <style jsx="true">{`
                .transition { transition: all 0.3s ease-in-out; }
                .max-w-500 { max-width: 500px; }
                .rotate-180 { transform: rotate(180deg); }
                .hover-lift { transition: transform 0.2s ease; }
                .hover-lift:hover { transform: translateY(-2px); }
                .hide-panel { max-height: 0; opacity: 0; transition: all 0.3s ease; }
                .show-panel { max-height: 1000px; opacity: 1; transition: all 0.4s ease; }
                .animate-fade-in { animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
            `}</style>
        </main>
    );
};

export default FaqPage;