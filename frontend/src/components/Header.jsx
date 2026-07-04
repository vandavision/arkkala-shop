// arkkala/frontend/src/components/Header.jsx
import React, { useState, useEffect, useContext, useRef } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import { CartContext } from '../context/CartContext';
import { getCategoryTree, globalSearch } from '../api/searchApi';

const Header = () => {
    const navigate = useNavigate();
    const location = useLocation();
    
    const { user, logout } = useContext(AuthContext);
    const { cartItems } = useContext(CartContext);

    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState(null);
    const [isSearching, setIsSearching] = useState(false);
    const [showSearchDropdown, setShowSearchDropdown] = useState(false);
    
    const [categories, setCategories] = useState([]);
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
    const [expandedCategory, setExpandedCategory] = useState(null);
    
    const searchRef = useRef(null);

    useEffect(() => {
        const fetchCategories = async () => {
            try {
                const data = await getCategoryTree();
                setCategories(data);
            } catch (error) {
                console.error('خطا در دریافت دسته‌بندی‌ها:', error);
            }
        };
        fetchCategories();
    }, []);

    useEffect(() => {
        setIsMobileMenuOpen(false);
        setShowSearchDropdown(false);
    }, [location]);

    useEffect(() => {
        if (searchQuery.trim().length > 2) {
            setIsSearching(true);
            const delayDebounceFn = setTimeout(async () => {
                try {
                    const data = await globalSearch(searchQuery);
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
            setSearchResults(null);
        }
    }, [searchQuery]);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (searchRef.current && !searchRef.current.contains(event.target)) {
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
        e.preventDefault();
        if (searchQuery.trim()) {
            setShowSearchDropdown(false);
            navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
        }
    };

    const toggleAccordion = (id) => {
        if (expandedCategory === id) setExpandedCategory(null);
        else setExpandedCategory(id);
    };


    const SearchBar = ({ isMobile }) => (
        <form onSubmit={handleSearchSubmit} className="position-relative w-100 mx-auto search-container" ref={!isMobile ? searchRef : null}>
            <div className="input-group">
                <input 
                    type="text" 
                    className="form-control bg-light border-0 shadow-none ps-4 pe-5 text-dark font-14 search-input" 
                    placeholder="جستجو در محصولات، برندها..." 
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    onFocus={() => searchQuery.length > 2 && setShowSearchDropdown(true)}
                />
                <button type="submit" className="btn bg-light border-0 text-muted search-btn">
                    {isSearching ? <div className="spinner-border spinner-border-sm text-danger" role="status"></div> : <i className="bi bi-search fs-5"></i>}
                </button>
            </div>

            {/* دراپ‌داون نتایج جستجو */}
            {showSearchDropdown && searchResults && (
                <div className="search-dropdown position-absolute w-100 bg-white shadow-xl rounded-4 mt-2 overflow-hidden border border-light">
                    {searchResults.products?.length > 0 || searchResults.posts?.length > 0 ? (
                        <div className="p-2 custom-scrollbar" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                            {searchResults.products?.length > 0 && (
                                <div className="mb-3">
                                    <h6 className="font-12 fw-bold text-muted px-3 py-2 bg-light rounded-3 mb-2">محصولات</h6>
                                    <ul className="list-unstyled mb-0">
                                        {searchResults.products.map(product => (
                                            <li key={`search-prod-${product.uuid}`}>
                                                <Link to={`/product/${product.slug}`} className="d-flex align-items-center p-2 text-decoration-none text-dark hover-bg-light rounded-3 transition">
                                                    <img src={product.image_url || '/assets/image/product/product_cover_1.png'} alt={product.title} className="rounded-3 shadow-sm object-fit-cover" style={{ width: '50px', height: '50px' }} />
                                                    <div className="ms-3 flex-grow-1">
                                                        <div className="font-13 fw-bold text-overflow-1">{product.title}</div>
                                                        <div className="text-danger font-13 fw-bold mt-1">{Number(product.base_price || 0).toLocaleString()} تومان</div>
                                                    </div>
                                                </Link>
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="p-4 text-center text-muted font-14">
                            <i className="bi bi-emoji-frown fs-3 d-block mb-2 text-warning"></i>
                            نتیجه‌ای یافت نشد!
                        </div>
                    )}
                </div>
            )}
        </form>
    );

    return (
        <>
            <header className="main-header bg-white sticky-top shadow-sm border-bottom border-light" style={{ zIndex: 1040 }}>
                

                <div className="d-lg-none">
                    <div className="d-flex justify-content-between align-items-center p-3">
                        <button className="btn border-0 p-0 text-dark" onClick={() => setIsMobileMenuOpen(true)}>
                            <i className="bi bi-list" style={{ fontSize: '28px' }}></i>
                        </button>

                        <Link to="/" className="d-inline-block text-center flex-grow-1">
                            <img src="/assets/image/logo.png" alt="آبتین" className="img-fluid" style={{ maxHeight: '40px', objectFit: 'contain' }} />
                        </Link>

                        <Link to="/cart" className="position-relative text-dark text-decoration-none">
                            <i className="bi bi-cart3" style={{ fontSize: '24px' }}></i>
                            <span className="position-absolute top-0 start-0 translate-middle badge rounded-circle bg-danger" style={{ padding: '5px', fontSize: '10px' }}>
                                {cartItems?.length || 0}
                            </span>
                        </Link>
                    </div>
                    <div className="px-3 pb-3" ref={searchRef}>
                        <SearchBar isMobile={true} />
                    </div>
                </div>


                <div className={`mobile-overlay ${isMobileMenuOpen ? 'show' : ''}`} onClick={() => setIsMobileMenuOpen(false)}></div>
                <div className={`mobile-sidebar bg-white ${isMobileMenuOpen ? 'open' : ''}`}>
                    <div className="d-flex justify-content-between align-items-center p-3 border-bottom border-light">
                        <img src="/assets/image/logo.png" alt="آبتین" style={{ maxHeight: '35px' }} />
                        <button className="btn border-0 text-muted p-1" onClick={() => setIsMobileMenuOpen(false)}>
                            <i className="bi bi-x-lg fs-4"></i>
                        </button>
                    </div>
                    
                    <div className="p-3 custom-scrollbar" style={{ height: 'calc(100vh - 140px)', overflowY: 'auto' }}>
                        {user ? (
                            <div className="d-flex align-items-center bg-light p-3 rounded-4 mb-4">
                                <div className="bg-white rounded-circle d-flex justify-content-center align-items-center shadow-sm" style={{width: '45px', height: '45px'}}>
                                    <i className="bi bi-person text-danger fs-4"></i>
                                </div>
                                <div className="ms-3 flex-grow-1">
                                    <h6 className="mb-1 font-14 fw-bold">{user.first_name || 'کاربر سایت'}</h6>
                                    <Link to="/profile" onClick={() => setIsMobileMenuOpen(false)} className="font-12 text-muted text-decoration-none">مشاهده حساب کاربری</Link>
                                </div>
                                <button className="btn p-0 text-danger" onClick={() => { logout(); setIsMobileMenuOpen(false); }}><i className="bi bi-box-arrow-right fs-5"></i></button>
                            </div>
                        ) : (
                            <Link to="/login" onClick={() => setIsMobileMenuOpen(false)} className="d-flex align-items-center bg-light p-3 rounded-4 mb-4 text-decoration-none text-dark">
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
                                                <span className="text-dark flex-grow-1">{cat.title}</span>
                                                <i className={`bi bi-chevron-down transition ${expandedCategory === cat.uuid ? 'rotate-180 text-danger' : 'text-muted'}`}></i>
                                            </div>
                                        ) : (
                                            <Link 
                                                to={`/category/${cat.slug}`} 
                                                onClick={() => setIsMobileMenuOpen(false)}
                                                className="d-flex justify-content-between align-items-center w-100 text-dark text-decoration-none"
                                            >
                                                <span className="flex-grow-1">{cat.title}</span>
                                            </Link>
                                        )}
                                    </div>
                                    
                                    {cat.children?.length > 0 && (
                                        <div className={`mobile-submenu overflow-hidden transition-all ${expandedCategory === cat.uuid ? 'open' : 'closed'}`}>
                                            <ul className="list-unstyled bg-light rounded-3 mt-2 p-2 ps-2 pe-3 border-end border-3 border-danger">
                                                <li className="mb-1">
                                                    <Link 
                                                        to={`/category/${cat.slug}`} 
                                                        onClick={() => setIsMobileMenuOpen(false)} 
                                                        className="d-flex align-items-center py-2 px-2 font-13 text-dark text-decoration-none border-bottom border-white transition hover-text-danger fw-bold"
                                                    >
                                                        <span className="me-2 text-danger fw-bold fs-5 lh-1">•</span>
                                                        همه محصولات {cat.title}
                                                    </Link>
                                                </li>
                                                {cat.children.map(subCat => (
                                                    <li key={`mob-subcat-${subCat.uuid}`}>
                                                        <Link 
                                                            to={`/category/${subCat.slug}`} 
                                                            onClick={() => setIsMobileMenuOpen(false)} 
                                                            className="d-flex align-items-center py-2 px-2 font-13 text-secondary text-decoration-none border-bottom border-white transition hover-text-danger"
                                                        >
                                                            <span className="me-2 text-danger fw-bold fs-5 lh-1">•</span>
                                                            {subCat.title}
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
                        <ul className="list-unstyled mobile-menu-list">
                            <li><Link to="/special-offers" onClick={() => setIsMobileMenuOpen(false)} className="d-block py-3 border-bottom border-light font-14 fw-bold text-dark text-decoration-none"><i className="bi bi-percent text-danger me-2 fs-5"></i> پیشنهادهای ویژه</Link></li>
                            <li><Link to="/best-sellers" onClick={() => setIsMobileMenuOpen(false)} className="d-block py-3 border-bottom border-light font-14 fw-bold text-dark text-decoration-none"><i className="bi bi-fire text-warning me-2 fs-5"></i> پرفروش‌ترین‌ها</Link></li>
                            <li><Link to="/blog" onClick={() => setIsMobileMenuOpen(false)} className="d-block py-3 font-14 fw-bold text-dark text-decoration-none"><i className="bi bi-journal-text text-primary me-2 fs-5"></i> مجله آبتین</Link></li>
                        </ul>
                    </div>
                </div>

                <div className="d-none d-lg-block pb-1">
                    <div className="container-fluid py-3">
                        <div className="row align-items-center">
                            
                            <div className="col-lg-2">
                                <Link to="/" className="d-inline-block hover-lift transition">
                                    <img src="/assets/image/logo.png" alt="فروشگاه آبتین" className="img-fluid" style={{ maxHeight: '55px', objectFit: 'contain' }} />
                                </Link>
                            </div>

                            <div className="col-lg-6 px-4">
                                <SearchBar isMobile={false} />
                            </div>

                            <div className="col-lg-4 d-flex justify-content-end gap-3 align-items-center">
                                {user ? (
                                    <div className="dropdown profile-dropdown hover-menu">
                                        <button className="btn border border-ui rounded-pill px-4 py-2 bg-white d-flex align-items-center gap-2 hover-shadow transition shadow-sm font-14 fw-bold text-dark">
                                            <i className="bi bi-person-circle fs-5 text-danger"></i>
                                            {user.first_name || 'حساب کاربری'}
                                            <i className="bi bi-chevron-down font-10 text-muted ms-1 mt-1"></i>
                                        </button>
                                        <ul className="dropdown-menu dropdown-menu-end shadow-xl border-0 rounded-4 mt-1 p-2" style={{ minWidth: '220px' }}>
                                            <li><Link className="dropdown-item py-2 font-14 rounded-3 hover-bg-light text-dark fw-bold mb-1" to="/profile"><i className="bi bi-person me-2 fs-5 text-muted"></i> پروفایل کاربری</Link></li>
                                            <li><Link className="dropdown-item py-2 font-14 rounded-3 hover-bg-light text-dark fw-bold mb-1" to="/orders"><i className="bi bi-box-seam me-2 fs-5 text-muted"></i> سفارشات من</Link></li>
                                            <li><hr className="dropdown-divider my-2 border-light" /></li>
                                            <li><button className="dropdown-item py-2 font-14 rounded-3 hover-bg-light text-danger fw-bold" onClick={logout}><i className="bi bi-box-arrow-right me-2 fs-5"></i> خروج از حساب</button></li>
                                        </ul>
                                    </div>
                                ) : (
                                    <Link to="/login" className="btn border border-ui rounded-pill px-4 py-2 bg-white d-flex align-items-center gap-2 hover-shadow transition shadow-sm">
                                        <i className="bi bi-box-arrow-in-left fs-5 text-danger"></i>
                                        <span className="font-14 fw-bold text-dark">ورود | ثبت‌نام</span>
                                    </Link>
                                )}
                                
                                <div className="vr bg-light mx-2" style={{ height: '35px', width: '2px' }}></div>

                                <Link to="/cart" className="btn border border-ui rounded-pill px-4 py-2 position-relative bg-white d-flex align-items-center gap-2 hover-shadow transition shadow-sm cart-btn">
                                    <i className="bi bi-cart3 fs-5 text-dark"></i>
                                    <span className="font-14 fw-bold text-dark">سبد خرید</span>
                                    <span className="position-absolute top-0 start-0 translate-middle badge rounded-circle bg-danger shadow-sm border border-2 border-white d-flex align-items-center justify-content-center" style={{ width: '24px', height: '24px', fontSize: '11px' }}>
                                        {cartItems?.length || 0}
                                    </span>
                                </Link>
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
                                                            <span className="cat-bullet"></span>
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
                                    <Link to="/blog" className="text-muted font-13 text-decoration-none fw-semibold hover-text-danger transition">وبلاگ</Link>
                                    <Link to="/faq" className="text-muted font-13 text-decoration-none fw-semibold hover-text-danger transition">سوالات متداول</Link>
                                    <Link to="/about" className="text-muted font-13 text-decoration-none fw-semibold hover-text-danger transition">درباره ما</Link>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>
            </header>

            <style jsx="true">{`
                .hover-shadow:hover { box-shadow: 0 .5rem 1rem rgba(0,0,0,.08)!important; transform: translateY(-1px); }
                .hover-bg-light:hover { background-color: #f8f9fa!important; }
                .hover-text-danger:hover { color: #ef4056!important; }
                .hover-lift { transition: transform 0.2s ease; }
                .hover-lift:hover { transform: translateY(-2px); }
                .transition { transition: all 0.2s ease-in-out; }
                
                .search-container .search-input { border-radius: 0 12px 12px 0 !important; }
                .search-container .search-btn { border-radius: 12px 0 0 12px !important; }
                .search-container .form-control:focus { background-color: #fff !important; box-shadow: 0 0 0 4px rgba(239, 64, 86, 0.1) !important; border: 1px solid #ef4056 !important; }
                .search-dropdown { z-index: 1060; }
                
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

                @keyframes fadeUp {
                    from { opacity: 0; transform: translateY(10px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                @keyframes fadeRight {
                    from { opacity: 0; transform: translateX(10px); }
                    to { opacity: 1; transform: translateX(0); }
                }
            `}</style>
        </>
    );
};

export default Header;