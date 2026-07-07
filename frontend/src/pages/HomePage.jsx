import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Autoplay, Pagination, Navigation, FreeMode } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/pagination';
import 'swiper/css/navigation';
import 'swiper/css/free-mode';

import { getHomePageData } from '../api/homeApi';
import ProductCard from '../components/ProductCard';
import CountdownTimer from '../components/CountdownTimer';

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

const SectionTitle = ({ title, highlight, linkPath, linkText = "مشاهده همه" }) => (
    <div className="d-flex flex-wrap align-items-center justify-content-between border-bottom border-light pb-3 mb-4">
        <div className="d-flex align-items-center gap-2">
            <div className="bg-danger rounded-pill" style={{width: '6px', height: '24px'}}></div>
            <h2 className="fw-900 h5 m-0 text-dark d-flex align-items-center gap-2">
                <span>{title}</span> <span className="text-danger">{highlight}</span>
            </h2>
        </div>
        {linkPath && (
            <Link to={linkPath} className="btn btn-outline-danger rounded-pill px-3 py-1 font-13 fw-bold shadow-sm hover-lift d-flex align-items-center gap-1 transition">
                {linkText} <i className="bi bi-chevron-left font-12"></i>
            </Link>
        )}
    </div>
);

const StoryModal = ({ videoSrc, onClose }) => {
    useEffect(() => {
        if (videoSrc) document.body.style.overflow = 'hidden';
        return () => { document.body.style.overflow = 'unset'; };
    }, [videoSrc]);

    if (!videoSrc) return null;

    return (
        <div 
            className="position-fixed top-0 start-0 w-100 h-100 d-flex justify-content-center align-items-center animate-fade-in"
            style={{ backgroundColor: 'rgba(0, 0, 0, 0.95)', zIndex: 999999 }} 
            onClick={onClose}
        >
            <button 
                className="position-absolute top-0 end-0 m-4 btn btn-light rounded-circle d-flex align-items-center justify-content-center p-0 shadow-lg hover-lift" 
                style={{ width: '40px', height: '40px', zIndex: 9999999 }}
                onClick={onClose}
                title="بستن"
            >
                <i className="bi bi-x fs-4 text-dark"></i>
            </button>
            <div className="position-relative d-flex align-items-center justify-content-center w-100 h-100 p-4" onClick={(e) => e.stopPropagation()}>
                <video src={videoSrc} controls autoPlay className="rounded-4 shadow-lg bg-black" style={{ maxHeight: '90vh', maxWidth: '100%', objectFit: 'contain' }} />
            </div>
        </div>
    );
};

const StorySection = ({ stories }) => {
    const [activeVideo, setActiveVideo] = useState(null);
    if (!stories?.length) return null;

    return (
        <>
            <section className="story-section">
                <div className="container-fluid pt-4">
                    <h2 className="section-title visually-hidden">استوری‌ها</h2>
                    <Swiper modules={[FreeMode]} freeMode={true} slidesPerView="auto" className="my-unique-free-mode px-2">
                        {stories.map((story) => (
                            <SwiperSlide key={story.uuid || story.id} className="mx-3 pointer storiesList-slide hover-lift transition-all" style={{ width: 'auto' }}>
                                <div className="stories-Swiper-item d-flex flex-column align-items-center" onClick={() => story.video ? setActiveVideo(story.video) : null}>
                                    <div className="stories-Swiper-item-imgContainer position-relative d-flex justify-content-center align-items-center radius-circle shadow-sm" style={{ cursor: story.video ? 'pointer' : 'default', padding: '3px', background: 'linear-gradient(45deg, #ef4056, #ffc107)' }}>
                                        <div className="bg-white overflow-hidden radius-circle d-flex p-1 w-100 h-100">
                                            <div className="radius-circle overflow-hidden d-flex w-100 h-100">
                                                <img 
                                                    className="object-fit-cover w-100 h-100" 
                                                    src={story.image ? resolveImageUrl(story.image) : '/assets/image/product/product-no-bg.png'} 
                                                    alt={story.title} 
                                                    loading="lazy"
                                                    onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/product/product-no-bg.png'; }}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                    <span className="mt-2 text-subtitle color-gray-800 text-truncate-2 text-center font-12 fw-bold">{story.title}</span>
                                </div>
                            </SwiperSlide>
                        ))}
                    </Swiper>
                </div>
            </section>
            <StoryModal videoSrc={activeVideo} onClose={() => setActiveVideo(null)} />
        </>
    );
};

