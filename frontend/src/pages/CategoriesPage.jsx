// frontend/src/pages/CategoriesPage.jsx
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

import { getCategoryTree } from '../api/searchApi';
import { getStaticPageSeo } from '../api/homeApi';
import SeoMeta from '../components/SeoMeta';

const resolveImageUrl = (url) => {
    if (!url) return null;
    let finalUrl = url;
    if (typeof finalUrl !== 'string') {
        if (finalUrl.url) finalUrl = finalUrl.url;
        else if (finalUrl.image) finalUrl = finalUrl.image;
        else return null;
    }
    if (typeof finalUrl !== 'string') return null;

    if (finalUrl.startsWith('http') || finalUrl.startsWith('data:') || finalUrl.startsWith('blob:')) {
        return finalUrl;
    }
    
    let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    baseUrl = baseUrl.replace(/\/api\/?$/, '');
    if (baseUrl.endsWith('/')) {
        baseUrl = baseUrl.slice(0, -1);
    }
    
    let path = finalUrl;
    if (!path.startsWith('/')) {
        path = '/media/' + path;
    } else if (!path.startsWith('/media/')) {
        path = '/media' + path;
    }
    
    return `${baseUrl}${path}`;
};

const CategoriesPage = () => {
    const [categories, setCategories] = useState([]);
    const [seoData, setSeoData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const [data, meta] = await Promise.all([
                    getCategoryTree(),
                    getStaticPageSeo('CategoriesPage')
                ]);
                setCategories(data || []);
                setSeoData(meta);
            } catch (error) {
                console.error("Error fetching categories:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchCategories();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, []);

    if (loading) {
        return (
            <div className="d-flex flex-column justify-content-center align-items-center min-vh-100 bg-light">
                <div className="spinner-border text-danger mb-3" style={{width: '3rem', height:'3rem', borderWidth: '0.25rem'}} role="status"></div>
                <h6 className="fw-bold text-muted animate-pulse font-14">در حال دریافت دسته‌بندی‌ها...</h6>
            </div>
        );
    }

    return (
        <main className="categories-page pb-5 bg-light min-vh-100">
            <SeoMeta seoData={seoData} fallbackTitle="دسته‌بندی کالاها" />

            <section className="bread-crumb py-3 mb-4 bg-white shadow-sm border-bottom border-light">
                <div className="container-fluid container-xl">
                    <nav aria-label="breadcrumb">
                        <ol className="breadcrumb mb-0 px-2">
                            <li className="breadcrumb-item"><Link to="/" className="font-13 text-muted text-decoration-none hover-text-danger transition"><i className="bi bi-house me-1"></i>خانه</Link></li>
                            <li className="breadcrumb-item"><Link to="/shop" className="font-13 text-muted text-decoration-none hover-text-danger transition">فروشگاه</Link></li>
                            <li className="breadcrumb-item active text-danger font-13 fw-bold" aria-current="page">دسته‌بندی کالاها</li>
                        </ol>
                    </nav>
                </div>
            </section>

            <div className="container-fluid container-xl">
                <div className="d-flex flex-column flex-md-row align-items-center justify-content-between mb-4 bg-white p-3 p-md-4 rounded-4 shadow-sm border border-ui">
                    <div className="d-flex align-items-center gap-3">
                        <div className="bg-danger bg-opacity-10 p-3 rounded-circle d-flex align-items-center justify-content-center">
                            <i className="bi bi-grid-1x2-fill text-danger fs-4"></i>
                        </div>
                        <div>
                            <h1 className="fw-900 h5 text-dark mb-1">دسته‌بندی <span className="text-danger">محصولات</span></h1>
                            <p className="text-muted font-12 m-0">تمامی محصولات فروشگاه در یک نگاه</p>
                        </div>
                    </div>
                </div>

                {categories.length > 0 ? (
                    <div className="row row-cols-1 row-cols-sm-2 row-cols-lg-3 row-cols-xl-4 g-3 g-md-4">
                        {categories.map((cat, index) => {
                            const catImgRaw = cat.image || cat.image_url || cat.icon || cat.logo;
                            const catImg = catImgRaw ? resolveImageUrl(catImgRaw) : '/assets/image/category/kalaye-degital.png';

                            return (
                                <div className="col animate-fade-in" key={cat.uuid || cat.id} style={{ animationDelay: `${index * 0.05}s` }}>
                                    <div className="bg-white rounded-4 shadow-sm border border-ui p-4 h-100 d-flex flex-column hover-shadow transition hover-lift category-card">
                                        
                                        {/* Header Card */}
                                        <div className="d-flex align-items-center gap-3 mb-3 pb-3 border-bottom border-light">
                                            <div className="bg-light rounded-circle d-flex align-items-center justify-content-center p-2 border border-ui transition img-wrapper flex-shrink-0" style={{width: '65px', height: '65px'}}>
                                                <img 
                                                    src={catImg} 
                                                    alt={cat.title} 
                                                    className="img-fluid object-fit-contain w-100 h-100 transition" 
                                                    onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/category/kalaye-degital.png'; }}
                                                />
                                            </div>
                                            <div className="flex-grow-1 overflow-hidden">
                                                <Link to={`/category/${cat.slug}`} className="text-decoration-none text-dark hover-text-danger transition d-block mb-1">
                                                    <h2 className="font-15 fw-900 m-0 text-truncate">{cat.title}</h2>
                                                </Link>
                                                {cat.children && cat.children.length > 0 && (
                                                    <span className="font-11 text-muted fw-bold px-2 py-1 bg-light rounded-pill border border-light d-inline-block mt-1">
                                                        {cat.children.length} گروه زیرمجموعه
                                                    </span>
                                                )}
                                            </div>
                                        </div>

                                        {/* Subcategories Link */}
                                        <div className="sub-cats d-flex flex-column gap-2 flex-grow-1 mb-3">
                                            {cat.children && cat.children.length > 0 && (
                                                <>
                                                    <ul className="list-unstyled p-0 m-0 d-flex flex-column gap-2">
                                                        {cat.children.slice(0, 3).map(sub => (
                                                            <li key={sub.uuid || sub.id}>
                                                                <Link to={`/category/${sub.slug}`} className="text-muted font-13 text-decoration-none hover-text-danger transition d-flex align-items-center gap-2 sub-cat-link">
                                                                    <i className="bi bi-chevron-left font-10 opacity-50 transition"></i> <span className="text-truncate">{sub.title}</span>
                                                                </Link>
                                                            </li>
                                                        ))}
                                                    </ul>
                                                    
                                                    {cat.children.length > 3 && (
                                                        <div className="mt-1">
                                                            <Link to={`/category/${cat.slug}`} className="font-12 fw-bold text-danger text-decoration-none transition hover-text-dark">
                                                                و {cat.children.length - 3} دسته دیگر...
                                                            </Link>
                                                        </div>
                                                    )}
                                                </>
                                            )}
                                        </div>

                                        {/* Preview Products Thumbnail */}
                                        {cat.products && cat.products.length > 0 ? (
                                            <div className="mt-auto pt-3 border-top border-light border-dashed">
                                                <span className="font-11 text-muted mb-2 d-block fw-bold"><i className="bi bi-star-fill text-warning me-1"></i> محبوب‌ترین‌ها:</span>
                                                <div className="d-flex align-items-center flex-wrap gap-2">
                                                    {cat.products.slice(0, 4).map(prod => {
                                                        let prodImgRaw = prod.image_url || prod.image || prod.thumbnail;
                                                        if (!prodImgRaw && prod.gallery && prod.gallery.length > 0) {
                                                            prodImgRaw = prod.gallery[0].url || prod.gallery[0].image;
                                                        }
                                                        const prodImg = prodImgRaw ? resolveImageUrl(prodImgRaw) : '/assets/image/product/product-no-bg.png';
                                                        
                                                        return (
                                                            <Link key={prod.uuid || prod.id} to={`/product/${prod.slug}`} className="bg-white border border-ui rounded-3 p-1 hover-lift transition shadow-sm product-thumb" title={prod.title}>
                                                                <img src={prodImg} className="w-100 h-100 object-fit-contain rounded-2" alt={prod.title} onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/product/product-no-bg.png'; }}/>
                                                            </Link>
                                                        );
                                                    })}
                                                    
                                                    {cat.products.length > 4 && (
                                                        <Link to={`/category/${cat.slug}`} className="bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25 rounded-3 p-1 hover-lift transition d-flex align-items-center justify-content-center font-11 fw-bold text-decoration-none shadow-sm product-thumb">
                                                            <i className="bi bi-three-dots"></i>
                                                        </Link>
                                                    )}
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="mt-auto pt-3 border-top border-light border-dashed">
                                                <Link to={`/category/${cat.slug}`} className="font-12 fw-bold text-danger text-decoration-none transition hover-text-dark d-flex align-items-center gap-1">
                                                    مشاهده کالاهای این دسته <i className="bi bi-arrow-left"></i>
                                                </Link>
                                            </div>
                                        )}

                                    </div>
                                </div>
                            );
                        })}
                    </div>
                ) : (
                    <div className="text-center py-5 my-5 bg-white rounded-4 shadow-sm border border-ui">
                        <i className="bi bi-box-seam text-muted opacity-25 mb-4 d-block" style={{fontSize: '4rem'}}></i>
                        <h4 className="text-dark fw-bold mb-3 font-16">هیچ دسته‌بندی یافت نشد!</h4>
                        <Link to="/shop" className="btn btn-danger rounded-pill px-4 py-2 mt-2 shadow-sm hover-lift fw-bold font-13">
                            مشاهده تمام محصولات
                        </Link>
                    </div>
                )}
            </div>

            <style jsx="true">{`
                .animate-pulse { animation: pulse 2s infinite; }
                @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
                
                .animate-fade-in { 
                    opacity: 0; 
                    transform: translateY(15px);
                    animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards; 
                }
                @keyframes fadeIn { to { opacity: 1; transform: translateY(0); } }

                .transition { transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); }
                .hover-text-danger:hover { color: #ef4056 !important; }
                .hover-text-dark:hover { color: #212529 !important; }
                
                .hover-lift { transition: transform 0.3s ease, box-shadow 0.3s; }
                .hover-lift:hover { transform: translateY(-4px); }
                
                .hover-shadow:hover { box-shadow: 0 12px 24px rgba(239, 64, 86, 0.08) !important; border-color: rgba(239, 64, 86, 0.2) !important; }

                .border-dashed { border-style: dashed !important; border-color: #dee2e6 !important;}

                .category-card .img-wrapper img {
                    transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                }

                .category-card:hover .img-wrapper {
                    background-color: #fff !important;
                    border-color: #ef4056 !important;
                    box-shadow: 0 4px 10px rgba(239, 64, 86, 0.15) !important;
                }

                .category-card:hover .img-wrapper img {
                    transform: scale(1.15) rotate(-3deg);
                }

                .sub-cat-link:hover i {
                    transform: translateX(-4px);
                    opacity: 1 !important;
                    color: #ef4056;
                }

                .product-thumb { width: 45px; height: 45px; }
                @media (min-width: 1400px) {
                    .product-thumb { width: 50px; height: 50px; }
                }
            `}</style>
        </main>
    );
};

export default CategoriesPage;