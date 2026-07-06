import React, { useContext } from 'react';
import { Link } from 'react-router-dom';
import { CartContext } from '../context/CartContext';
import { CompareContext } from '../context/CompareContext';

const Footer = () => {
    const { cartItems } = useContext(CartContext);
    const { compareIds } = useContext(CompareContext);

    const scrollToTop = () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    return (
        <>
            <footer className="footer pb-4 mb-5 mb-xl-0">
                <div className="container-fluid">
                    <div className="row gy-4 border-bottom pb-4 mb-4">
                        <div className="col-lg-2">
                            <h6 className="fs-4 fw-900 text-center border-top main-color-one-border border-4 border-bottom py-3 lh-lg text-dark">
                                فروشــــــگــــــاه <br/>ایــــــنــــتـــرنتی <br/>آبـــــــتــــــیــــــن
                            </h6>
                        </div>
                        <div className="col-lg-4">
                            <p className="text-muted font-14 lh-lg text-justify mt-2">
                                لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ، و با استفاده از طراحان گرافیک است، چاپگرها و متون بلکه روزنامه و مجله در ستون و سطرآنچنان که لازم است، و برای شرایط فعلی تکنولوژی مورد نیاز، و کاربردهای متنوع با هدف بهبود ابزارهای کاربردی می باشد.
                            </p>
                        </div>
                        <div className="col-lg-3">
                            <div className="row gy-3">
                                <div className="col-md-6 col-lg-12">
                                    <div className="d-flex align-items-center rounded-pill alert main-color-one-border border p-2 shadow-sm bg-white">
                                        <div className="w-40-px h-40-px rounded-circle d-flex align-items-center justify-content-center text-center main-color-one-bg">
                                            <i className="bi bi-telephone fs-5 text-white"></i>
                                        </div>
                                        <div className="ms-3">
                                            <small className="font-12 text-muted">شماره تماس</small>
                                            <h6 className="fw-normal mt-1 mb-0 text-muted" dir="ltr"><span className="fw-900 text-dark">12345678</span> 021</h6>
                                        </div>
                                    </div>
                                </div>
                                <div className="col-md-6 col-lg-12">
                                    <div className="d-flex align-items-center rounded-pill alert main-color-one-border border p-2 shadow-sm bg-white">
                                        <div className="w-40-px h-40-px rounded-circle d-flex align-items-center justify-content-center text-center main-color-one-bg">
                                            <i className="bi bi-clock fs-5 text-white"></i>
                                        </div>
                                        <div className="ms-3">
                                            <small className="font-12 text-muted">ساعت کاری</small>
                                            <h6 className="fw-900 mt-1 mb-0 text-dark">۲۴ ساعته شبانه روز</h6>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="col-lg-3">
                            <div className="row">
                                <div className="col-6">
                                    <h4 className="font-16 fw-bold mb-3 text-dark">آبتین</h4>
                                    <ul className="list-unstyled p-0 m-0">
                                        <li className="mb-2"><Link to="/about" className="text-muted text-decoration-none font-14 mco-hover">درباره ما</Link></li>
                                        <li className="mb-2"><Link to="/contact" className="text-muted text-decoration-none font-14 mco-hover">تماس با ما</Link></li>
                                        <li className="mb-2"><Link to="/privacy" className="text-muted text-decoration-none font-14 mco-hover">حریم خصوصی</Link></li>
                                    </ul>
                                </div>
                                <div className="col-6">
                                    <h4 className="font-16 fw-bold mb-3 text-dark">خدمات ما</h4>
                                    <ul className="list-unstyled p-0 m-0">
                                        <li className="mb-2"><Link to="/faq" className="text-muted text-decoration-none font-14 mco-hover">سوالات متداول</Link></li>
                                        <li className="mb-2"><Link to="/rules" className="text-muted text-decoration-none font-14 mco-hover">شرایط و قوانین</Link></li>
                                        <li className="mb-2"><Link to="/return" className="text-muted text-decoration-none font-14 mco-hover">ضمانت بازگشت کالا</Link></li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="row justify-content-center border-bottom pb-4 mb-4">
                        <div className="col-12 d-flex justify-content-center gap-3">
                            <div className="footer-namad-item border-ui p-2 rounded-4 bg-white shadow-sm">
                                <img src="https://trustseal.enamad.ir/logo.aspx?id=123" alt="Enamad" />
                            </div>
                            <div className="footer-namad-item border-ui p-2 rounded-4 bg-white shadow-sm">
                                <img src="https://logo.samandehi.ir/logo.aspx?id=123" alt="Samandehi" />
                            </div>
                        </div>
                    </div>

                    <div className="footer-copy-right d-flex flex-column flex-md-row justify-content-between align-items-center">
                        <p className="font-14 text-muted mb-3 mb-md-0">کلیه حقوق این سایت متعلق به <span className="fw-bold text-dark">فروشگاه آبتین</span> می‌باشد.</p>
                        <div className="d-flex gap-3">
                            <a href="#" className="text-muted fs-5 mco-hover"><i className="bi bi-instagram"></i></a>
                            <a href="#" className="text-muted fs-5 mco-hover"><i className="bi bi-telegram"></i></a>
                            <a href="#" className="text-muted fs-5 mco-hover"><i className="bi bi-linkedin"></i></a>
                        </div>
                    </div>
                </div>
            </footer>

            <div className="mobile-footer d-xl-none d-table justify-content-center shadow-lg bg-white position-fixed bottom-0 p-2 w-100" style={{ zIndex: 1040, tableLayout: 'fixed', borderTop: '1px solid #eee' }}>
                <ul className="d-table-row list-unstyled m-0 p-0 w-100">
                    <li className="d-table-cell align-middle cursor-pointer" onClick={scrollToTop}>
                        <div className="mf-link nav-link text-center text-muted hover-text-danger transition">
                            <span className="d-block mf-link-icon"><i className="bi bi-chevron-up fs-4"></i></span>
                            <span className="mt-1 font-12 fw-bold mf-link-title">بالا</span>
                        </div>
                    </li>
                    <li className="d-table-cell align-middle">
                        <Link to="/profile/favorites" className="mf-link nav-link text-center text-muted hover-text-danger transition text-decoration-none">
                            <div className="mf-link-icon position-relative d-table mx-auto">
                                <i className="bi bi-heart fs-4"></i>
                            </div>
                            <span className="mt-1 font-12 fw-bold mf-link-title">علاقه‌مندی</span>
                        </Link>
                    </li>
                    <li className="d-table-cell align-middle">
                        <Link to="/" className="mf-link nav-link text-center text-muted hover-text-danger transition text-decoration-none">
                            <span className="d-block mf-link-icon"><i className="bi bi-house fs-4"></i></span>
                            <span className="mt-1 font-12 fw-bold mf-link-title">خانه</span>
                        </Link>
                    </li>
                    
                    <li className="d-table-cell align-middle">
                        <Link to="/compare" className="mf-link nav-link text-center text-muted hover-text-danger transition text-decoration-none">
                            <div className="position-relative mf-link-icon d-table mx-auto overflow-visible-custom">
                                <span className="d-block mf-link-icon"><i className="bi bi-arrow-left-right fs-4"></i></span>
                                {compareIds?.length > 0 && (
                                    <span className="position-absolute bg-danger text-white rounded-circle shadow-sm fw-bold d-flex align-items-center justify-content-center px-1" style={{ top: '-4px', right: '-8px', minWidth: '18px', height: '18px', fontSize: '10px', border: '2px solid #fff', borderRadius: '50rem', lineHeight: 1 }}>
                                        {compareIds.length}
                                    </span>
                                )}
                            </div>
                            <span className="mt-1 font-12 fw-bold mf-link-title">مقایسه</span>
                        </Link>
                    </li>
                    
                    <li className="d-table-cell align-middle">
                        <div className="mf-link nav-link text-center text-muted hover-text-danger transition cursor-pointer" data-bs-toggle="offcanvas" data-bs-target="#offcanvasCart" aria-controls="offcanvasCart">
                            <div className="position-relative mf-link-icon d-table mx-auto overflow-visible-custom">
                                <span className="d-block mf-link-icon"><i className="bi bi-bag fs-4"></i></span>
                                {cartItems?.length > 0 && (
                                    <span className="position-absolute bg-danger text-white shadow-sm fw-bold d-flex align-items-center justify-content-center px-1" style={{ top: '-4px', right: '-8px', minWidth: '18px', height: '18px', fontSize: '10px', border: '2px solid #fff', borderRadius: '50rem', lineHeight: 1 }}>
                                        {cartItems.length}
                                    </span>
                                )}
                            </div>
                            <span className="mt-1 font-12 fw-bold mf-link-title">سبد خرید</span>
                        </div>
                    </li>
                </ul>
            </div>
            <style jsx="true">{`
                .cursor-pointer { cursor: pointer; }
                .overflow-visible-custom { overflow: visible !important; }
                .hover-text-danger:hover { color: #ef4056 !important; }
                .transition { transition: all 0.2s ease-in-out; }
            `}</style>
        </>
    );
};

export default Footer;