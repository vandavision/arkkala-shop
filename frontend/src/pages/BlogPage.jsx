// arkkala/frontend/src/pages/BlogPage.jsx
import React, { useState, useEffect, useRef, useContext } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { getPostsList, getBlogCategories } from '../api/blogApi';
import { getStaticPageSeo } from '../api/homeApi';
import { SiteContext } from '../context/SiteContext';
import SeoMeta from '../components/SeoMeta';

const resolveImageUrl = (url) => {
    if (!url) return '/assets/image/blog/blog-1.jpg';
    if (typeof url !== 'string') {
        if (url.url) url = url.url;
        else return '/assets/image/blog/blog-1.jpg';
    }
    if (url.startsWith('http') || url.startsWith('data:') || url.startsWith('blob:')) return url;
    let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    baseUrl = baseUrl.replace(/\/api\/?$/, '').replace(/\/$/, '');
    let path = url.startsWith('/') ? url : `/${url}`;
    if (!path.startsWith('/media/')) path = `/media${path}`;
    return `${baseUrl}${path}`;
};

const BlogPage = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const { settings } = useContext(SiteContext);
    
    const siteName = settings?.site_name || 'فروشگاه';

    const [posts, setPosts] = useState([]);
    const [categories, setCategories] = useState([]);
    const [pagination, setPagination] = useState({ count: 0, next: null, previous: null });
    const [loading, setLoading] = useState(true);
    const [seoData, setSeoData] = useState(null);

    const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '');
    const [activeCategory, setActiveCategory] = useState(searchParams.get('category__slug') || '');
    const [page, setPage] = useState(Number(searchParams.get('page')) || 1);

    const filterTimeoutRef = useRef(null);

    useEffect(() => {
        const fetchInitialData = async () => {
            try {
                const [catsData, meta] = await Promise.all([
                    getBlogCategories(),
                    getStaticPageSeo('BlogPage')
                ]);
                setCategories(catsData.results || catsData || []);
                setSeoData(meta);
            } catch (error) {
                console.error("Error fetching initial blog data", error);
            }
        };
        fetchInitialData();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, []);

    const fetchPosts = async (queryString) => {
        setLoading(true);
        try {
            const data = await getPostsList(queryString);
            setPosts(data.results || data || []);
            if (data && data.count !== undefined) {
                setPagination({ count: data.count, next: data.next, previous: data.previous });
            } else if (Array.isArray(data)) {
                setPagination({ count: data.length, next: null, previous: null });
            }
        } catch (error) {
            console.error("Error fetching posts:", error);
        } finally {
            setLoading(false);
        }
    };

    const applyFilters = () => {
        const params = new URLSearchParams();
        if (searchQuery.trim()) params.set('search', searchQuery.trim());
        if (activeCategory) params.set('category__slug', activeCategory);
        if (page > 1) params.set('page', page);

        setSearchParams(params);
        fetchPosts(params.toString());
    };

    useEffect(() => {
        if (filterTimeoutRef.current) clearTimeout(filterTimeoutRef.current);
        filterTimeoutRef.current = setTimeout(() => {
            applyFilters();
        }, 500);
    }, [searchQuery, activeCategory, page]);

    const handlePageChange = (newPage) => {
        setPage(newPage);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const handleCategorySelect = (slug) => {
        if (activeCategory === slug) setActiveCategory('');
        else setActiveCategory(slug);
        setPage(1);
    };

    const handleSearchSubmit = (e) => {
        e.preventDefault();
        setPage(1);
        applyFilters();
    };

    const totalPages = Math.ceil(pagination.count / 9);

    return (
        <main className="blog-page-wrapper bg-light min-vh-100 pb-5">
            <SeoMeta seoData={seoData} fallbackTitle={`مجله اینترنتی ${siteName}`} />

            <section className="bread-crumb py-3 bg-white shadow-sm border-bottom border-light mb-4">
                <div className="container-fluid container-xl">
                    <nav aria-label="breadcrumb">
                        <ol className="breadcrumb mb-0 px-2">
                            <li className="breadcrumb-item"><Link to="/" className="font-14 text-muted text-decoration-none hover-text-danger transition"><i className="bi bi-house me-1"></i>خانه</Link></li>
                            <li className="breadcrumb-item active text-danger font-14 fw-bold" aria-current="page">مجله {siteName}</li>
                        </ol>
                    </nav>
                </div>
            </section>

            <section className="content">
                <div className="container-fluid container-xl">
                    <div className="blog-header mb-4">
                        <div className="row gy-4 align-items-center bg-white p-4 rounded-4 shadow-sm border border-ui mx-0">
                            <div className="col-md-6 text-center text-md-start">
                                <div className="d-flex align-items-center justify-content-center justify-content-md-start gap-3">
                                    <div className="bg-danger bg-opacity-10 p-3 rounded-circle d-flex align-items-center justify-content-center">
                                        <i className="bi bi-journal-text text-danger fs-3"></i>
                                    </div>
                                    <div>
                                        <h1 className="fw-900 h4 text-dark mb-1">مجله <span className="text-danger">{siteName}</span></h1>
                                        <p className="text-muted font-13 m-0">بروزترین مقالات، نقد و بررسی‌ها و اخبار تکنولوژی</p>
                                    </div>
                                </div>
                            </div>
                            <div className="col-md-6">
                                <div className="search-bar">
                                    <form onSubmit={handleSearchSubmit}>
                                        <div className="position-relative">
                                            <input 
                                                type="text" 
                                                className="form-control py-3 px-4 rounded-pill bg-light border-0 shadow-none font-14 pe-5 text-dark fw-bold focus-white transition" 
                                                placeholder="جستجو در مقالات..."
                                                value={searchQuery}
                                                onChange={(e) => { setSearchQuery(e.target.value); setPage(1); }}
                                            />
                                            <button type="submit" className="btn border-0 position-absolute end-0 top-50 translate-middle-y me-2 text-muted hover-text-danger">
                                                <i className="bi bi-search fs-5"></i>
                                            </button>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>

                    {categories.length > 0 && (
                        <div className="blog-menu mb-5">
                            <div className="bg-white p-3 rounded-4 shadow-sm border border-ui overflow-hidden">
                                <ul className="nav flex-nowrap overflow-auto custom-scrollbar pb-2 m-0 p-0 gap-2 align-items-center d-flex flex-row">
                                    <li className="nav-item flex-shrink-0">
                                        <button 
                                            className={`btn rounded-pill px-4 py-2 font-13 fw-bold transition ${activeCategory === '' ? 'btn-danger text-white shadow-sm' : 'btn-light text-muted hover-bg-danger-light'}`}
                                            onClick={() => handleCategorySelect('')}
                                        >
                                            همه مطالب
                                        </button>
                                    </li>
                                    {categories.map(cat => (
                                        <li className="nav-item flex-shrink-0" key={cat.uuid}>
                                            <button 
                                                className={`btn rounded-pill px-4 py-2 font-13 fw-bold transition ${activeCategory === cat.slug ? 'btn-danger text-white shadow-sm' : 'btn-light text-muted hover-bg-danger-light'}`}
                                                onClick={() => handleCategorySelect(cat.slug)}
                                            >
                                                {cat.title}
                                            </button>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    )}

                    {loading ? (
                        <div className="text-center py-5 my-5">
                            <div className="spinner-border text-danger" role="status" style={{width: '3.5rem', height: '3.5rem', borderWidth: '0.25rem'}}></div>
                            <p className="mt-3 fw-bold text-muted font-15">در حال دریافت مقالات...</p>
                        </div>
                    ) : posts.length > 0 ? (
                        <div className="row gy-4 gx-3 gx-md-4">
                            {posts.map(post => (
                                <div className="col-12 col-md-6 col-lg-4 animate-fade-in" key={post.uuid}>
                                    <div className="card blog-card border-0 bg-transparent h-100 hover-lift group-blog-card">
                                        <div className="card-img position-relative z-0 overflow-hidden rounded-4 shadow-sm">
                                            <Link to={`/blog/${post.slug}`}>
                                                <picture>
                                                    <source srcSet={resolveImageUrl(post.image).replace(/\.(jpg|jpeg|png)$/i, '.webp')} type="image/webp" />
                                                    <img 
                                                        src={resolveImageUrl(post.image)} 
                                                        className="img-fluid w-100 object-fit-cover transition blog-image" 
                                                        style={{height: '240px'}}
                                                        alt={post.image_alt || post.title}
                                                        title={post.image_alt || post.title}
                                                        loading="lazy"
                                                        decoding="async"
                                                        onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/blog/blog-1.jpg'; }}
                                                    />
                                                </picture>
                                            </Link>
                                            {post.category && (
                                                <span className="position-absolute top-0 end-0 bg-white text-danger fw-bold font-11 px-3 py-1 m-3 rounded-pill shadow-sm">
                                                    {post.category.title}
                                                </span>
                                            )}
                                        </div>
                                        <div 
                                            className="card-body bg-white rounded-4 shadow-sm border border-ui position-relative mx-3 d-flex flex-column transition blog-card-body" 
                                            style={{ marginTop: '-40px', zIndex: 2 }}
                                        >
                                            <Link to={`/blog/${post.slug}`} className="text-decoration-none">
                                                <h3 className="text-overflow-2 h6 fw-900 mb-3 text-dark lh-lg transition group-blog-title">{post.title}</h3>
                                            </Link>
                                            
                                            {post.short_description && (
                                                <p className="font-13 text-muted text-justify text-overflow-2 mb-4 lh-base flex-grow-1">
                                                    {post.short_description}
                                                </p>
                                            )}

                                            <div className="d-flex mt-auto align-items-center justify-content-between border-top border-light pt-3">
                                                <div className="text-muted font-12 d-flex align-items-center fw-bold">
                                                    <i className="bi bi-calendar4-week fs-5 ms-2 text-primary"></i>
                                                    <span className="pt-1">{new Date(post.created_at).toLocaleDateString('fa-IR', { year: 'numeric', month: 'long', day: 'numeric' })}</span>
                                                </div>
                                                <Link to={`/blog/${post.slug}`} className="btn btn-sm btn-outline-danger rounded-pill px-3 py-1 font-12 fw-bold d-flex align-items-center gap-1 transition">
                                                    مطالعه <i className="bi bi-arrow-left-short fs-5"></i>
                                                </Link>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="text-center py-5 my-5 bg-white rounded-4 shadow-sm border border-ui">
                            <i className="bi bi-journal-x fs-1 text-muted opacity-50 mb-3 d-block" style={{fontSize: '4rem'}}></i>
                            <h4 className="text-muted fw-bold mb-3">مقاله‌ای یافت نشد!</h4>
                            <p className="text-muted font-14">با این مشخصات یا در این دسته‌بندی مطلبی برای نمایش وجود ندارد.</p>
                            <button className="btn btn-danger rounded-pill px-4 mt-3 shadow-sm hover-lift" onClick={() => {setSearchQuery(''); setActiveCategory(''); setPage(1);}}>
                                مشاهده همه مقالات
                            </button>
                        </div>
                    )}

                    {totalPages > 1 && (
                        <div className="my-paginate mt-5 pt-3 d-flex justify-content-center">
                            <nav aria-label="Page navigation">
                                <ul className="pagination flex-wrap justify-content-center gap-2 m-0">
                                    <li className={`page-item ${!pagination.previous ? 'disabled' : ''}`}>
                                        <button className="page-link rounded-3 border border-ui shadow-sm text-dark hover-bg-light" onClick={() => handlePageChange(Math.max(1, page - 1))}>قبلی</button>
                                    </li>
                                    {[...Array(totalPages)].map((_, i) => {
                                        const pageNum = i + 1;
                                        if (pageNum === 1 || pageNum === totalPages || (pageNum >= page - 2 && pageNum <= page + 2)) {
                                            return (
                                                <li key={i} className={`page-item ${page === pageNum ? 'active' : ''}`}>
                                                    <button className={`page-link rounded-3 border shadow-sm ${page === pageNum ? 'bg-danger border-danger text-white' : 'border-ui text-dark hover-bg-light'}`} onClick={() => handlePageChange(pageNum)}>{pageNum}</button>
                                                </li>
                                            );
                                        } else if (pageNum === page - 3 || pageNum === page + 3) {
                                            return <li key={i} className="page-item disabled"><span className="page-link border-0 bg-transparent text-muted">...</span></li>;
                                        }
                                        return null;
                                    })}
                                    <li className={`page-item ${!pagination.next ? 'disabled' : ''}`}>
                                        <button className="page-link rounded-3 border border-ui shadow-sm text-dark hover-bg-light" onClick={() => handlePageChange(Math.min(totalPages, page + 1))}>بعدی</button>
                                    </li>
                                </ul>
                            </nav>
                        </div>
                    )}

                </div>
            </section>

            <style jsx="true">{`
                .transition { transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); }
                .hover-lift { transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), box-shadow 0.3s; }
                .hover-lift:hover { transform: translateY(-5px); }
                .hover-text-danger:hover { color: #ef4056 !important; }
                .hover-bg-light:hover { background-color: #f8f9fa !important; }
                .hover-bg-danger-light:hover { background-color: #ffe6e9 !important; color: #ef4056 !important;}
                
                .text-overflow-1 { overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; }
                .text-overflow-2 { overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }

                .animate-fade-in { animation: fadeIn 0.5s cubic-bezier(0.16, 1, 0.3, 1); }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

                .custom-scrollbar::-webkit-scrollbar { height: 6px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #ddd; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #ef4056; }
                
                .focus-white:focus { background-color: #fff !important; box-shadow: 0 0 0 4px rgba(239, 64, 86, 0.1) !important; border: 1px solid #ef4056 !important;}

                .group-blog-card:hover .blog-image { transform: scale(1.08); }
                .group-blog-card:hover .group-blog-title { color: #ef4056 !important; }
                .group-blog-card:hover .blog-card-body { box-shadow: 0 15px 35px rgba(239, 64, 86, 0.1) !important; border-color: rgba(239, 64, 86, 0.3) !important;}
            `}</style>
        </main>
    );
};

export default BlogPage;