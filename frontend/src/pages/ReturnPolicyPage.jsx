import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { getStaticPageSeo } from '../api/homeApi';
import { SiteContext } from '../context/SiteContext';
import SeoMeta from '../components/SeoMeta';

const ReturnPolicyPage = () => {
    const { settings } = useContext(SiteContext);
    const [seoData, setSeoData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const meta = await getStaticPageSeo('ReturnPolicyPage');
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

    if (loading) {
        return (
            <div className="d-flex flex-column justify-content-center align-items-center min-vh-100 bg-light">
                <div className="spinner-border text-danger mb-3" style={{width: '3.5rem', height:'3.5rem', borderWidth: '0.25rem'}} role="status"></div>
                <h5 className="fw-bold text-muted font-14">در حال بارگذاری قوانین...</h5>
            </div>
        );
    }

    return (
        <main className="return-policy-page bg-light min-vh-100 pb-5">
            <SeoMeta seoData={seoData} fallbackTitle={`شرایط مرجوعی | ${settings?.site_name || 'فروشگاه'}`} />
            
            <section className="bread-crumb py-3 mb-5 bg-white shadow-sm border-bottom border-light">
                <div className="container-fluid container-xl">
                    <nav aria-label="breadcrumb">
                        <ol className="breadcrumb mb-0 px-2">
                            <li className="breadcrumb-item"><Link to="/" className="font-14 text-muted text-decoration-none hover-text-danger transition"><i className="bi bi-house me-1"></i>خانه</Link></li>
                            <li className="breadcrumb-item active text-danger font-14 fw-bold" aria-current="page">شرایط و قوانین مرجوعی کالا</li>
                        </ol>
                    </nav>
                </div>
            </section>

            <div className="container-fluid container-xl">
                <div className="bg-white rounded-5 shadow-sm border border-ui p-4 p-md-5 position-relative overflow-hidden animate-fade-in">
                    <div className="position-absolute top-0 end-0 bg-danger opacity-5 rounded-circle translate-middle" style={{width:'300px', height:'300px', filter:'blur(40px)'}}></div>
                    
                    <div className="position-relative z-1">
                        <div className="text-center mb-5">
                            <div className="bg-danger bg-opacity-10 d-inline-flex p-3 rounded-circle mb-3">
                                <i className="bi bi-arrow-return-left text-danger display-5"></i>
                            </div>
                            <h1 className="fw-900 h3 text-dark mb-2">شرایط بازگرداندن کالا در {settings?.site_name || 'فروشگاه'}</h1>
                            <p className="text-muted font-14">رضایت شما هدف اصلی ماست؛ با خیال آسوده خرید کنید.</p>
                        </div>

                        <div className="row justify-content-center">
                            <div className="col-lg-10 col-xl-9">
                                <div className="policy-content font-15 text-dark lh-lg text-justify">
                                    <h4 className="fw-900 text-dark mb-4 mt-5 border-end border-danger border-4 pe-3">۱. انصراف از خرید</h4>
                                    <p>در صورتی که قبل از ارسال کالا از خرید خود منصرف شدید، باید هر چه سریع‌تر وضعیت انصراف خود را به واحد پشتیبانی اطلاع دهید. در این حالت، مبلغ پرداختی شما ظرف مدت ۴۸ تا ۷۲ ساعت کاری به حساب شما عودت داده خواهد شد.</p>
                                    <p>اگر پس از دریافت کالا از خرید منصرف شدید، تا حداکثر ۷ روز کاری فرصت دارید کالا را بازگردانید. لازم به ذکر است که در این حالت، کالا <strong>نباید به هیچ وجه از بسته‌بندی پلمپ اولیه (وکیوم) خارج شده باشد</strong> و تمامی متعلقات آن باید به صورت کامل بازگردانده شود. هزینه ارسال کالا در حالت انصراف از خرید به عهده مشتری است.</p>

                                    <h4 className="fw-900 text-dark mb-4 mt-5 border-end border-danger border-4 pe-3">۲. مغایرت کالای دریافتی با اطلاعات سایت</h4>
                                    <p>در صورتی که کالای دریافتی با مشخصات درج شده در سایت مغایرت دارد، مشتری باید حداکثر تا ۲۴ ساعت پس از دریافت کالا، پشتیبانی را مطلع سازد. در صورتی که مغایرت از روی جعبه مشخص است، از باز کردن پلمپ کالا خودداری نمایید.</p>

                                    <h4 className="fw-900 text-dark mb-4 mt-5 border-end border-danger border-4 pe-3">۳. وجود نقص یا ایراد فنی</h4>
                                    <p>برای کالاهای دارای مهلت تست سلامت فیزیکی و فنی، مشتریان تا ۷ روز پس از دریافت کالا فرصت دارند در صورت مشاهده نقص فنی، به پشتیبانی اطلاع دهند. بدیهی است آسیب‌های ناشی از استفاده نادرست، نوسانات برق، ضربه و آب‌خوردگی شامل شرایط مرجوعی نمی‌شود.</p>

                                    <div className="alert bg-warning bg-opacity-10 border border-warning border-opacity-25 rounded-4 p-4 mt-5 d-flex gap-3">
                                        <i className="bi bi-exclamation-triangle-fill text-warning fs-3"></i>
                                        <div>
                                            <h6 className="fw-bold text-dark font-15 mb-2">فرآیند رسیدگی پس از رسیدن کالا به فروشگاه</h6>
                                            <p className="font-13 text-muted m-0 lh-lg">کارشناسان ما ایرادهای اعلام شده را بررسی می‌کنند. در صورت تایید نقص یا مغایرت، کالا تعویض و یا مبلغ آن عودت داده می‌شود. در صورتی که ایراد تایید نشود، کالا مجدداً برای مشتری ارسال می‌گردد.</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <style jsx="true">{`
                .transition { transition: all 0.3s ease-in-out; }
                .animate-fade-in { animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
                .policy-content p { margin-bottom: 1.5rem; color: #495057; }
            `}</style>
        </main>
    );
};

export default ReturnPolicyPage;