const MainSlider = ({ sliders }) => {
    if (!sliders?.length) return null;
    return (
        <section className="main-slider mt-4">
            <div className="container-fluid position-relative">
                <h2 className="section-title visually-hidden">اسلایدر</h2>
                <div className="slider">
                    <Swiper
                        modules={[Autoplay, Pagination, Navigation]}
                        spaceBetween={0} slidesPerView={1}
                        autoplay={{ delay: 5000, disableOnInteraction: false }} 
                        pagination={{ clickable: true }} 
                        navigation
                        className="rounded-4 overflow-hidden shadow-sm"
                    >
                        {sliders.map((slider) => (
                            <SwiperSlide key={slider.uuid || slider.id}>
                                <a href={slider.link || '#'}>
                                    <img 
                                        src={slider.image ? resolveImageUrl(slider.image) : '/assets/image/product/product-no-bg.png'} 
                                        className="img-fluid w-100" 
                                        style={{ maxHeight: '450px', objectFit: 'cover' }} 
                                        alt={slider.title} 
                                        onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/product/product-no-bg.png'; }}
                                    />
                                </a>
                            </SwiperSlide>
                        ))}
                    </Swiper>
                </div>
            </div>
        </section>
    );
};

const CategoriesSection = ({ categories }) => {
    if (!categories?.length) return null;
    return (
        <section className="card-categories site-slider mt-4 mb-5">
            <div className="container-fluid">
                <div className="row align-items-center gy-4">
                    <div className="col-lg-2">
                        <div className="d-lg-flex justify-content-lg-start">
                            <div className="d-flex align-items-center justify-content-lg-center justify-content-between flex-lg-column w-100">
                                <div className="d-flex flex-row flex-lg-column align-items-center align-items-lg-start gap-2 gap-lg-1">
                                    <h5 className="h3 fw-900 mb-0 text-dark">دسته بندی</h5>
                                    <h5 className="h3 fw-900 mb-0 text-danger">محصولات</h5>
                                </div>
                                <Link to="/categories" className="btn btn-sm mt-lg-4 px-4 btn-outline-danger rounded-pill fw-bold shadow-sm hover-lift transition-all d-flex align-items-center gap-1">
                                    مشاهده <i className="bi bi-chevron-left font-12"></i>
                                </Link>
                            </div>
                        </div>
                    </div>
                    <div className="col-lg-10">
                        <Swiper modules={[FreeMode, Navigation]} freeMode={true} slidesPerView="auto" navigation className="pro-slider py-4 px-2">
                            {categories.map(cat => {
                                const imgUrl = cat.image || cat.image_url || cat.icon || cat.logo;
                                return (
                                <SwiperSlide key={cat.uuid || cat.id} style={{ width: 'auto' }}>
                                    <Link to={`/category/${cat.slug}`} className="text-decoration-none">
                                        <div className="cat-item d-flex flex-column align-items-center mx-2 mx-md-3 group-cat-item">
                                            <div className="cat-item-image bg-white rounded-4 d-flex align-items-center justify-content-center mb-3 position-relative z-1 shadow-sm border border-ui" style={{ width: '110px', height: '110px', padding: '8px' }}>
                                                <div className="bg-light rounded-circle w-100 h-100 d-flex align-items-center justify-content-center overflow-hidden inner-cat-circle" style={{ transition: 'all 0.3s ease' }}>
                                                    <img 
                                                        src={imgUrl ? resolveImageUrl(imgUrl) : '/assets/image/category/kalaye-degital.png'} 
                                                        style={{ width: '65%', height: '65%', objectFit: 'contain', transition: 'transform 0.4s ease' }} 
                                                        alt={cat.title} 
                                                        className="cat-img"
                                                        onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/category/kalaye-degital.png'; }} 
                                                    />
                                                </div>
                                            </div>
                                            <div className="cat-item-desc text-center px-2">
                                                <h6 className="font-14 fw-bold text-dark transition-colors group-cat-text m-0">{cat.title}</h6>
                                            </div>
                                        </div>
                                    </Link>
                                </SwiperSlide>
                            )})}
                        </Swiper>
                    </div>
                </div>
            </div>
        </section>
    );
};

