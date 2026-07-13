import React, { useState, useEffect, useContext } from 'react';
import { Link, useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { CartContext } from '../context/CartContext';
import { CompareContext } from '../context/CompareContext';
import { SiteContext } from '../context/SiteContext';
import { getCategoryTree, globalSearch } from '../api/searchApi';
import CartDrawer from './CartDrawer';

const resolveImageUrl = (url) => {
    if (!url) return null;
    if (url.startsWith('http') || url.startsWith('data:')) return url;
    let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    baseUrl = baseUrl.replace(/\/api\/?$/, '');
    return `${baseUrl}${url.startsWith('/') ? '' : '/'}${url}`;
};

const Header = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [searchParams] = useSearchParams();
    
    const { user, logout } = useContext(AuthContext);
    const { cartItems } = useContext(CartContext);
    const { compareIds } = useContext(CompareContext);
    const { settings } = useContext(SiteContext);

    const initialSearch = (location.pathname === '/shop' || location.pathname.includes('/category/')) 
        ? (searchParams.get('search') || searchParams.get('q') || '') 
        : '';
        
    const [searchQuery, setSearchQuery] = useState(initialSearch);
    
    const [searchResults, setSearchResults] = useState(null);
    const [isSearching, setIsSearching] = useState(false);
    const [showSearchDropdown, setShowSearchDropdown] = useState(false);
    
    const [categories, setCategories] = useState([]);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [expandedCategory, setExpandedCategory] = useState(null);

    useEffect(() => {
        let isMounted = true;
        const fetchCategories = async () => {
            try {
                const data = await getCategoryTree();
                if (isMounted) setCategories(data);
            } catch (error) {
                console.error('خطا در دریافت دسته‌بندی‌ها:', error);
            }
        };
        fetchCategories();
        return () => { isMounted = false; };
    }, []);

    useEffect(() => {
        setIsMobileMenuOpen(false);
        setShowSearchDropdown(false);
    }, [location]);

    useEffect(() => {
        if (location.pathname === '/shop' || location.pathname.includes('/category/')) {
            setSearchQuery(searchParams.get('search') || searchParams.get('q') || '');
        } else {
            setSearchQuery(''); 
        }
    }, [searchParams, location.pathname]);

    useEffect(() => {
        if (searchQuery.trim().length >= 2) {
            setIsSearching(true);
            const delayDebounceFn = setTimeout(async () => {
                try {
                    const data = await globalSearch(searchQuery.trim());
                    setSearchResults(data);
                    setShowSearchDropdown(true);
                } catch (error) {
                    console.error('خطا در جستجو:', error);
                } finally {
                    setIsSearching(false);
                }
            }, 500);

            return () => clearTimeout(delayDebounceFn);
        } else {
            setShowSearchDropdown(false);
            searchResults && setSearchResults(null);
        }
    }, [searchQuery]);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (!event.target.closest('.search-container')) {
                setShowSearchDropdown(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    useEffect(() => {
        if (isMobileMenuOpen) document.body.style.overflow = 'hidden';
        else document.body.style.overflow = 'unset';
    }, [isMobileMenuOpen]);

    const handleSearchSubmit = (e) => {
        if (e) e.preventDefault();
        setShowSearchDropdown(false);
        if (searchQuery.trim()) {
            navigate(`/shop?search=${encodeURIComponent(searchQuery.trim())}`);
        } else {
            navigate('/shop');
        }
    };

    const toggleAccordion = (id) => {
        if (expandedCategory === id) setExpandedCategory(null);
        else setExpandedCategory(id);
    };

    const hasResults = searchResults && (
        searchResults.products?.length > 0 || 
        searchResults.categories?.length > 0 || 
        searchResults.brands?.length > 0
    );

    const renderSearchBar = () => (
        <form onSubmit={handleSearchSubmit} className="position-relative w-100 mx-auto search-container z-3">
            <div className="input-group shadow-sm rounded-pill border border-light overflow-hidden">
                <input 
                    type="text" 
                    className="form-control bg-light border-0 shadow-none ps-4 pe-5 text-dark font-13 search-input py-3" 
                    placeholder="جستجو در محصولات، برندها و دسته‌بندی‌ها..." 
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onFocus={() => searchQuery.trim().length >= 2 && setShowSearchDropdown(true)}
                    autoComplete="off"
                />
                <button type="submit" className="btn bg-light border-0 text-muted search-btn px-4" aria-label="Search">
                    {isSearching ? <div className="spinner-border spinner-border-sm text-danger" role="status"></div> : <i className="bi bi-search fs-5 text-danger"></i>}
                </button>
            </div>

            {showSearchDropdown && (
                <div className="search-dropdown position-absolute w-100 bg-white shadow-lg rounded-4 mt-2 overflow-hidden border border-ui text-start" style={{ top: '100%', right: 0, zIndex: 9999 }} dir="rtl">
                    {isSearching ? (
                        <div className="text-center py-5">
                            <div className="spinner-border text-danger" role="status" style={{ width: '2rem', height: '2rem' }}></div>
                            <div className="mt-3 text-muted font-14 fw-bold">در حال جستجو...</div>
                        </div>
                    ) : hasResults ? (
                        <div className="row g-0">
                            <div className="col-md-8 col-12 p-3 custom-scrollbar" style={{ maxHeight: '450px', overflowY: 'auto' }}>
                                <div className="d-flex justify-content-between align-items-center mb-3 pb-2 border-bottom">
                                    <h6 className="font-14 fw-bold text-dark m-0"><i className="bi bi-box-seam text-danger me-1"></i> محصولات مرتبط</h6>
                                    <button type="button" className="btn btn-sm btn-link text-danger text-decoration-none fw-bold p-0" onClick={handleSearchSubmit}>
                                        نمایش همه <i className="bi bi-chevron-left font-12"></i>
                                    </button>
                                </div>
                                
                                <div className="row g-2">
                                    {searchResults.products?.length > 0 ? (
                                        searchResults.products.map(product => (
                                            <div className="col-md-6 col-12" key={`search-prod-${product.uuid}`}>
                                                <Link to={`/product/${product.slug}`} className="d-flex align-items-center p-2 text-decoration-none text-dark hover-bg-light rounded-3 transition border border-light h-100" onClick={() => setShowSearchDropdown(false)}>
                                                    <img 
                                                        src={product.image_url ? resolveImageUrl(product.image_url) : '/assets/image/product/logo.png'} 
                                                        alt={product.title} 
                                                        className="rounded-3 shadow-sm object-fit-cover bg-white" 
                                                        style={{ width: '60px', height: '60px', border: '1px solid #eee' }} 
                                                        loading="lazy"
                                                        decoding="async"
                                                        onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/product/logo.png'; }} 
                                                    />
                                                    <div className="ms-3 flex-grow-1 text-end">
                                                        <div className="font-13 fw-bold text-overflow-2 mb-1" style={{ lineHeight: '1.4' }}>{product.title}</div>
                                                        <div className="text-danger font-13 fw-bold">{Number(product.base_price || 0).toLocaleString()} تومان</div>
                                                    </div>
                                                </Link>
                                            </div>
                                        ))
                                    ) : (
                                        <div className="col-12 text-center py-4 text-muted font-13">محصولی با این نام یافت نشد.</div>
                                    )}
                                </div>
                            </div>

                            <div className="col-md-4 col-12 bg-light p-3 border-start custom-scrollbar" style={{ maxHeight: '450px', overflowY: 'auto' }}>
                                {searchResults.categories?.length > 0 && (
                                    <div className="mb-4 text-end">
                                        <h6 className="font-13 fw-bold text-dark mb-3"><i className="bi bi-grid text-muted me-1"></i> دسته‌بندی‌ها</h6>
                                        <div className="d-flex flex-wrap gap-2">
                                            {searchResults.categories.map(cat => (
                                                <Link to={`/shop?category__slug=${cat.slug}`} key={`search-cat-${cat.uuid}`} className="badge bg-white text-dark border border-ui p-2 fw-normal hover-bg-danger font-12 text-decoration-none shadow-sm transition" onClick={() => setShowSearchDropdown(false)}>
                                                    {cat.title}
                                                </Link>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {searchResults.brands?.length > 0 && (
                                    <div className="mb-4 text-end">
                                        <h6 className="font-13 fw-bold text-dark mb-3"><i className="bi bi-tags text-muted me-1"></i> برندها</h6>
                                        <div className="d-flex flex-wrap gap-2">
                                            {searchResults.brands.map(brand => (
                                                <Link to={`/shop?brands=${brand.slug}`} key={`search-brand-${brand.uuid}`} className="d-flex align-items-center badge bg-white text-dark border border-ui px-2 py-1 fw-normal hover-bg-danger text-decoration-none shadow-sm transition" onClick={() => setShowSearchDropdown(false)}>
                                                    {brand.logo && <img src={resolveImageUrl(brand.logo)} alt={brand.title} width="16" height="16" className="me-2 object-fit-contain" loading="lazy" decoding="async" onError={(e) => { e.target.onerror = null; e.target.style.display = 'none'; }} />}
                                                    <span className="font-12">{brand.title}</span>
                                                </Link>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : (
                        <div className="p-5 text-center text-muted">
                            <i className="bi bi-search fs-1 text-muted opacity-25 d-block mb-3"></i>
                            <h6 className="font-14 fw-bold">نتیجه‌ای برای "{searchQuery}" در فروشگاه پیدا نشد!</h6>
                            <p className="font-12 mt-2">لطفاً املای کلمه را بررسی کنید یا محصول دیگری را امتحان کنید.</p>
                        </div>
                    )}
                </div>
            )}
        </form>
    );

    return (
        <>
            <header className="override-header-styles bg-white shadow-sm border-bottom border-light">
                
                <div className="d-lg-none bg-white w-100" style={{ position: 'relative', zIndex: 10 }}>
                    <div className="container-fluid px-3 pt-3 pb-3">
                        <div className="row align-items-center pb-3 m-0 w-100">
                            <div className="col-auto p-0">
                                <button aria-label="Menu" className="btn border-0 p-0 text-dark hover-lift shadow-none" onClick={() => setIsMobileMenuOpen(true)}>
                                    <i className="bi bi-list" style={{ fontSize: '32px' }}></i>
                                </button>
                            </div>
                            <div className="col text-center p-0">
                                <Link to="/" className="d-inline-block text-center w-100">
                                    <img src={settings?.logo_url || "/assets/image/logo.png"} alt={settings?.site_name} className="img-fluid" style={{ maxHeight: '38px', objectFit: 'contain' }} fetchpriority="high" loading="eager" decoding="async" />
                                </Link>
                            </div>
                            <div className="col-auto text-end p-0">
                                <ul className="d-flex align-items-center justify-content-end list-unstyled m-0 p-0 gap-3"></ul>
                            </div>
                        </div>
                        <div className="w-100 overflow-visible-custom">
                            {renderSearchBar()}
                        </div>
                    </div>
                </div>

                <div className={`mobile-overlay ${isMobileMenuOpen ? 'show' : ''}`} onClick={() => setIsMobileMenuOpen(false)}></div>
                <div className={`mobile-sidebar bg-white ${isMobileMenuOpen ? 'open' : ''}`}>
                    <div className="d-flex justify-content-between align-items-center p-3 border-bottom border-light">
                        <img src={settings?.logo_url || "/assets/image/logo.png"} alt={settings?.site_name} style={{ maxHeight: '35px' }} loading="lazy" decoding="async" />
                        <button className="btn border-0 text-muted p-1 hover-lift" onClick={() => setIsMobileMenuOpen(false)}>
                            <i className="bi bi-x-lg fs-4"></i>
                        </button>
                    </div>
                    
                    <div className="p-3 custom-scrollbar" style={{ height: 'calc(100vh - 140px)', overflowY: 'auto' }}>
                        {user ? (
                            <div className="d-flex align-items-center bg-light p-3 rounded-4 mb-4 border border-ui">
                                <div className="bg-white rounded-circle d-flex justify-content-center align-items-center shadow-sm" style={{width: '45px', height: '45px'}}>
                                    <i className="bi bi-person text-danger fs-4"></i>
                                </div>
                                <div className="ms-3 flex-grow-1">
                                    <h6 className="mb-1 font-14 fw-bold">{user.first_name || 'کاربر سایت'}</h6>
                                    <Link to="/dashboard/profile" onClick={() => setIsMobileMenuOpen(false)} className="font-12 text-muted text-decoration-none">مشاهده حساب کاربری</Link>
                                </div>
                                <button aria-label="Logout" className="btn p-0 text-danger hover-lift" onClick={() => { logout(); setIsMobileMenuOpen(false); }}><i className="bi bi-box-arrow-right fs-5"></i></button>
                            </div>
                        ) : (
                            <Link to="/login" onClick={() => setIsMobileMenuOpen(false)} className="d-flex align-items-center bg-light p-3 rounded-4 mb-4 border border-ui text-decoration-none text-dark hover-lift transition">
                                <div className="bg-white rounded-circle d-flex justify-content-center align-items-center shadow-sm" style={{width: '45px', height: '45px'}}>
                                    <i className="bi bi-box-arrow-in-left text-danger fs-4"></i>
                                </div>
                                <h6 className="ms-3 mb-0 font-14 fw-bold flex-grow-1">ورود یا ثبت‌نام</h6>
                                <i className="bi bi-chevron-left text-muted"></i>
                            </Link>
                        )}

                        <h6 className="font-13 fw-bold text-muted mb-3">دسته‌بندی محصولات</h6>
                        <ul className="list-unstyled mobile-menu-list">
                            {categories.map(cat => (
                                <li key={`mob-cat-${cat.uuid}`}>
                                    <div className="py-3 border-bottom border-light font-14 fw-bold text-dark">
                                        {cat.children?.length > 0 ? (
                                            <div 
                                                className="d-flex justify-content-between align-items-center w-100" 
                                                onClick={() => toggleAccordion(cat.uuid)}
                                                style={{ cursor: 'pointer' }}
                                            >
                                                <div className="d-flex align-items-center gap-2 flex-grow-1">
                                                    {cat.image && <img src={resolveImageUrl(cat.image)} alt={cat.title} width="24" height="24" className="object-fit-contain rounded-circle" loading="lazy" decoding="async" onError={(e)=>{e.target.onerror = null; e.target.style.display='none'}} />}
                                                    <span className="text-dark">{cat.title}</span>
                                                </div>
                                                <i className={`bi bi-chevron-down transition ${expandedCategory === cat.uuid ? 'rotate-180 text-danger' : 'text-muted'}`}></i>
                                            </div>
                                        ) : (
                                            <Link 
                                                to={`/category/${cat.slug}`} 
                                                onClick={() => setIsMobileMenuOpen(false)}
                                                className="d-flex justify-content-between align-items-center w-100 text-dark text-decoration-none"
                                            >
                                                <div className="d-flex align-items-center gap-2 flex-grow-1">
                                                    {cat.image && <img src={resolveImageUrl(cat.image)} alt={cat.title} width="24" height="24" className="object-fit-contain rounded-circle" loading="lazy" decoding="async" onError={(e)=>{e.target.onerror = null; e.target.style.display='none'}} />}
                                                    <span>{cat.title}</span>
                                                </div>
                                            </Link>
                                        )}
                                    </div>
                                    
                                    {cat.children?.length > 0 && (
                                        <div className={`mobile-submenu overflow-hidden transition-all ${expandedCategory === cat.uuid ? 'open' : 'closed'}`}>
                                            <ul className="list-unstyled bg-light rounded-3 mt-2 p-2 ps-2 pe-3 border-end border-3 border-danger">
                                                <li className="mb-1">
                                                    <Link to={`/category/${cat.slug}`} onClick={() => setIsMobileMenuOpen(false)} className="d-flex align-items-center py-2 px-2 font-13 text-dark text-decoration-none border-bottom border-white transition hover-text-danger fw-bold">
                                                        <span className="me-2 text-danger fw-bold fs-5 lh-1">•</span> همه محصولات {cat.title}
                                                    </Link>
                                                </li>
                                                {cat.children.map(subCat => (
                                                    <li key={`mob-subcat-${subCat.uuid}`}>
                                                        <Link to={`/category/${subCat.slug}`} onClick={() => setIsMobileMenuOpen(false)} className="d-flex align-items-center py-2 px-2 font-13 text-secondary text-decoration-none border-bottom border-white transition hover-text-danger">
                                                            <span className="me-2 text-danger fw-bold fs-5 lh-1">•</span> {subCat.title}
                                                        </Link>
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </li>
                            ))}
                        </ul>

                        <h6 className="font-13 fw-bold text-muted mb-3 mt-4">دسترسی سریع</h6>
                        <ul className="list-unstyled mobile-menu-list pb-5">
                            <li><Link to="/" onClick={() => setIsMobileMenuOpen(false)} className="d-block py-3 border-bottom border-light font-14 fw-bold text-dark text-decoration-none hover-text-danger transition"><i className="bi bi-house-door text-primary me-2 fs-5"></i> صفحه اصلی فروشگاه</Link></li>
                            <li><Link to="/compare" onClick={() => setIsMobileMenuOpen(false)} className="d-block py-3 border-bottom border-light font-14 fw-bold text-dark text-decoration-none hover-text-danger transition"><i className="bi bi-shuffle text-warning me-2 fs-5"></i> مقایسه محصولات</Link></li>
                            <li><Link to="/special-offers" onClick={() => setIsMobileMenuOpen(false)} className="d-block py-3 border-bottom border-light font-14 fw-bold text-dark text-decoration-none hover-text-danger transition"><i className="bi bi-percent text-danger me-2 fs-5"></i> پیشنهادهای ویژه</Link></li>
                            <li><Link to="/best-sellers" onClick={() => setIsMobileMenuOpen(false)} className="d-block py-3 border-bottom border-light font-14 fw-bold text-dark text-decoration-none hover-text-danger transition"><i className="bi bi-fire text-warning me-2 fs-5"></i> پرفروش‌ترین‌ها</Link></li>
                            <li><Link to="/brands" onClick={() => setIsMobileMenuOpen(false)} className="d-block py-3 border-bottom border-light font-14 fw-bold text-dark text-decoration-none hover-text-danger transition"><i className="bi bi-stars text-primary me-2 fs-5"></i> برندهای برتر</Link></li>
                            <li><Link to="/blog" onClick={() => setIsMobileMenuOpen(false)} className="d-block py-3 border-bottom border-light font-14 fw-bold text-dark text-decoration-none hover-text-danger transition"><i className="bi bi-journal-text text-success me-2 fs-5"></i> مجله {settings?.site_name}</Link></li>
                            <li><Link to="/faq" onClick={() => setIsMobileMenuOpen(false)} className="d-block py-3 border-bottom border-light font-14 fw-bold text-dark text-decoration-none hover-text-danger transition"><i className="bi bi-patch-question text-info me-2 fs-5"></i> سوالات متداول</Link></li>
                            <li><Link to="/about" onClick={() => setIsMobileMenuOpen(false)} className="d-block py-3 border-bottom border-light font-14 fw-bold text-dark text-decoration-none hover-text-danger transition"><i className="bi bi-info-circle text-secondary me-2 fs-5"></i> درباره ما</Link></li>
                            <li><Link to="/rules" onClick={() => setIsMobileMenuOpen(false)} className="d-block py-3 font-14 fw-bold text-dark text-decoration-none hover-text-danger transition"><i className="bi bi-shield-check text-dark me-2 fs-5"></i> شرایط و قوانین</Link></li>
                        </ul>
                    </div>
                </div>

                <div className="d-none d-lg-block pb-1">
                    <div className="container-fluid py-3">
                        <div className="row align-items-center m-0 w-100">
                            <div className="col-lg-2 p-0">
                                <Link to="/" className="d-inline-block hover-lift transition">
                                    {/* SEO Optimization: LCP Image loaded eager with fetchpriority high */}
                                    <img src={settings?.logo_url || "/assets/image/logo.png"} alt={settings?.site_name} className="img-fluid" style={{ maxHeight: '55px', objectFit: 'contain' }} fetchpriority="high" loading="eager" decoding="async" />
                                </Link>
                            </div>

                            <div className="col-lg-6 px-4">
                                {renderSearchBar()}
                            </div>

                            <div className="col-lg-4 p-0 d-flex justify-content-end align-items-center">
                                <ul className="d-flex align-items-center justify-content-end list-unstyled m-0 p-0 gap-3">
                                    <li className="position-relative" style={{ zIndex: 20 }}>
                                        {user ? (
                                            <div className="dropdown profile-dropdown position-relative">
                                                <Link to="/dashboard" className="btn border border-ui rounded-pill px-4 py-2 bg-white d-flex align-items-center gap-2 hover-shadow transition shadow-sm font-14 fw-bold text-dark text-decoration-none">
                                                    <i className="bi bi-person-circle fs-5 text-danger"></i>
                                                    <span className="text-truncate" style={{maxWidth: '100px'}}>{user.first_name || 'حساب کاربری'}</span>
                                                    <i className="bi bi-chevron-down font-10 text-muted ms-1 mt-1 transition arrow-icon"></i>
                                                </Link>
                                                <ul className="dropdown-menu dropdown-menu-end shadow-xl border border-light rounded-4 p-2 profile-dropdown-menu" style={{ minWidth: '240px' }}>
                                                    <div className="p-3 mb-2 border-bottom border-light text-center bg-light rounded-3">
                                                        <span className="d-block font-14 fw-900 text-dark mb-1 text-truncate">{user.first_name || 'کاربر عزیز'} {user.last_name || ''}</span>
                                                        <span className="font-12 text-muted text-truncate d-block" dir="ltr">{user.phone_number || user.email || '---'}</span>
                                                    </div>
                                                    <li><Link className="dropdown-item py-2 px-3 font-14 rounded-3 hover-bg-light text-dark fw-bold mb-1 transition d-flex align-items-center" to="/dashboard"><i className="bi bi-grid-1x2 me-2 fs-5 text-muted"></i> پیشخوان من</Link></li>
                                                    <li><Link className="dropdown-item py-2 px-3 font-14 rounded-3 hover-bg-light text-dark fw-bold mb-1 transition d-flex align-items-center" to="/dashboard/profile"><i className="bi bi-person-vcard me-2 fs-5 text-muted"></i> اطلاعات حساب</Link></li>
                                                    <li><Link className="dropdown-item py-2 px-3 font-14 rounded-3 hover-bg-light text-dark fw-bold mb-1 transition d-flex align-items-center" to="/dashboard/orders"><i className="bi bi-box-seam me-2 fs-5 text-muted"></i> سفارشات من</Link></li>
                                                    <li><Link className="dropdown-item py-2 px-3 font-14 rounded-3 hover-bg-light text-dark fw-bold mb-1 transition d-flex align-items-center" to="/dashboard/favorites"><i className="bi bi-heart me-2 fs-5 text-muted"></i> علاقه‌مندی‌ها</Link></li>
                                                    <li><Link className="dropdown-item py-2 px-3 font-14 rounded-3 hover-bg-light text-dark fw-bold mb-1 transition d-flex align-items-center" to="/dashboard/comments"><i className="bi bi-chat-quote me-2 fs-5 text-muted"></i> دیدگاه‌های من</Link></li>
                                                    <li><hr className="dropdown-divider my-2 border-light" /></li>
                                                    <li><button className="dropdown-item py-2 px-3 font-14 rounded-3 hover-bg-danger-light text-danger fw-bold transition d-flex align-items-center" onClick={logout}><i className="bi bi-box-arrow-right me-2 fs-5"></i> خروج از حساب</button></li>
                                                </ul>
                                            </div>
                                        ) : (
                                            <Link to="/login" className="btn border border-ui rounded-pill px-4 py-2 bg-white d-flex align-items-center gap-2 hover-shadow transition shadow-sm text-decoration-none">
                                                <i className="bi bi-box-arrow-in-left fs-5 text-danger"></i>
                                                <span className="font-14 fw-bold text-dark">ورود | ثبت‌نام</span>
                                            </Link>
                                        )}
                                    </li>

                                    <li className="vr bg-light mx-1" style={{ height: '35px', width: '2px' }}></li>

                                    <li className="position-relative" style={{ zIndex: 20 }}>
                                        <Link to="/compare" className="btn border border-ui rounded-circle bg-white d-flex align-items-center justify-content-center shadow-sm hover-shadow transition text-decoration-none overflow-visible-custom" title="مقایسه محصولات" style={{ width: '45px', height: '45px', padding: 0, overflow: 'visible' }}>
                                            <i className="bi bi-shuffle text-dark fs-5"></i>
                                            {compareIds?.length > 0 && (
                                                <span className="position-absolute bg-warning text-dark shadow-sm fw-bold d-flex align-items-center justify-content-center px-1"
                                                      style={{ top: '-4px', right: '-4px', minWidth: '22px', height: '22px', fontSize: '11px', border: '2px solid #fff', borderRadius: '50rem', lineHeight: 1 }}>
                                                    {compareIds.length}
                                                </span>
                                            )}
                                        </Link>
                                    </li>

                                    <li className="position-relative" style={{ zIndex: 20 }}>
                                        <button type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasCart" aria-controls="offcanvasCart" className="btn border border-ui rounded-pill px-4 py-2 bg-white d-flex align-items-center gap-2 shadow-sm hover-shadow transition text-decoration-none">
                                            <div className="position-relative d-flex align-items-center justify-content-center overflow-visible-custom" style={{ width: '24px', height: '24px', overflow: 'visible' }}>
                                                <i className="bi bi-cart3 fs-5 text-dark"></i>
                                                {cartItems?.length > 0 && (
                                                    <span className="position-absolute bg-danger text-white shadow-sm fw-bold d-flex align-items-center justify-content-center px-1" 
                                                          style={{ top: '-10px', right: '-12px', minWidth: '22px', height: '22px', fontSize: '11px', border: '2px solid #fff', borderRadius: '50rem', lineHeight: 1 }}>
                                                        {cartItems.length}
                                                    </span>
                                                )}
                                            </div>
                                            <span className="font-14 fw-bold text-dark ms-1">سبد خرید</span>
                                        </button>
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    <div className="container-fluid mt-2 pb-2">
                        <ul className="d-flex list-unstyled m-0 p-0 align-items-center gap-4 h-40-px desktop-nav">
                            <li className="dropdown h-100 d-flex align-items-center position-relative group-mega-menu z-3">
                                <Link to="/categories" className="btn bg-danger text-white rounded-pill px-4 py-2 fw-bold font-14 text-decoration-none d-flex align-items-center gap-2 shadow-sm transition hover-lift">
                                    <i className="bi bi-list fs-5"></i>
                                    دسته‌بندی کالاها
                                </Link>
                                
                                <div className="position-absolute mega-menu-panel shadow-lg border border-light rounded-4 bg-white" style={{ top: '120%', right: 0, width: '280px', opacity: 0, visibility: 'hidden', transition: 'all 0.2s ease-in-out' }}>
                                    <ul className="list-unstyled mb-0 m-0 py-2">
                                        {categories.length > 0 ? (
                                            categories.map(cat => (
                                                <li key={`desk-cat-${cat.uuid}`} className="position-relative menu-item-group">
                                                    <Link 
                                                        to={`/category/${cat.slug}`} 
                                                        className="d-flex justify-content-between align-items-center py-3 px-4 font-14 fw-bold text-dark transition menu-link text-decoration-none"
                                                    >
                                                        <span className="d-flex align-items-center gap-2">
                                                            {cat.image ? (
                                                                <img src={resolveImageUrl(cat.image)} alt={cat.title} width="20" height="20" className="object-fit-contain rounded-circle" loading="lazy" decoding="async" />
                                                            ) : (
                                                                <span className="cat-bullet"></span>
                                                            )}
                                                            {cat.title}
                                                        </span>
                                                        {cat.children?.length > 0 && <i className="bi bi-chevron-left font-12 text-muted transition arrow-icon"></i>}
                                                    </Link>
                                                    
                                                    {cat.children?.length > 0 && (
                                                        <div className="position-absolute sub-menu-panel shadow-sm border-start border-light border-opacity-50 rounded-start-4 bg-white p-3" style={{ top: '0', right: '100%', minWidth: '240px', height: '100%', minHeight: '300px', opacity: 0, visibility: 'hidden', transition: 'all 0.2s ease-in-out' }}>
                                                            <h6 className="font-13 fw-900 text-muted mb-3 pb-2 border-bottom border-light">دسته‌بندی‌های {cat.title}</h6>
                                                            <ul className="list-unstyled mb-0 d-flex flex-column gap-2">
                                                                {cat.children.map(subCat => (
                                                                    <li key={`desk-subcat-${subCat.uuid}`}>
                                                                        <Link to={`/category/${subCat.slug}`} className="d-block py-1 font-13 text-secondary text-decoration-none transition fw-semibold sub-menu-link">
                                                                            {subCat.title}
                                                                        </Link>
                                                                    </li>
                                                                ))}
                                                            </ul>
                                                        </div>
                                                    )}
                                                </li>
                                            ))
                                        ) : (
                                            <li className="px-4 py-4 text-muted font-14 text-center">
                                                <div className="spinner-border spinner-border-sm text-danger me-2"></div> بارگذاری...
                                            </li>
                                        )}
                                    </ul>
                                </div>
                            </li>
                            
                            <li key="nav-divider" className="vr bg-light" style={{ height: '20px', width: '2px' }}></li>
                            <li key="nav-special-offers">
                                <Link to="/special-offers" className="text-muted font-14 fw-bold text-decoration-none d-flex align-items-center gap-2 hover-text-danger transition">
                                    <i className="bi bi-percent fs-5 text-danger"></i> پیشنهاد ویژه
                                </Link>
                            </li>
                            <li key="nav-best-sellers">
                                <Link to="/best-sellers" className="text-muted font-14 fw-bold text-decoration-none d-flex align-items-center gap-2 hover-text-danger transition">
                                    <i className="bi bi-fire fs-5 text-warning"></i> پرفروش‌ترین‌ها
                                </Link>
                            </li>
                            <li key="nav-brands">
                                <Link to="/brands" className="text-muted font-14 fw-bold text-decoration-none d-flex align-items-center gap-2 hover-text-danger transition">
                                    <i className="bi bi-stars fs-5 text-primary"></i> برندهای برتر
                                </Link>
                            </li>
                            <li key="nav-links" className="ms-auto">
                                <div className="d-flex gap-4">
                                    <Link to="/blog" className="text-muted font-13 text-decoration-none fw-semibold hover-text-danger transition">مجله {settings?.site_name}</Link>
                                    <Link to="/faq" className="text-muted font-13 text-decoration-none fw-semibold hover-text-danger transition">سوالات متداول</Link>
                                    <Link to="/about" className="text-muted font-13 text-decoration-none fw-semibold hover-text-danger transition">درباره ما</Link>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>

                <style jsx="true">{`
                    .override-header-styles { position: sticky !important; top: 0 !important; height: auto !important; min-height: fit-content !important; z-index: 1040 !important; padding: 0 !important; display: block !important; overflow: visible !important; }
                    .overflow-visible-custom { overflow: visible !important; }
                    .hover-shadow:hover { box-shadow: 0 .5rem 1rem rgba(0,0,0,.08)!important; transform: translateY(-1px); }
                    .hover-bg-light:hover { background-color: #f8f9fa!important; }
                    .hover-bg-danger-light:hover { background-color: #ffe6e9 !important; color: #ef4056 !important;}
                    .hover-text-danger:hover { color: #ef4056!important; }
                    .hover-lift { transition: transform 0.2s ease; }
                    .hover-lift:hover { transform: translateY(-2px); }
                    .cursor-pointer { cursor: pointer; }
                    .transition { transition: all 0.2s ease-in-out; }
                    .text-overflow-1 { overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; }
                    .text-overflow-2 { overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
                    .search-container .search-input { border-radius: 0 50px 50px 0 !important; }
                    .search-container .search-btn { border-radius: 50px 0 0 50px !important; }
                    .search-container .form-control:focus { background-color: #fff !important; box-shadow: 0 0 0 4px rgba(239, 64, 86, 0.1) !important; border: 1px solid #ef4056 !important; }
                    .group-mega-menu:hover .mega-menu-panel { opacity: 1 !important; visibility: visible !important; transform: translateY(10px); }
                    .menu-item-group:hover .menu-link { color: #ef4056 !important; background-color: #fce8eb; }
                    .menu-item-group:hover .arrow-icon { color: #ef4056 !important; transform: translateX(-3px); }
                    .menu-item-group:hover .cat-bullet { background-color: #ef4056 !important; transform: scale(1.5); }
                    .menu-item-group:hover .sub-menu-panel { opacity: 1 !important; visibility: visible !important; }
                    .sub-menu-link:hover { color: #ef4056 !important; padding-right: 10px; }
                    .cat-bullet { width: 6px; height: 6px; background-color: #ccc; border-radius: 50%; transition: all 0.2s ease; }
                    .mobile-sidebar { position: fixed; top: 0; right: 0; width: 300px; height: 100vh; z-index: 1060; transform: translateX(100%); transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); box-shadow: -5px 0 15px rgba(0,0,0,0.05); }
                    .mobile-sidebar.open { transform: translateX(0); }
                    .mobile-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100vh; background: rgba(0,0,0,0.5); z-index: 1055; opacity: 0; visibility: hidden; transition: all 0.3s; backdrop-filter: blur(2px); }
                    .mobile-overlay.show { opacity: 1; visibility: visible; }
                    .rotate-180 { transform: rotate(180deg); }
                    .mobile-submenu { max-height: 0; opacity: 0; transition: all 0.3s ease-in-out; }
                    .mobile-submenu.open { max-height: 500px; opacity: 1; margin-bottom: 10px; }
                    .custom-scrollbar::-webkit-scrollbar { width: 6px; }
                    .custom-scrollbar::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
                    .custom-scrollbar::-webkit-scrollbar-thumb { background: #ddd; border-radius: 10px; }
                    .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #ccc; }
                    .rounded-circle {border-radius: 50% !important;}
                    
                    @media (min-width: 992px) {
                        .profile-dropdown:hover .profile-dropdown-menu {
                            display: block !important;
                            animation: fadeInDropdown 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                        }
                        .profile-dropdown:hover .arrow-icon {
                            transform: rotate(180deg);
                        }
                        .profile-dropdown-menu {
                            top: 100%;
                            margin-top: 10px !important;
                            box-shadow: 0 15px 35px rgba(0,0,0,0.1) !important;
                        }
                        .profile-dropdown-menu::before {
                            content: '';
                            position: absolute;
                            top: -15px;
                            left: 0;
                            width: 100%;
                            height: 15px;
                            background: transparent;
                        }
                    }
                    @keyframes fadeInDropdown {
                        from { opacity: 0; transform: translateY(15px); }
                        to { opacity: 1; transform: translateY(0); }
                    }
                `}</style>
            </header>
            <CartDrawer />
        </>
    );
};

export default Header;