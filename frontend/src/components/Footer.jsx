// arkkala/frontend/src/components/Footer.jsx
import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => {
    return (
        <footer className="footer pb-4">
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
    );
};

export default Footer;