import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getBrandsList } from '../api/searchApi';
import { getStaticPageSeo } from '../api/homeApi';
import SeoMeta from '../components/SeoMeta';

const resolveImageUrl = (url) => {
    if (!url) return '/assets/image/brand/brand1-1.png';
    if (typeof url !== 'string') {
        if (url.url) url = url.url;
        else return '/assets/image/brand/brand1-1.png';
    }
    if (url.startsWith('http') || url.startsWith('data:') || url.startsWith('blob:')) return url;
    
    let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    baseUrl = baseUrl.replace(/\/api\/?$/, '').replace(/\/$/, '');
    
    let path = url.startsWith('/') ? url : `/${url}`;
    if (!path.startsWith('/media/')) {
        path = `/media${path}`;
    }
    
    return `${baseUrl}${path}`;
};

const BrandsPage = () => {
    const [brands, setBrands] = useState([]);
    const [filteredBrands, setFilteredBrands] = useState([]);
    const [seoData, setSeoData] = useState(null);
    const [searchQuery, setSearchQuery] = useState('');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchBrands = async () => {
            try {
                const [data, meta] = await Promise.all([
                    getBrandsList(),
                    getStaticPageSeo('BrandsPage')
                ]);
                const brandsData = data.results || data || [];
                setBrands(brandsData);
                setFilteredBrands(brandsData);
                setSeoData(meta);
            } catch (error) {
                console.error("Error fetching brands:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchBrands();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, []);

    useEffect(() => {
        if (!searchQuery || searchQuery.trim() === '') {
            setFilteredBrands(brands);
        } else {
            const normalizeText = (text) => {
                if (!text) return '';
                return text.toString().toLowerCase().replace(/ي/g, 'ی').replace(/ك/g, 'ک');
            };

            const query = normalizeText(searchQuery.trim());

            const filtered = brands.filter(brand => {
                const titleMatch = normalizeText(brand.title).includes(query);
                const slugMatch = normalizeText(brand.slug).includes(query);
                
                return titleMatch || slugMatch;
            });
            
            setFilteredBrands(filtered);
        }
    }, [searchQuery, brands]);

    if (loading) {
        return (
            <div className="d-flex flex-column justify-content-center align-items-center min-vh-100 bg-light">
                <div className="spinner-border text-danger mb-4" style={{width: '4rem', height:'4rem', borderWidth: '0.3rem'}} role="status"></div>
                <h5 className="fw-900 text-dark animate-pulse tracking-wide">در حال بارگذاری برندهای برتر...</h5>
            </div>
        );
    }

    return (
        <main className="brands-page pb-5 bg-light min-vh-100">
            <SeoMeta seoData={seoData} fallbackTitle="برندهای برتر" />

            <section className="bread-crumb py-3 mb-4 bg-white shadow-sm border-bottom border-light position-relative z-3">
                <div className="container-fluid container-xl">
                    <nav aria-label="breadcrumb">
                        <ol className="breadcrumb mb-0 px-2">
                            <li className="breadcrumb-item"><Link to="/" className="font-14 text-muted text-decoration-none hover-text-danger transition"><i className="bi bi-house-door-fill me-1"></i>خانه</Link></li>
                            <li className="breadcrumb-item"><Link to="/shop" className="font-14 text-muted text-decoration-none hover-text-danger transition">فروشگاه</Link></li>
                            <li className="breadcrumb-item active text-danger font-14 fw-bold" aria-current="page">برندهای برتر</li>
                        </ol>
                    </nav>
                </div>
            </section>

            <div className="container-fluid container-xl">
                
                <div className="brands-hero-section position-relative rounded-5 overflow-hidden mb-5 shadow-sm border border-light">
                    <div className="position-absolute top-0 start-0 w-100 h-100 z-0 bg-hero-pattern"></div>
                    <div className="position-absolute top-0 end-0 bg-danger rounded-circle blur-blob translate-middle opacity-25" style={{ width: '300px', height: '300px' }}></div>
                    <div className="position-absolute bottom-0 start-0 bg-warning rounded-circle blur-blob translate-middle opacity-25" style={{ width: '250px', height: '250px' }}></div>

                    <div className="row align-items-center justify-content-center position-relative z-1 p-5 text-center min-h-300">
                        <div className="col-12 col-md-8 col-lg-6">
                            <div className="d-inline-flex align-items-center justify-content-center bg-white rounded-pill px-4 py-2 mb-4 shadow-sm">
                                <i className="bi bi-stars text-warning fs-5 me-2"></i>
                                <span className="font-14 fw-bold text-dark">اصالت و کیفیت تضمین‌شده</span>
                            </div>
                            
                            <h1 className="fw-900 text-dark display-6 mb-3 lh-base">
                                برترین <span className="text-danger position-relative d-inline-block">برندهای<svg className="position-absolute bottom-0 start-0 w-100 translate-middle-y" style={{ zIndex: -1, marginBottom: '-8px' }} height="12" viewBox="0 0 200 12" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M2 10C68 -2 134 -2 198 10" stroke="#ffc107" strokeWidth="4" strokeLinecap="round"/></svg></span> جهان در آرک کالا
                            </h1>
                            <p className="text-muted font-15 mb-5 lh-lg px-md-4">
                                مجموعه‌ای بی‌نظیر از محصولات اورجینال محبوب‌ترین برندهای داخلی و بین‌المللی را با اطمینان کامل خریداری کنید.
                            </p>

                            <div className="search-glass-wrapper mx-auto position-relative shadow-lg rounded-pill p-1 bg-white bg-opacity-75 backdrop-blur">
                                <input 
                                    type="text" 
                                    className="form-control py-3 px-4 rounded-pill bg-white border-0 shadow-none font-14 text-dark fw-bold" 
                                    placeholder="دنبال چه برندی هستید؟ (مثلا: اپل، سونی...)"
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                />
                                <div className="position-absolute end-0 top-50 translate-middle-y me-2">
                                    <button className="btn btn-danger rounded-circle d-flex align-items-center justify-content-center shadow-sm" style={{ width: '45px', height: '45px' }}>
                                        <i className="bi bi-search fs-5 text-white"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {filteredBrands.length > 0 ? (
                    <div className="row row-cols-2 row-cols-sm-3 row-cols-md-4 row-cols-lg-5 row-cols-xl-6 g-3 g-md-4 pb-4">
                        {filteredBrands.map((brand, index) => (
                            <div 
                                className="col animate-staggered-fade" 
                                key={brand.uuid}
                                style={{ animationDelay: `${index * 0.05}s` }}
                            >
                                <Link to={`/shop?brands=${brand.slug}`} className="text-decoration-none d-block h-100">
                                    <div className="brand-luxury-card bg-white rounded-4 p-4 d-flex flex-column align-items-center text-center h-100 position-relative">
                                        
                                        <div className="brand-logo-circle mb-4 d-flex align-items-center justify-content-center bg-white rounded-circle position-relative z-1 transition-all">
                                            <div className="brand-logo-inner d-flex align-items-center justify-content-center w-100 h-100 rounded-circle bg-light p-3 transition-all">
                                                <img 
                                                    src={resolveImageUrl(brand.logo)} 
                                                    alt={brand.title} 
                                                    className="img-fluid brand-img grayscale transition-all"
                                                    onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/brand/brand1-1.png'; }}
                                                />
                                            </div>
                                        </div>

                                        <h3 className="font-15 fw-900 text-dark mb-2 text-truncate w-100 brand-title transition-all position-relative z-1">{brand.title}</h3>
                                        
                                        <div className="mt-auto pt-2 w-100 position-relative z-1">
                                            <span className="font-12 fw-bold text-muted bg-light rounded-pill px-3 py-1 d-inline-flex align-items-center justify-content-center gap-1 transition-all brand-badge">
                                                <i className="bi bi-box-seam"></i> {brand.product_count || 0} کالا
                                            </span>
                                        </div>

                                        <div className="brand-card-hover-bg position-absolute bottom-0 start-0 w-100 h-0 bg-danger bg-opacity-10 rounded-4 transition-all z-0"></div>
                                    </div>
                                </Link>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-5 bg-white rounded-5 shadow-sm border border-ui mt-4 mb-5">
                        <div className="mb-4 position-relative d-inline-block">
                            <div className="bg-light rounded-circle d-flex align-items-center justify-content-center mx-auto" style={{ width: '120px', height: '120px' }}>
                                <i className="bi bi-emoji-frown fs-1 text-muted opacity-50"></i>
                            </div>
                            <div className="position-absolute bottom-0 end-0 bg-white rounded-circle p-1 shadow-sm translate-middle-x mb-2 me-2">
                                <div className="bg-danger rounded-circle d-flex align-items-center justify-content-center" style={{ width: '30px', height: '30px' }}>
                                    <i className="bi bi-search text-white font-12"></i>
                                </div>
                            </div>
                        </div>
                        <h4 className="text-dark fw-900 mb-3 fs-5">برندی با این نام پیدا نکردیم!</h4>
                        <p className="text-muted font-14 mb-4">لطفاً املای کلمه را بررسی کنید یا عبارت دیگری بنویسید.</p>
                        <button className="btn btn-dark rounded-pill px-5 py-2 font-14 fw-bold shadow-sm hover-lift" onClick={() => setSearchQuery('')}>
                            مشاهده تمام برندها <i className="bi bi-arrow-counterclockwise ms-1 align-middle"></i>
                        </button>
                    </div>
                )}
            </div>

            <style jsx="true">{`
                .animate-pulse { animation: pulse 2s infinite; }
                @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
                
                .animate-staggered-fade {
                    opacity: 0;
                    transform: translateY(30px);
                    animation: fadeUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                }
                @keyframes fadeUp { to { opacity: 1; transform: translateY(0); } }

                .transition-all { transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); }
                .tracking-wide { letter-spacing: 0.5px; }
                .min-h-300 { min-height: 320px; }

                .brands-hero-section {
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                }
                .bg-hero-pattern {
                    background-image: radial-gradient(#adb5bd 1px, transparent 1px);
                    background-size: 24px 24px;
                    opacity: 0.3;
                }
                .blur-blob {
                    filter: blur(60px);
                    animation: float 10s infinite ease-in-out alternate;
                }
                @keyframes float { 0% { transform: translate(-50%, -50%) scale(1); } 100% { transform: translate(-45%, -55%) scale(1.1); } }
                
                .backdrop-blur { backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); }
                .search-glass-wrapper input:focus {
                    background-color: #fff !important;
                    box-shadow: none !important;
                }

                .brand-luxury-card {
                    border: 1px solid #f0f0f1;
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.02);
                    transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
                    overflow: hidden;
                }

                .brand-logo-circle {
                    width: 100px;
                    height: 100px;
                    border: 1px solid #f5f5f6;
                    box-shadow: 0 4px 10px rgba(0,0,0,0.03);
                }

                .brand-img {
                    max-height: 100%;
                    max-width: 100%;
                    object-fit: contain;
                    filter: grayscale(100%);
                    opacity: 0.6;
                }

                .brand-luxury-card:hover {
                    transform: translateY(-8px);
                    box-shadow: 0 20px 40px rgba(239, 64, 86, 0.12) !important;
                    border-color: rgba(239, 64, 86, 0.2) !important;
                }

                .brand-luxury-card:hover .brand-logo-circle {
                    box-shadow: 0 15px 25px rgba(239, 64, 86, 0.15) !important;
                    border-color: #ef4056 !important;
                    transform: scale(1.05);
                }

                .brand-luxury-card:hover .brand-logo-inner {
                    background-color: #fff !important;
                }

                .brand-luxury-card:hover .brand-img {
                    filter: grayscale(0%);
                    opacity: 1;
                    transform: scale(1.15);
                }

                .brand-luxury-card:hover .brand-title {
                    color: #ef4056 !important;
                }

                .brand-luxury-card:hover .brand-badge {
                    background-color: #ef4056 !important;
                    color: white !important;
                    border-color: #ef4056 !important;
                    box-shadow: 0 4px 10px rgba(239, 64, 86, 0.3);
                }

                .brand-luxury-card:hover .brand-card-hover-bg {
                    height: 100%;
                    opacity: 0.5;
                }

                .hover-lift { transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), box-shadow 0.3s; }
                .hover-lift:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important; }
            `}</style>
        </main>
    );
};

export default BrandsPage;