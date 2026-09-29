import React, { useContext } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { CartContext } from '../context/CartContext';
import { CompareContext } from '../context/CompareContext';
import { SiteContext } from '../context/SiteContext'; 

const Footer = () => {
    const { cartItems } = useContext(CartContext);
    const { compareIds } = useContext(CompareContext);
    const { settings } = useContext(SiteContext); 
    const location = useLocation();

    const isHomeActive = location.pathname === '/';
    const isFavActive = location.pathname.includes('/favorites');
    const isCompareActive = location.pathname.includes('/compare');
    const isProfileActive = location.pathname.includes('/dashboard') && !isFavActive;

    const scrollToTop = () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const activeNamads = [];
    for (let i = 1; i <= 7; i++) {
        const imgUrl = settings?.[`namad_${i}_img_url`];
        const linkUrl = settings?.[`namad_${i}_link`];
        
        if (imgUrl) {
            activeNamads.push({
                id: i,
                img: imgUrl,
                link: linkUrl && linkUrl !== 'null' ? linkUrl : '#'
            });
        }
    }

    return (
        <>
            <footer className="footer bg-white border-top border-ui pt-5 mt-5 pb-5 pb-xl-2 mb-5 mb-xl-0">
                <div className="container-fluid container-xl">
                    <div className="row gy-4 border-bottom border-light pb-5 mb-4">
                        
                        <div className="col-lg-2">
                            <h6 className="fs-4 fw-900 text-center border-top border-danger border-4 border-bottom py-3 lh-lg text-dark">
                                فروشگاه <br/> اینترنتی <br/> {settings?.site_name || '...'}
                            </h6>
                        </div>

                        <div className="col-lg-4">
                            <p className="text-muted font-14 lh-lg text-justify pe-lg-3 m-0" dangerouslySetInnerHTML={{ __html: settings?.about_us_footer?.replace(/\n/g, '<br/>') || '' }}></p>
                        </div>

                        <div className="col-lg-3">
                            <div className="row gy-3">
                                <div className="col-md-6 col-lg-12">
                                    <div className="d-flex align-items-center rounded-pill alert border-danger border bg-white m-0 p-2 shadow-sm">
                                        <div className="rounded-circle d-flex align-items-center justify-content-center text-center bg-danger text-white flex-shrink-0" style={{width: '40px', height: '40px'}}>
                                            <i className="bi bi-phone-flip fs-5"></i>
                                        </div>
                                        <div className="ms-3 text-truncate">
                                            <small className="font-12 text-muted d-block">شماره تماس</small>
                                            <h6 className="fw-900 mt-1 mb-0 text-dark font-14 text-truncate" dir="ltr">{settings?.phone_number || '---'}</h6>
                                        </div>
                                    </div>
                                </div>
                                <div className="col-md-6 col-lg-12">
                                    <div className="d-flex align-items-center rounded-pill alert border-danger border bg-white m-0 p-2 shadow-sm">
                                        <div className="rounded-circle d-flex align-items-center justify-content-center text-center bg-danger text-white flex-shrink-0" style={{width: '40px', height: '40px'}}>
                                            <i className="bi bi-clock fs-5"></i>
                                        </div>
                                        <div className="ms-3 text-truncate">
                                            <small className="font-12 text-muted d-block">ساعت کاری</small>
                                            <h6 className="fw-900 mt-1 mb-0 text-dark font-14 text-truncate">{settings?.working_hours || '---'}</h6>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="col-lg-3">
                            <div className="row">
                                <div className="col-6">
                                    <h4 className="font-15 fw-bold mb-3 text-dark icon-circle position-relative pe-3 ms-2">{settings?.site_name}</h4>
                                    <ul className="navbar-nav gap-2">
                                        <li className="nav-item"><Link to="/about" className="nav-link text-muted font-13 hover-text-danger p-0 transition">درباره ما</Link></li>
                                        <li className="nav-item"><Link to="/contact" className="nav-link text-muted font-13 hover-text-danger p-0 transition">تماس با ما</Link></li>
                                        <li className="nav-item"><Link to="/blog" className="nav-link text-muted font-13 hover-text-danger p-0 transition">مجله</Link></li>
                                        <li className="nav-item"><Link to="/brands" className="nav-link text-muted font-13 hover-text-danger p-0 transition">برندها</Link></li>
                                    </ul>
                                </div>
                                <div className="col-6">
                                    <h4 className="font-15 fw-bold mb-3 text-dark icon-circle position-relative pe-3 ms-2">خدمات ما</h4>
                                    <ul className="navbar-nav gap-2">
                                        <li className="nav-item"><Link to="/faq" className="nav-link text-muted font-13 hover-text-danger p-0 transition">سوالات متداول</Link></li>
                                        <li className="nav-item"><Link to="/rules" className="nav-link text-muted font-13 hover-text-danger p-0 transition">شرایط و قوانین</Link></li>
                                        <li className="nav-item"><Link to="/return" className="nav-link text-muted font-13 hover-text-danger p-0 transition">مرجوعی کالا</Link></li>
                                        <li className="nav-item"><Link to="/dashboard/orders" className="nav-link text-muted font-13 hover-text-danger p-0 transition">پیگیری سفارش</Link></li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="row mb-4">
                        <div className="col-12">
                            <nav className="navbar navbar-expand justify-content-center p-0">
                                <ul className="navbar-nav flex-row flex-wrap justify-content-center gap-3">
                                    {activeNamads.map(namad => (
                                        <li className="nav-item" key={`namad-${namad.id}`}>
                                            <a href={namad.link} target="_blank" rel="noreferrer" className="nav-link bg-light border border-ui rounded-4 shadow-sm hover-lift d-flex align-items-center justify-content-center p-2 bg-white" style={{width: '90px', height: '90px'}}>
                                                <img src={namad.img} alt={`نماد اعتبار ${namad.id}`} className="img-fluid object-fit-contain w-100 h-100" loading="lazy" decoding="async" />
                                            </a>
                                        </li>
                                    ))}
                                </ul>
                            </nav>
                        </div>
                    </div>

                    <div className="row align-items-center pb-2">
                        <div className="col-md-5 text-center text-md-start mb-3 mb-md-0">
                            <p className="font-13 text-muted m-0">{settings?.copyright_text || `کلیه حقوق این سایت متعلق به ${settings?.site_name} می‌باشد.`}</p>
                        </div>
                        
                        <div className="col-md-2 text-center d-none d-md-block">
                            <button onClick={scrollToTop} aria-label="Scroll to top" className="btn bg-danger text-white rounded-circle shadow-sm hover-lift d-flex align-items-center justify-content-center mx-auto p-0" style={{width:'40px', height:'40px'}}>
                                <i className="bi bi-chevron-up fs-5"></i>
                            </button>
                        </div>

                        <div className="col-md-5 text-center text-md-end">
                            <nav className="navbar navbar-expand p-0 justify-content-center justify-content-md-end">
                                <ul className="navbar-nav flex-row gap-3">
                                    {settings?.instagram && <li className="nav-item"><a href={settings.instagram} target="_blank" rel="noreferrer" className="nav-link text-muted hover-text-danger fs-5 transition p-0" aria-label="اینستاگرام"><i className="bi bi-instagram"></i></a></li>}
                                    {settings?.twitter && <li className="nav-item"><a href={settings.twitter} target="_blank" rel="noreferrer" className="nav-link text-muted hover-text-info fs-5 transition p-0" aria-label="توییتر"><i className="bi bi-twitter-x"></i></a></li>}
                                    {settings?.linkedin && <li className="nav-item"><a href={settings.linkedin} target="_blank" rel="noreferrer" className="nav-link text-muted hover-text-primary fs-5 transition p-0" aria-label="لینکدین"><i className="bi bi-linkedin"></i></a></li>}
                                    {settings?.telegram && <li className="nav-item"><a href={settings.telegram} target="_blank" rel="noreferrer" className="nav-link text-muted hover-text-primary fs-5 transition p-0" aria-label="تلگرام"><i className="bi bi-telegram"></i></a></li>}
                                    {settings?.whatsapp && <li className="nav-item"><a href={settings.whatsapp} target="_blank" rel="noreferrer" className="nav-link text-muted hover-text-success fs-5 transition p-0" aria-label="واتساپ"><i className="bi bi-whatsapp"></i></a></li>}
                                </ul>
                            </nav>
                        </div>
                    </div>
                </div>
            </footer>

            {/* Curved Cutout Center FAB Navigation */}
            <div className="curved-bottom-nav d-xl-none">
                <div className="nav-container shadow-lg">
                    
                    <Link to="/" className={`nav-item-curved ${isHomeActive ? 'active' : ''}`}>
                        <div className="icon-wrapper">
                            <i className={`bi ${isHomeActive ? 'bi-house-fill' : 'bi-house'}`}></i>
                        </div>
                        <span className="dot"></span>
                    </Link>

                    <Link to="/compare" className={`nav-item-curved ${isCompareActive ? 'active' : ''}`}>
                        <div className="icon-wrapper">
                            <i className="bi bi-shuffle"></i>
                            {compareIds?.length > 0 && (
                                <span className="count-badge">{compareIds.length}</span>
                            )}
                        </div>
                        <span className="dot"></span>
                    </Link>

                    <div className="nav-item-center-wrap" data-bs-toggle="offcanvas" data-bs-target="#offcanvasCart">
                        <div className="center-fab shadow-lg">
                            <i className="bi bi-bag fs-4 text-white"></i>
                            {cartItems?.length > 0 && (
                                <span className="fab-badge">{cartItems.length}</span>
                            )}
                        </div>
                    </div>

                    <Link to="/dashboard/favorites" className={`nav-item-curved ${isFavActive ? 'active' : ''}`}>
                        <div className="icon-wrapper">
                            <i className={`bi ${isFavActive ? 'bi-heart-fill' : 'bi-heart'}`}></i>
                        </div>
                        <span className="dot"></span>
                    </Link>

                    <Link to="/dashboard" className={`nav-item-curved ${isProfileActive ? 'active' : ''}`}>
                        <div className="icon-wrapper">
                            <i className={`bi ${isProfileActive ? 'bi-person-fill' : 'bi-person'}`}></i>
                        </div>
                        <span className="dot"></span>
                    </Link>

                </div>
            </div>

            <style jsx="true">{`
                /* Desktop Footer Styles */
                .cursor-pointer { cursor: pointer; }
                .hover-text-danger:hover { color: #ef4056 !important; padding-right: 5px; }
                .hover-text-info:hover { color: #0dcaf0 !important; }
                .hover-text-success:hover { color: #198754 !important; }
                .hover-text-primary:hover { color: #0d6efd !important; }
                
                .hover-lift { transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s; }
                .hover-lift:hover { transform: translateY(-4px); box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important; }
                .transition { transition: all 0.3s ease; }
                
                .icon-circle::before { 
                    content: ""; 
                    position: absolute; 
                    right: 0; 
                    top: 35%; 
                    width: 8px; 
                    height: 8px; 
                    border-radius: 50%; 
                    background-color: #ef4056; 
                }

                /* --- Curved Cutout Center FAB Navigation --- */
                .curved-bottom-nav {
                    position: fixed;
                    bottom: 20px;
                    left: 50%;
                    transform: translateX(-50%);
                    width: 94%;
                    max-width: 450px;
                    z-index: 1040;
                }

                .curved-bottom-nav .nav-container {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    height: 70px;
                    /* The magic cutout is created using radial-gradient */
                    /* A circle positioned 5px below the top edge creates the perfect notch */
                    background: radial-gradient(circle at 50% 5px, transparent 36px, #ffffff 37px);
                    border-radius: 25px;
                    filter: drop-shadow(0 10px 25px rgba(0, 0, 0, 0.12));
                    padding: 0 10px;
                    direction: rtl; /* Align RTL */
                }

                .nav-item-curved {
                    flex: 1;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100%;
                    color: #b0b0b0; /* Light grey for inactive */
                    text-decoration: none;
                    -webkit-tap-highlight-color: transparent;
                    transition: all 0.3s ease;
                }

                .nav-item-curved .icon-wrapper {
                    position: relative;
                    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                }

                .nav-item-curved i {
                    font-size: 24px;
                }

                /* Active State Styling */
                .nav-item-curved.active {
                    color: #ef4056;
                }

                .nav-item-curved.active .icon-wrapper {
                    transform: translateY(-4px);
                }

                /* The Dot Indicator */
                .nav-item-curved .dot {
                    width: 6px;
                    height: 6px;
                    background-color: #ef4056;
                    border-radius: 50%;
                    margin-top: 4px;
                    opacity: 0;
                    transform: scale(0);
                    transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                }

                .nav-item-curved.active .dot {
                    opacity: 1;
                    transform: scale(1);
                }

                /* Center FAB Styling */
                .nav-item-center-wrap {
                    flex: 1.2; /* Slightly wider to give breathing room around the cutout */
                    display: flex;
                    justify-content: center;
                    position: relative;
                    height: 100%;
                    cursor: pointer;
                    -webkit-tap-highlight-color: transparent;
                }

                .center-fab {
                    position: absolute;
                    top: -25px; /* Center of FAB aligns with +5px inside the bar to match the cutout */
                    width: 60px;
                    height: 60px;
                    background: #ef4056;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    box-shadow: 0 8px 20px rgba(239, 64, 86, 0.4) !important;
                    transition: transform 0.2s cubic-bezier(0.175, 0.885, 0.32, 1.275);
                }

                .nav-item-center-wrap:active .center-fab {
                    transform: scale(0.9);
                }

                /* Badges */
                .count-badge {
                    position: absolute;
                    top: -4px;
                    right: -6px;
                    background: #ef4056;
                    color: #fff;
                    font-size: 10px;
                    min-width: 16px;
                    height: 16px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 900;
                    border: 2px solid #fff;
                    line-height: 1;
                }

                .fab-badge {
                    position: absolute;
                    top: -2px;
                    right: -2px;
                    background: #fff;
                    color: #ef4056;
                    font-size: 11px;
                    min-width: 20px;
                    height: 20px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 900;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                }

                /* iPhone safe area support */
                @supports (padding-bottom: env(safe-area-inset-bottom)) {
                    .curved-bottom-nav {
                        bottom: calc(20px + env(safe-area-inset-bottom));
                    }
                }
            `}</style>
        </>
    );
};

export default Footer;