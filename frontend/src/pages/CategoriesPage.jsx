import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getCategoryTree } from '../api/searchApi';
import ProductCard from '../components/ProductCard';

const resolveImageUrl = (url) => {
    if (!url) return null;
    if (typeof url !== 'string') {
        if (url.url) url = url.url;
        else return null;
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

const CategoriesPage = () => {
    const [categories, setCategories] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const data = await getCategoryTree();
                setCategories(data);
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
                <div className="spinner-border text-danger mb-3" style={{width: '3.5rem', height:'3.5rem', borderWidth: '0.25rem'}} role="status"></div>
                <h6 className="fw-bold text-muted animate-pulse">در حال دریافت دسته‌بندی‌ها...</h6>
            </div>
        );
    }

    return (
        <main className="categories-page pb-5 bg-light min-vh-100">
            <section className="bread-crumb py-3 mb-4 bg-white shadow-sm border-bottom border-light">
                <div className="container-fluid container-xl">
                    <nav aria-label="breadcrumb">
                        <ol className="breadcrumb mb-0 px-2">
                            <li className="breadcrumb-item"><Link to="/" className="font-14 text-muted text-decoration-none hover-text-danger transition"><i className="bi bi-house me-1"></i>خانه</Link></li>
                            <li className="breadcrumb-item"><Link to="/shop" className="font-14 text-muted text-decoration-none hover-text-danger transition">فروشگاه</Link></li>
                            <li className="breadcrumb-item active text-danger font-14 fw-bold" aria-current="page">دسته‌بندی کالاها</li>
                        </ol>
                    </nav>
                </div>
            </section>

            <div className="container-fluid container-xl">
                <div className="d-flex flex-column flex-md-row align-items-center justify-content-between mb-5 bg-white p-4 rounded-4 shadow-sm border border-ui">
                    <div className="d-flex align-items-center gap-3">
                        <div className="bg-danger bg-opacity-10 p-3 rounded-circle d-flex align-items-center justify-content-center">
                            <i className="bi bi-grid-1x2-fill text-danger fs-3"></i>
                        </div>
                        <div>
                            <h1 className="fw-900 h4 text-dark mb-2">دسته‌بندی <span className="text-danger">کالاها</span></h1>
                            <p className="text-muted font-13 m-0">تمامی محصولات فروشگاه بر اساس گروه‌های تخصصی</p>
                        </div>
                    </div>
                </div>

                {categories.length > 0 ? (
                    <div className="d-flex flex-column gap-5">
                        {categories.map((cat) => (
                            <section className="category-mega-block animate-fade-in" key={cat.uuid}>
                                <div className="bg-white rounded-4 shadow-sm border border-ui p-4 p-md-5 position-relative overflow-hidden">
                                    
                                    <div className="d-flex flex-column flex-md-row align-items-md-center justify-content-between mb-5 pb-4 border-bottom border-light position-relative z-1">
                                        <div className="d-flex align-items-center gap-3 mb-4 mb-md-0">
                                            <div className="cat-parent-icon bg-light rounded-4 d-flex align-items-center justify-content-center border border-ui shadow-sm p-2" style={{ width: '85px', height: '85px' }}>
                                                <img 
                                                    src={resolveImageUrl(cat.image || cat.icon || cat.logo) || '/assets/image/category/kalaye-degital.png'} 
                                                    alt={cat.title} 
                                                    className="img-fluid object-fit-contain w-100 h-100" 
                                                    onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/category/kalaye-degital.png'; }}
                                                />
                                            </div>
                                            <div>
                                                <h2 className="h4 fw-900 text-dark mb-2">{cat.title}</h2>
                                                <span className="badge bg-light text-muted border border-ui px-3 py-2 font-12 fw-bold rounded-pill">
                                                    {cat.children?.length || 0} گروه کالایی
                                                </span>
                                            </div>
                                        </div>
                                        <div className="text-end">
                                            <Link to={`/category/${cat.slug}`} className="btn btn-outline-danger rounded-pill px-4 py-2 font-13 fw-bold shadow-sm hover-bg-danger transition d-inline-flex align-items-center gap-2">
                                                مشاهده همه کالاهای این دسته <i className="bi bi-arrow-left"></i>
                                            </Link>
                                        </div>
                                    </div>

                                    <div className="position-relative z-1 mb-4">
                                        {cat.children && cat.children.length > 0 ? (
                                            <div className="row gy-5 gx-2 gx-md-4">
                                                {cat.children.map(sub => {
                                                    const subImg = resolveImageUrl(sub.image || sub.icon || sub.logo);
                                                    return (
                                                        <div className="col-4 col-sm-3 col-md-3 col-lg-2" key={sub.uuid}>
                                                            <Link to={`/category/${sub.slug}`} className="text-decoration-none sub-cat-card d-block text-center">
                                                                <div className="sub-cat-img-box mx-auto mb-3 d-flex align-items-center justify-content-center transition shadow-sm position-relative" style={{ width: '100px', height: '100px' }}>
                                                                    {subImg ? (
                                                                        <img 
                                                                            src={subImg} 
                                                                            alt={sub.title} 
                                                                            className="img-fluid p-3 transition position-relative z-2" 
                                                                            style={{width: '100%', height:'100%', objectFit:'contain'}} 
                                                                        />
                                                                    ) : (
                                                                        <i className="bi bi-ui-radios-grid text-muted fs-2 transition position-relative z-2"></i>
                                                                    )}
                                                                </div>
                                                                <h4 className="font-13 fw-bold text-dark transition sub-cat-title lh-base px-1 m-0 text-overflow-2">{sub.title}</h4>
                                                            </Link>
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        ) : (
                                            <div className="alert bg-light border-light text-center rounded-3 py-4 m-0 d-flex flex-column align-items-center justify-content-center">
                                                <i className="bi bi-folder-x fs-1 text-muted opacity-25 mb-2"></i>
                                                <span className="font-13 text-muted fw-bold">زیردسته‌ای برای این گروه ثبت نشده است.</span>
                                            </div>
                                        )}
                                    </div>

                                    {cat.products && cat.products.length > 0 && (
                                        <div className="mt-5 pt-4 border-top border-light position-relative z-1">
                                            <div className="d-flex align-items-center justify-content-between mb-4">
                                                <h4 className="font-16 fw-bold text-dark m-0">
                                                    <i className="bi bi-star-fill text-warning me-2"></i>محبوب‌ترین‌های {cat.title}
                                                </h4>
                                                <Link to={`/category/${cat.slug}`} className="font-13 text-danger text-decoration-none fw-bold hover-text-dark transition">
                                                    نمایش همه
                                                </Link>
                                            </div>
                                            <div className="row gy-4 gx-3">
                                                {cat.products.map(prod => (
                                                    <div className="col-12 col-sm-6 col-lg-3" key={prod.uuid}>
                                                        <ProductCard product={prod} />
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )}

                                </div>
                            </section>
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-5 bg-white rounded-4 shadow-sm border border-ui">
                        <div className="mb-4">
                            <i className="bi bi-box-seam fs-1 text-muted opacity-25" style={{fontSize: '5rem'}}></i>
                        </div>
                        <h4 className="text-muted fw-bold mb-3">هیچ دسته‌بندی در سایت یافت نشد!</h4>
                        <Link to="/shop" className="btn btn-danger rounded-pill px-5 py-3 mt-3 shadow-sm hover-lift fw-bold">
                            مشاهده تمام محصولات فروشگاه
                        </Link>
                    </div>
                )}
            </div>

            <style jsx="true">{`
                .animate-pulse { animation: pulse 2s infinite; }
                @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
                
                .animate-fade-in { animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }

                .transition { transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); }
                .hover-text-danger:hover { color: #ef4056 !important; }
                .hover-text-dark:hover { color: #212529 !important; }
                .hover-lift { transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), box-shadow 0.3s; }
                .hover-lift:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important; }
                
                .text-overflow-2 { overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }

                .sub-cat-card .sub-cat-img-box {
                    background-color: #f8f9fa;
                    border: 2px solid transparent;
                    border-radius: 50%;
                }
                
                .sub-cat-card:hover .sub-cat-img-box {
                    background-color: #fff;
                    border-color: #ef4056;
                    box-shadow: 0 12px 25px rgba(239, 64, 86, 0.15) !important;
                    transform: translateY(-8px);
                }

                .sub-cat-card .sub-cat-img-box img,
                .sub-cat-card .sub-cat-img-box i {
                    transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), color 0.3s;
                }

                .sub-cat-card:hover .sub-cat-img-box img {
                    transform: scale(1.15) rotate(3deg);
                }
                
                .sub-cat-card:hover .sub-cat-img-box i {
                    transform: scale(1.15);
                    color: #ef4056 !important;
                }

                .sub-cat-card:hover .sub-cat-title {
                    color: #ef4056 !important;
                }

                .hover-bg-danger:hover {
                    background-color: #ef4056 !important;
                    color: white !important;
                }

                @media (max-width: 576px) {
                    .sub-cat-card .sub-cat-img-box {
                        width: 80px !important;
                        height: 80px !important;
                    }
                    .sub-cat-card h4 {
                        font-size: 11px !important;
                    }
                }
            `}</style>
        </main>
    );
};

export default CategoriesPage;