const SpecialOffers = ({ products }) => {
    if (!products?.length) return null;

    const now = new Date().getTime();

    const activeSpecialOffers = products.filter(p => {
        if (!p.special_offer_end) return false;
        const endDate = new Date(p.special_offer_end).getTime();
        return endDate > now;
    });

    if (activeSpecialOffers.length === 0) return null;

    let sectionEndTime = activeSpecialOffers.reduce((latest, current) => {
        const currentDate = new Date(current.special_offer_end).getTime();
        const latestDate = new Date(latest).getTime();
        return currentDate > latestDate ? current.special_offer_end : latest;
    }, activeSpecialOffers[0].special_offer_end);

    return (
        <section className="special-offers mt-4 mb-4">
            <div className="container-fluid">
                <div className="rounded-4 shadow-sm position-relative overflow-hidden d-flex flex-column flex-xl-row align-items-center p-3 p-md-4 gap-4" style={{ background: 'linear-gradient(135deg, #ef4056 0%, #d32f44 100%)' }}>
                    
                    <div className="position-absolute top-0 end-0 opacity-10" style={{ pointerEvents: 'none' }}>
                        <svg width="250" height="250" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="100" cy="0" r="80" fill="white"/>
                        </svg>
                    </div>

                    <div className="d-flex flex-column justify-content-center align-items-center align-items-xl-start text-center text-xl-start text-white ms-xl-3 position-relative z-2" style={{ minWidth: '180px' }}>
                        <div className="mb-3 d-none d-xl-block">
                            <i className="bi bi-percent rounded-circle bg-white text-danger d-flex align-items-center justify-content-center shadow" style={{width: '60px', height: '60px', fontSize: '30px'}}></i>
                        </div>
                        <h3 className="fw-900 fs-3 mb-1">پیشنهادات</h3>
                        <h3 className="fw-900 fs-3 mb-3">شگفت‌انگیز</h3>
                        
                        {sectionEndTime && (
                            <div className="mb-4 d-flex justify-content-center w-100" style={{ minHeight: '35px' }}>
                                <CountdownTimer endTime={sectionEndTime} variant="white" />
                            </div>
                        )}

                        <Link to="/special-offers" className="btn btn-light rounded-pill px-4 py-2 fw-bold text-danger font-14 shadow-sm transition hover-lift d-flex align-items-center gap-1">
                            مشاهده همه <i className="bi bi-chevron-left align-middle"></i>
                        </Link>
                    </div>
                    
                    <div className="position-relative flex-grow-1 w-100" style={{ zIndex: 10, minWidth: 0 }}>
                        <Swiper 
                            modules={[Navigation]} 
                            slidesPerView={1.2} 
                            spaceBetween={15} 
                            breakpoints={{ 576: { slidesPerView: 2.2 }, 768: { slidesPerView: 3.2 }, 992: { slidesPerView: 4.2 }, 1400: { slidesPerView: 4.5 } }} 
                            navigation 
                            className="pb-2 px-1"
                        >
                            {activeSpecialOffers.map(product => (
                                <SwiperSlide key={product.uuid || product.id} className="h-auto">
                                    <ProductCard product={product} />
                                </SwiperSlide>
                            ))}
                        </Swiper>
                    </div>
                    
                </div>
            </div>
        </section>
    );
};

const BannersSection = ({ banners }) => {
    if (!banners?.length) return null;
    return (
        <section className="banner mt-4 pb-md-3 pb-0">
            <div className="container-fluid">
                <h2 className="section-title visually-hidden">بنر های تبلیغاتی</h2>
                <div className="row gy-3">
                    {banners.slice(0, 2).map((banner) => (
                        <div className="col-md-6" key={banner.uuid || banner.id}>
                            <a href={banner.link || '#'}>
                                <div className="banner-image-parent shadow-sm rounded-4 overflow-hidden d-block hover-lift">
                                    <img 
                                        className="img-fluid w-100" 
                                        style={{transition: 'transform 0.4s ease'}} 
                                        src={banner.image ? resolveImageUrl(banner.image) : '/assets/image/product/product-no-bg.png'} 
                                        alt={banner.title} 
                                        loading="lazy" 
                                        onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/product/product-no-bg.png'; }}
                                    />
                                </div>
                            </a>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
};

const BestSellers = ({ products, sideBanner }) => {
    if (!products?.length) return null;
    return (
        <section className="product-slider mt-4">
            <div className="container-fluid">
                <SectionTitle title="پرفروش ترین" highlight="محصولات" linkPath="/best-sellers" />
                <div className="row gy-3 mt-3">
                    <div className="col-md-3 d-none d-md-block">
                        <a href={sideBanner?.link || "/best-sellers"}>
                            <div className="banner-image-parent h-100 shadow-sm rounded-4 overflow-hidden d-block hover-lift">
                                <img 
                                    className="img-fluid w-100 h-100 object-fit-cover" 
                                    style={{transition: 'transform 0.4s ease'}} 
                                    src={sideBanner?.image ? resolveImageUrl(sideBanner.image) : "/assets/image/product/product_cover_1.png"} 
                                    alt={sideBanner?.title || "بنر محصولات پرفروش"} 
                                    onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/product/product_cover_1.png'; }}
                                />
                            </div>
                        </a>
                    </div>
                    <div className="col-md-12 col-lg-9">
                        <Swiper 
                            modules={[Navigation]} 
                            slidesPerView={1.5} 
                            spaceBetween={15} 
                            breakpoints={{ 576: { slidesPerView: 2.5 }, 992: { slidesPerView: 3.5 }, 1200: { slidesPerView: 4 } }} 
                            navigation 
                            className="pro-slider-with-cover h-100 pb-2 px-1"
                        >
                            {products.map(product => (
                                <SwiperSlide key={product.uuid || product.id} className="h-auto">
                                    <ProductCard product={product} />
                                </SwiperSlide>
                            ))}
                        </Swiper>
                    </div>
                </div>
            </div>
        </section>
    );
};

const ProductGroupGrid = ({ groups }) => {
    if (!groups?.length) return null;
    return (
        <section className="product-group mt-5">
            <div className="container-fluid">
                <div className="border bg-white slider-parent border-ui px-3 rounded-4 py-4 shadow-sm">
                    <div className="row gy-4">
                        {groups.map((group, groupIndex) => (
                            <div className="col-lg-3 col-sm-6 border-end-lg" key={groupIndex}>
                                <div className="product-group-item px-2">
                                    <h5 className="fw-bold text-dark ms-1 mb-2">دسته‌بندی {groupIndex + 1}</h5>
                                    <p className="text-muted font-12 mb-3">بر اساس سلیقه شما</p>
                                    <div className="row gy-3">
                                        {group.map((product) => (
                                            <div className="col-6" key={product.uuid || product.id}>
                                                <Link to={`/product/${product.slug || product.uuid || product.id}`} className="hover-lift d-block">
                                                    <img 
                                                        src={product.gallery?.[0]?.url ? resolveImageUrl(product.gallery[0].url) : '/assets/image/product/product-no-bg.png'} 
                                                        className="img-fluid rounded border border-ui p-1 transition" 
                                                        alt={product.title} 
                                                        style={{height: '100px', objectFit:'contain', width:'100%'}} 
                                                        onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/product/product-no-bg.png'; }} 
                                                    />
                                                </Link>
                                            </div>
                                        ))}
                                    </div>
                                    <div className="text-center py-3 mt-2">
                                        <Link to="/shop" className="text-danger fw-bold font-13 hover-text-dark transition d-flex align-items-center justify-content-center gap-1">مشاهده همه <i className="bi bi-chevron-left font-12"></i></Link>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
};

const BrandsSection = ({ brands }) => {
    if (!brands?.length) return null;
    return (
        <section className="product-slider brand-box mt-5">
            <div className="container-fluid">
                <SectionTitle title="محبوب ترین" highlight="برندها" linkPath="/brands" />
                <Swiper modules={[Autoplay, Navigation]} slidesPerView={2.5} spaceBetween={15} breakpoints={{ 576: { slidesPerView: 4 }, 768: { slidesPerView: 6 }, 1024: { slidesPerView: 8 } }} autoplay={{ delay: 3000 }} navigation className="pro-slider py-3 px-1">
                    {brands.map(brand => (
                        <SwiperSlide key={brand.uuid || brand.id}>
                            <Link to={`/shop?brands=${brand.slug}`} className="d-block text-center border-ui bg-white rounded-3 p-3 shadow-sm hover-lift">
                                <img 
                                    src={brand.logo ? resolveImageUrl(brand.logo) : '/assets/image/brand/brand1-1.png'} 
                                    className="img-fluid" 
                                    style={{height: '60px', objectFit: 'contain', filter: 'grayscale(100%)', opacity: '0.7', transition: 'all 0.3s'}} 
                                    onMouseOver={e => {e.currentTarget.style.filter='none'; e.currentTarget.style.opacity='1'}} 
                                    onMouseOut={e => {e.currentTarget.style.filter='grayscale(100%)'; e.currentTarget.style.opacity='0.7'}} 
                                    alt={brand.title} 
                                    onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/brand/brand1-1.png'; }}
                                />
                            </Link>
                        </SwiperSlide>
                    ))}
                </Swiper>
            </div>
        </section>
    );
};

const BlogSection = ({ posts }) => {
    if (!posts?.length) return null;
    return (
        <section className="blog-slider mt-5 mb-5">
            <div className="container-fluid">
                <SectionTitle title="آخرین مطالب" highlight="وبلاگ" linkPath="/blog" />
                
                <Swiper 
                    modules={[Navigation]} 
                    slidesPerView={1.2} 
                    spaceBetween={20} 
                    breakpoints={{ 768: { slidesPerView: 3 }, 1200: { slidesPerView: 4 } }} 
                    navigation 
                    className="mt-4 blog-slider-sw pb-5 pt-3 px-2" 
                >
                    {posts.map(post => (
                        <SwiperSlide key={post.uuid || post.id}>
                            <div className="card blog-card border-0 bg-transparent overflow-visible hover-lift">
                                <div className="card-img position-relative z-0">
                                    <img 
                                        src={post.image ? resolveImageUrl(post.image) : '/assets/image/blog/blog-1.jpg'} 
                                        className="img-fluid rounded-4 w-100 object-fit-cover" 
                                        style={{height: '240px'}}
                                        alt={post.title} 
                                        loading="lazy" 
                                        onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/blog/blog-1.jpg'; }}
                                    />
                                </div>
                                <div 
                                    className="card-body bg-white rounded-4 shadow-sm border-ui position-relative mx-3" 
                                    style={{ marginTop: '-40px', zIndex: 2 }}
                                >
                                    <h6 className="text-overflow-2 h6 fw-bold mb-3 text-dark lh-lg">{post.title}</h6>
                                    <div className="d-flex mt-4 align-items-center justify-content-between border-top pt-3">
                                        <div className="text-muted font-12 d-flex align-items-center">
                                            <i className="bi bi-calendar2-week fs-5 ms-2"></i>
                                            <span className="pt-1">{post.read_time || '۱۲'} دقیقه مطالعه</span>
                                        </div>
                                        <Link to={`/blog/${post.slug}`} className="btn btn-sm btn-danger text-white rounded-pill px-3 py-1 d-flex align-items-center gap-1 shadow-sm transition">
                                            مشاهده <i className="bi bi-arrow-left-short fs-5"></i>
                                        </Link>
                                    </div>
                                </div>
                            </div>
                        </SwiperSlide>
                    ))}
                </Swiper>
            </div>
        </section>
    );
};

const HomePage = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await getHomePageData();
                setData(response);
            } catch (error) {
                console.error("Error fetching home data:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return (
        <div className="d-flex flex-column justify-content-center align-items-center min-vh-100 bg-light">
            <div className="spinner-border text-danger mb-3" style={{width: '3.5rem', height:'3.5rem', borderWidth: '0.25rem'}} role="status"></div>
            <h6 className="fw-bold text-muted animate-pulse">در حال بارگذاری صفحه اصلی...</h6>
        </div>
    );

    if (!data) return <div className="text-center mt-5 min-vh-100 pt-5"><h2 className="text-danger fw-bold">خطا در دریافت اطلاعات از سرور</h2></div>;

    const topBanners = data.banners?.filter(b => b.position !== 'best_sellers_side');
    const bestSellersBanner = data.banners?.find(b => b.position === 'best_sellers_side');

    const chunkArray = (arr, size) => arr.length ? [arr.slice(0, size), ...chunkArray(arr.slice(size), size)] : [];
    const productGroups = chunkArray(data.best_sellers || [], 4).slice(0, 4);

    return (
        <main>
            <StorySection stories={data.stories} />
            <MainSlider sliders={data.sliders} />
            <CategoriesSection categories={data.categories} />
            <SpecialOffers products={data.special_offers} />
            <BannersSection banners={topBanners} />
            <BestSellers products={data.best_sellers} sideBanner={bestSellersBanner} />
            <ProductGroupGrid groups={productGroups} />
            <BrandsSection brands={data.brands} />
            <BlogSection posts={data.latest_posts} />

            <style jsx="true">{`
                .hover-lift { transition: transform 0.2s ease, box-shadow 0.2s ease; }
                .hover-lift:hover { transform: translateY(-4px); box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important; }
                .hover-text-danger:hover { color: #ef4056 !important; }
                .hover-text-dark:hover { color: #212529 !important; }
                .transition-all { transition: all 0.3s ease; }
                .animate-fade-in { animation: fadeIn 0.3s ease-in-out; }
                @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
                
                .group-cat-item { cursor: pointer; }
                .group-cat-item:hover .inner-cat-circle { 
                    border-color: #ef4056 !important; 
                    box-shadow: 0 0 0 4px rgba(239, 64, 86, 0.15) !important; 
                }
                .group-cat-item:hover .cat-img { transform: scale(1.15) !important; }
                .group-cat-item:hover .group-cat-text { color: #ef4056 !important; }
                
                .text-overflow-2 { overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
                
                @media (min-width: 992px) {
                    .border-end-lg { border-left: 1px solid #dee2e6; }
                    .border-end-lg:last-child { border-left: none; }
                }
            `}</style>
        </main>
    );
};

export default HomePage;