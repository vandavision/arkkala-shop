import React, { useState, useEffect, useContext, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Swiper, SwiperSlide } from 'swiper/react';
import { FreeMode, Navigation, Thumbs, Zoom, EffectFade, Autoplay } from 'swiper/modules';
import Chart from 'chart.js/auto';
import { getProductDetail, submitComment, submitQuestion, getProductsList, toggleFavorite } from '../api/shopApi';
import { CartContext } from '../context/CartContext';
import { AuthContext } from '../context/AuthContext';
import { CompareContext } from '../context/CompareContext';
import SeoMeta from '../components/SeoMeta';
import CountdownTimer from '../components/CountdownTimer';

import 'swiper/css';
import 'swiper/css/free-mode';
import 'swiper/css/navigation';
import 'swiper/css/thumbs';
import 'swiper/css/zoom';
import 'swiper/css/effect-fade';

const resolveImageUrl = (url) => {
    if (!url) return '/assets/image/product/product-no-bg.png';
    if (url.startsWith('http') || url.startsWith('data:')) return url;
    
    let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    baseUrl = baseUrl.replace(/\/api\/?$/, '');
    
    return `${baseUrl}${url.startsWith('/') ? '' : '/'}${url}`;
};

const ProductDetailPage = () => {
    const { slug, id } = useParams();
    const productIdentifier = slug || id;

    const { user } = useContext(AuthContext);
    const { addToCart } = useContext(CartContext);
    const { addToCompare } = useContext(CompareContext);
    
    const chartRef = useRef(null);
    const chartInstance = useRef(null);

    const [product, setProduct] = useState(null);
    const [suggestedProducts, setSuggestedProducts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [thumbsSwiper, setThumbsSwiper] = useState(null);
    const [activeTab, setActiveTab] = useState('desc'); 

    const [selectedOptions, setSelectedOptions] = useState({});
    const [selectedVariant, setSelectedVariant] = useState(null);
    const [quantity, setQuantity] = useState(1);
    const [hasInsurance, setHasInsurance] = useState(false);
    const [isAddingToCart, setIsAddingToCart] = useState(false);
    
    const [isFavorite, setIsFavorite] = useState(false);

    const [rating, setRating] = useState(5);
    const [commentBody, setCommentBody] = useState('');
    const [pros, setPros] = useState('');
    const [cons, setCons] = useState('');
    const [submittingComment, setSubmittingComment] = useState(false);

    const [questionText, setQuestionText] = useState('');
    const [guestName, setGuestName] = useState('');
    const [submittingQuestion, setSubmittingQuestion] = useState(false);

    const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
    const showToast = (message, type = 'success') => {
        setToast({ show: true, message, type });
        setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 4000);
    };

    useEffect(() => {
        if (!productIdentifier) return;
        let isMounted = true;

        const fetchProduct = async () => {
            try {
                setLoading(true);
                const data = await getProductDetail(productIdentifier);
                
                if (isMounted) {
                    setProduct(data);
                    setIsFavorite(data.is_favorite || false);
                    
                    if (data.is_variable && data.variants && data.variants.length > 0) {
                        const initialOptions = {};
                        data.variants[0].attributes.forEach(attr => {
                            initialOptions[attr.attribute_name] = attr.value;
                        });
                        setSelectedOptions(initialOptions);
                        setSelectedVariant(data.variants[0]);
                    }
                }

                if (data.category && data.category.slug) {
                    try {
                        const related = await getProductsList(`category__slug=${data.category.slug}`);
                        const filteredRelated = (related.results || related).filter(p => p.uuid !== data.uuid);
                        if (isMounted) setSuggestedProducts(filteredRelated);
                    } catch (err) {
                        console.error("Error fetching related products:", err);
                    }
                }
            } catch (err) {
                if (isMounted) setError("محصول مورد نظر یافت نشد.");
            } finally {
                if (isMounted) setLoading(false);
            }
        };

        fetchProduct();
        window.scrollTo(0, 0);

        return () => {
            isMounted = false;
        };
    }, [productIdentifier]);

    useEffect(() => {
        const modalElement = document.getElementById('chartModal');
        
        if (modalElement && product) {
            const handleModalShown = () => {
                if (typeof window === 'undefined' || !Chart) {
                    console.warn("Chart.js is not loaded.");
                    return;
                }

                if (chartInstance.current) {
                    chartInstance.current.destroy();
                }

                const ctx = chartRef.current?.getContext('2d');
                if (!ctx) return;
                
                Chart.defaults.font.family = "payda"; 

                const hasHistory = product.price_history && product.price_history.length > 0;
                const labels = hasHistory 
                    ? product.price_history.map(ph => new Date(ph.created_at).toLocaleDateString('fa-IR', { month: 'short', day: 'numeric' }))
                    : ['هم‌اکنون'];
                    
                const dataPoints = hasHistory 
                    ? product.price_history.map(ph => Number(ph.price))
                    : [Number(product.base_price)];

                const gradient = ctx.createLinearGradient(0, 0, 0, 400);
                gradient.addColorStop(0, 'rgba(239, 64, 86, 0.4)');
                gradient.addColorStop(1, 'rgba(239, 64, 86, 0)');

                chartInstance.current = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: labels,
                        datasets: [{
                            label: 'قیمت فروش (تومان)',
                            data: dataPoints,
                            borderWidth: 3,
                            borderColor: '#ef4056',
                            backgroundColor: gradient,
                            fill: true,
                            pointBackgroundColor: '#fff',
                            pointBorderColor: '#ef4056',
                            pointBorderWidth: 2,
                            pointRadius: 6,
                            pointHoverRadius: 8,
                            tension: 0.4,
                        }]
                    },
                    options: { 
                        responsive: true, 
                        maintainAspectRatio: false,
                        plugins: { 
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    label: function(context) {
                                        let label = context.dataset.label || '';
                                        if (label) label += ': ';
                                        if (context.parsed.y !== null) {
                                            label += new Intl.NumberFormat('fa-IR').format(context.parsed.y) + ' تومان';
                                        }
                                        return label;
                                    }
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: false,
                                ticks: {
                                    callback: function(value) {
                                        return new Intl.NumberFormat('fa-IR').format(value);
                                    }
                                }
                            }
                        }
                    }
                });
            };

            const handleModalHidden = () => {
                if (chartInstance.current) {
                    chartInstance.current.destroy();
                    chartInstance.current = null;
                }
            };

            modalElement.addEventListener('shown.bs.modal', handleModalShown);
            modalElement.addEventListener('hidden.bs.modal', handleModalHidden);

            return () => {
                modalElement.removeEventListener('shown.bs.modal', handleModalShown);
                modalElement.removeEventListener('hidden.bs.modal', handleModalHidden);
            };
        }
    }, [product]);

    const handleOptionChange = (attributeName, value) => {
        const newOptions = { ...selectedOptions, [attributeName]: value };
        setSelectedOptions(newOptions);
        if (product?.variants) {
            const matchedVariant = product.variants.find(variant => 
                variant.attributes.every(attr => newOptions[attr.attribute_name] === attr.value)
            );
            setSelectedVariant(matchedVariant || null);
            setQuantity(1); 
        }
    };

    const handleAddToCart = async (e) => {
        e.preventDefault();
        const currentInventory = selectedVariant ? selectedVariant.inventory : product?.base_inventory || 0;
        
        if (currentInventory === 0) {
            return showToast("این کالا در حال حاضر ناموجود است.", "danger");
        }
        if (quantity > currentInventory) {
            return showToast(`حداکثر موجودی قابل سفارش ${currentInventory} عدد است.`, "warning");
        }
        
        try {
            setIsAddingToCart(true);
            if (addToCart) {
                const variantId = selectedVariant ? selectedVariant.uuid : null;
                await addToCart(product.uuid, variantId, quantity);
                showToast("محصول با موفقیت به سبد خرید اضافه شد.", "success");
            }
        } catch (error) {
            if(error.response?.status !== 401) {
                showToast(error.response?.data?.error || "خطا در افزودن به سبد خرید. لطفا مجدد تلاش کنید.", "danger");
            }
        } finally {
            setIsAddingToCart(false);
        }
    };

    const handleToggleFavorite = async () => {
        if (!user) {
            showToast("برای استفاده از لیست علاقه‌مندی‌ها، لطفاً وارد حساب کاربری خود شوید.", "warning");
            return;
        }
        try {
            const result = await toggleFavorite(productIdentifier);
            setIsFavorite(result.is_favorite);
            showToast(result.message, "success");
        } catch (err) {
            showToast("خطا در برقراری ارتباط با سرور.", "danger");
        }
    };

    const handleCompareClick = (e) => {
        e.preventDefault();
        if (product) {
            addToCompare(product.uuid);
        }
    };

    const handleCommentSubmit = async (e) => {
        e.preventDefault();
        if (!commentBody.trim()) return showToast("لطفاً متن نظر را وارد کنید.", "warning");
        setSubmittingComment(true);
        const fullBodyText = `نقاط قوت: ${pros || 'ندارد'}\nنقاط ضعف: ${cons || 'ندارد'}\n\nتوضیحات: ${commentBody}`;
        try {
            await submitComment(productIdentifier, { body: fullBodyText, rating });
            showToast("دیدگاه شما ثبت شد و پس از تایید نمایش داده می‌شود.", "success");
            setCommentBody(''); setPros(''); setCons(''); setRating(5);
        } catch (err) {
            showToast("خطا در ثبت نظر. لطفاً مجدداً تلاش کنید.", "danger");
        } finally {
            setSubmittingComment(false);
        }
    };

    const handleQuestionSubmit = async (e) => {
        e.preventDefault();
        if (!questionText.trim()) return showToast("لطفاً متن پرسش را وارد کنید.", "warning");
        setSubmittingQuestion(true);
        try {
            const payload = { text: questionText };
            if (!user) payload.name = guestName.trim() || "کاربر مهمان";
            await submitQuestion(productIdentifier, payload);
            showToast("پرسش شما با موفقیت ثبت شد.", "success");
            setQuestionText(''); setGuestName('');
        } catch (err) {
            showToast("خطا در ثبت پرسش. لطفاً مجدداً تلاش کنید.", "danger");
        } finally {
            setSubmittingQuestion(false);
        }
    };

    const copyToClipboard = () => {
        navigator.clipboard.writeText(window.location.href)
            .then(() => showToast("لینک کالا با موفقیت کپی شد.", "success"))
            .catch(() => showToast("خطا در کپی کردن لینک.", "danger"));
    };

    if (loading) return <div className="text-center py-5 my-5 min-vh-100 d-flex align-items-center justify-content-center"><div className="spinner-border text-danger" style={{width: '4rem', height:'4rem', borderWidth:'0.3rem'}} aria-label="در حال بارگذاری"></div></div>;
    if (error || !product) return <div className="text-center py-5 my-5 text-danger min-vh-100 d-flex flex-column align-items-center justify-content-center"><i className="bi bi-exclamation-triangle fs-1 mb-3"></i><h2 className="fw-bold mb-4">{error}</h2><Link to="/shop" className="btn btn-danger rounded-pill px-5 py-3 shadow-sm hover-lift fw-bold">بازگشت به فروشگاه</Link></div>;

    const allImages = product.gallery && product.gallery.length > 0 
        ? product.gallery.map(img => ({ ...img, url: resolveImageUrl(img.url) }))
        : [{ url: resolveImageUrl(product.image_url || product.image), is_main: true, image_alt: product.title }];
        
    const mainVideo = product.videos?.length 
        ? { ...product.videos[0], url: resolveImageUrl(product.videos[0].url) } 
        : null;

    let originalPrice = product.is_variable && selectedVariant ? selectedVariant.price : product.base_price;
    let currentInventory = product.is_variable && selectedVariant ? selectedVariant.inventory : product.base_inventory || 0;
    
    let currentPrice = originalPrice;
    let hasDiscount = false;
    let discountPercent = 0;
    let isWholesaleActive = false;

    if (product.is_wholesale && quantity >= product.wholesale_min_quantity) {
        let wholesalePr = product.is_variable && selectedVariant ? selectedVariant.wholesale_price : product.wholesale_base_price;
        if (wholesalePr) {
            currentPrice = wholesalePr;
            isWholesaleActive = true;
            hasDiscount = true;
            discountPercent = Math.round(((originalPrice - wholesalePr) / originalPrice) * 100);
        }
    }

    if (product.is_special_offer && product.special_discount_percent > 0) {
        let specialPriceCalculated = originalPrice * (1 - (product.special_discount_percent / 100));
        if (specialPriceCalculated < currentPrice) {
            currentPrice = specialPriceCalculated;
            isWholesaleActive = false; 
            hasDiscount = true;
            discountPercent = product.special_discount_percent;
        }
    }

    const availableAttributes = {};
    if (product.is_variable && product.variants) {
        product.variants.forEach(variant => {
            variant.attributes.forEach(attr => {
                if (!availableAttributes[attr.attribute_name]) availableAttributes[attr.attribute_name] = new Set();
                availableAttributes[attr.attribute_name].add(attr.value);
            });
        });
    }

    return (
        <React.Fragment>
            {product && <SeoMeta 
                seoData={product.seo || product} 
                fallbackTitle={product.title} 
                price={currentPrice} 
                inventory={currentInventory} 
                customImage={allImages[0]?.url} 
                customSchema={product.seo?.schema_markup || product.json_ld || product.seo?.json_ld}
                slug={product.slug}
            />}

            <div className={`custom-toast ${toast.show ? 'show' : ''} bg-${toast.type} shadow-lg d-flex align-items-center gap-3`} role="alert" aria-live="assertive" aria-atomic="true">
                <i className={`bi ${toast.type === 'success' ? 'bi-check-circle-fill' : toast.type === 'warning' ? 'bi-exclamation-triangle-fill' : 'bi-x-circle-fill'} fs-3 text-white`}></i>
                <span className="font-14 fw-bold text-white lh-base">{toast.message}</span>
            </div>

            <section className="bread-crumb py-0 mb-3 mt-3">
                <div className="container-fluid">
                    <div className="content-box border-0 shadow-sm rounded-4 bg-white">
                        <nav aria-label="breadcrumb">
                            <ol className="breadcrumb mb-0 py-3 px-3 px-md-4">
                                <li className="breadcrumb-item"><Link to="/" className="font-13 font-md-14 text-muted text-decoration-none hover-text-danger transition"><i className="bi bi-house me-1"></i>خانه</Link></li>
                                <li className="breadcrumb-item"><Link to="/shop" className="font-13 font-md-14 text-muted text-decoration-none hover-text-danger transition">فروشگاه</Link></li>
                                {product.category && (
                                    <li className="breadcrumb-item"><Link to={`/shop?category__slug=${product.category.slug}`} className="font-13 font-md-14 text-muted text-decoration-none hover-text-danger transition">{product.category.title}</Link></li>
                                )}
                                <li className="breadcrumb-item active text-danger font-13 font-md-14 fw-bold text-overflow-1" aria-current="page">{product.title}</li>
                            </ol>
                        </nav>
                    </div>
                </div>
            </section>

            <section className="content">
                <div className="container-fluid">
                    <div className="content-box bg-transparent p-0 border-0">
                        <div className="row gy-4">
                            
                            <div className="col-12 col-lg-4">
                                <div className="pro_gallery position-relative bg-white p-3 p-md-4 rounded-4 shadow-sm border border-ui h-lg-100">
                                    <div className="icon-product-box mt-3 me-3 z-3">
                                        {mainVideo && (
                                            <button className="btn p-0 icon-product-box-item hint--left cursor-pointer bg-light border border-ui shadow-sm hover-lift text-danger" data-bs-toggle="modal" data-bs-target="#videoModal" aria-label="ویدیو معرفی">
                                                <i className="bi bi-play-fill fs-5"></i>
                                            </button>
                                        )}
                                        <button className="btn p-0 icon-product-box-item hint--left cursor-pointer bg-light border border-ui shadow-sm hover-lift" data-bs-toggle="modal" data-bs-target="#shareModal" aria-label="اشتراک گذاری">
                                            <i className="bi bi-share-fill"></i>
                                        </button>
                                        <button onClick={handleToggleFavorite} className={`btn p-0 icon-product-box-item hint--left cursor-pointer bg-light border border-ui shadow-sm hover-lift ${isFavorite ? 'active-favorite' : ''}`} aria-label={isFavorite ? "حذف از علاقه‌مندی‌ها" : "افزودن به علاقه‌مندی‌ها"}>
                                            <i className={isFavorite ? "bi bi-heart-fill text-danger pulse-animation" : "bi bi-heart text-dark"}></i>
                                        </button>
                                        <button className="btn p-0 icon-product-box-item hint--left cursor-pointer bg-light border border-ui shadow-sm hover-lift" data-bs-toggle="modal" data-bs-target="#chartModal" aria-label="نمودار قیمت">
                                            <i className="bi bi-bar-chart-line-fill text-primary"></i>
                                        </button>
                                        <button onClick={handleCompareClick} className="btn p-0 icon-product-box-item hint--left cursor-pointer bg-light border border-ui shadow-sm hover-lift" aria-label="افزودن به مقایسه">
                                            <i className="bi bi-shuffle text-success"></i>
                                        </button>
                                    </div>

                                    <div className="position-absolute z-3 top-0 start-0 mt-4 ms-4 d-flex flex-column gap-2">
                                        {product.is_special_offer && <span className="badge bg-danger shadow-sm px-3 py-2 rounded-pill font-13 fw-bold animate-pulse d-flex align-items-center gap-1"><i className="bi bi-lightning-charge-fill text-warning fs-6"></i> پیشنهاد شگفت‌انگیز</span>}
                                        {isWholesaleActive && !product.is_special_offer && <span className="badge bg-info text-dark shadow-sm px-3 py-2 rounded-pill font-13 fw-bold">قیمت عمده فعال</span>}
                                        {currentInventory === 0 && <span className="badge bg-secondary shadow-sm px-3 py-2 rounded-pill font-13 fw-bold">ناموجود</span>}
                                    </div>

                                    <Swiper
                                        dir="rtl"
                                        style={{ '--swiper-navigation-color': '#ef4056', '--swiper-pagination-color': '#ef4056' }}
                                        spaceBetween={10}
                                        navigation={true}
                                        thumbs={{ swiper: thumbsSwiper && !thumbsSwiper.destroyed ? thumbsSwiper : null }}
                                        modules={[FreeMode, Navigation, Thumbs, Zoom, EffectFade]}
                                        effect="fade"
                                        zoom={true}
                                        className="product-gallery mb-3 rounded-4 mt-3"
                                    >
                                        {allImages.map((img, idx) => (
                                            <SwiperSlide key={idx} title="برای بزرگنمایی دابل کلیک کنید">
                                                <div className="swiper-zoom-container bg-white">
                                                    <img 
                                                        src={img.url} 
                                                        alt={img.image_alt || product.title} 
                                                        title={img.image_alt || product.title} 
                                                        className="img-fluid object-fit-contain main-gallery-img" 
                                                        fetchpriority={idx === 0 ? "high" : "auto"} 
                                                        loading={idx === 0 ? "eager" : "lazy"}
                                                        decoding="async"
                                                        onError={(e) => { e.target.src = '/assets/image/product/product-no-bg.png'; }} 
                                                    />
                                                </div>
                                            </SwiperSlide>
                                        ))}
                                    </Swiper>

                                    <Swiper
                                        dir="rtl"
                                        onSwiper={setThumbsSwiper}
                                        spaceBetween={12}
                                        slidesPerView={4}
                                        freeMode={true}
                                        watchSlidesProgress={true}
                                        modules={[FreeMode, Navigation, Thumbs]}
                                        className="product-gallery-thumb"
                                    >
                                        {allImages.map((img, idx) => (
                                            <SwiperSlide key={idx} className="cursor-pointer bg-white rounded-3 border border-ui p-1 hover-shadow transition">
                                                <img 
                                                    src={img.url} 
                                                    alt={img.image_alt || `گالری تصویر ${idx + 1} از ${product.title}`} 
                                                    className="img-fluid object-fit-contain rounded-2" 
                                                    style={{height:'75px', width:'100%'}} 
                                                    loading="lazy" 
                                                    decoding="async"
                                                    onError={(e) => { e.target.src = '/assets/image/product/product-no-bg.png'; }} 
                                                />
                                            </SwiperSlide>
                                        ))}
                                    </Swiper>
                                </div>
                            </div>

                            <div className="col-12 col-lg-4">
                                <div className="product-meta bg-white p-4 p-md-5 rounded-4 shadow-sm border border-ui h-lg-100 d-flex flex-column">
                                    {product.brand && (
                                        <div className="mb-3">
                                            <Link to={`/shop?brands=${product.brand.slug}`} className="text-danger font-14 fw-bold text-decoration-none hover-text-dark transition d-flex align-items-center gap-2 w-fit-content px-3 py-1 bg-danger bg-opacity-10 rounded-pill">
                                                <i className="bi bi-tag-fill"></i> {product.brand.title}
                                            </Link>
                                        </div>
                                    )}
                                    <h1 className="fs-5 mb-3 lh-base fw-900 text-dark">{product.title}</h1>
                                    {product.english_title && <p className="font-13 text-muted font-en mb-4">{product.english_title}</p>}
                                    
                                    {/* Content Freshness Indicator */}
                                    {product.modified_at && (
                                        <div className="mb-3">
                                            <span className="font-11 text-muted">آخرین بروزرسانی: <time dateTime={product.modified_at}>{new Date(product.modified_at).toLocaleDateString('fa-IR')}</time></span>
                                        </div>
                                    )}

                                    {/* GEO: Expert Reviewer Badge */}
                                    {product.expert_reviewer && (
                                        <div className="alert bg-success bg-opacity-10 border border-success border-opacity-25 rounded-pill py-2 px-3 d-inline-flex align-items-center gap-2 mb-3 shadow-sm w-fit-content">
                                            <i className="bi bi-patch-check-fill text-success fs-5"></i>
                                            <span className="font-12 text-dark fw-bold">بررسی و تایید شده توسط: {product.expert_reviewer}</span>
                                        </div>
                                    )}

                                    <div className="d-flex align-items-center pb-4 border-bottom border-light flex-wrap gap-3 gap-md-4">
                                        <div className="d-flex align-items-center bg-warning bg-opacity-10 px-3 py-1 rounded-pill border border-warning border-opacity-25" aria-label={`امتیاز ${product.average_rating.toFixed(1)} از 5`}>
                                            <i className="bi bi-star-fill text-warning me-2"></i>
                                            <span className="text-dark fw-bold font-14 pt-1">{product.average_rating.toFixed(1)}</span>
                                        </div>
                                        <div className="d-flex align-items-center text-muted font-13">
                                            <i className="bi bi-chat-text me-2"></i> {product.comments?.length || 0} دیدگاه
                                        </div>
                                        <div className="d-flex align-items-center text-success font-13 fw-bold">
                                            <i className="bi bi-cart-check-fill me-2"></i> {product.sold_count} فروش
                                        </div>
                                    </div>

                                    <div className="product-feature py-4">
                                        <h2 className="font-16 mb-3 fw-bold text-dark d-flex align-items-center gap-2"><i className="bi bi-card-checklist text-primary"></i> ویژگی‌های برتر</h2>
                                        
                                        {/* GEO: Explicit Key Takeaways Rendering if available */}
                                        {product.key_takeaways && Array.isArray(product.key_takeaways) && product.key_takeaways.length > 0 ? (
                                            <ul className="list-unstyled m-0 p-0 d-flex flex-column gap-3 mb-4">
                                                {product.key_takeaways.map((kt, idx) => (
                                                    <li key={idx} className="font-13 text-dark d-flex align-items-start fw-semibold"><i className="bi bi-check-circle-fill text-success me-2 fs-5"></i>{kt}</li>
                                                ))}
                                            </ul>
                                        ) : product.short_description ? (
                                            <p className="font-14 text-muted text-justify lh-lg m-0">{product.short_description}</p>
                                        ) : (
                                            <ul className="list-unstyled m-0 p-0 d-flex flex-column gap-3">
                                                {product.variants?.[0]?.attributes.slice(0,5).map((attr, idx) => (
                                                    <li key={idx} className="font-13 text-muted d-flex align-items-center"><i className="bi bi-check2-circle text-success me-2 fs-5"></i><span className="fw-bold text-dark me-2">{attr.attribute_name}:</span> {attr.value}</li>
                                                ))}
                                            </ul>
                                        )}
                                    </div>
                                    
                                    <div className="alert bg-primary bg-opacity-10 border border-primary border-opacity-25 rounded-4 p-3 d-flex align-items-start gap-3 mt-auto mb-0">
                                        <i className="bi bi-shield-check text-primary fs-3"></i>
                                        <span className="text-justify font-13 text-dark lh-base m-0 pt-1">ضمانت اصالت و سلامت فیزیکی کالا به همراه پشتیبانی ۲۴ ساعته.</span>
                                    </div>
                                </div>
                            </div>

                            <div className="col-12 col-lg-4">
                                <div className="alert border border-ui p-3 p-md-4 rounded-4 shadow-sm bg-white glass-panel sticky-sidebar">
                                    
                                    <div className="d-flex align-items-center justify-content-between pb-3 border-bottom border-light mb-4">
                                        <div className="d-flex align-items-center gap-2">
                                            <i className="bi bi-shop fs-4 text-primary"></i>
                                            <div>
                                                <strong className="d-block font-14 text-dark">فروشگاه رسمی آرک کالا</strong>
                                                <span className="font-12 text-success">تضمین کیفیت</span>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="d-flex bg-light border border-ui alert align-items-center justify-content-between rounded-4 mb-4">
                                        <div className="form-check m-0 d-flex align-items-center gap-2">
                                            <input className="form-check-input mt-0 shadow-none cursor-pointer" style={{width:'18px', height:'18px'}} type="checkbox" id="insuranceCheck" checked={hasInsurance} onChange={(e) => setHasInsurance(e.target.checked)} />
                                            <label className="form-check-label fw-bold font-13 text-dark cursor-pointer pt-1" htmlFor="insuranceCheck">بیمه تجهیزات فیزیکی کالا</label>
                                        </div>
                                    </div>

                                    {product.is_variable && Object.keys(availableAttributes).map((attrName, index) => {
                                        const isColor = attrName.includes('رنگ') || attrName.includes('Color');
                                        return (
                                            <div key={index} className="mb-4">
                                                <div className="font-14 fw-bold mb-3 d-block text-dark d-flex align-items-center gap-2"><i className="bi bi-sliders text-secondary"></i> انتخاب {attrName}</div>
                                                <div className="d-flex flex-wrap gap-2" role="radiogroup" aria-label={`انتخاب ${attrName}`}>
                                                    {Array.from(availableAttributes[attrName]).map(val => {
                                                        const isSelected = selectedOptions[attrName] === val;
                                                        return (
                                                            <React.Fragment key={val}>
                                                                <input type="radio" className="btn-check" id={`attr-${attrName}-${val}`} checked={isSelected} onChange={() => handleOptionChange(attrName, val)} aria-checked={isSelected} />
                                                                <label className={`btn font-12 px-3 py-2 border rounded-pill transition hover-lift ${isSelected ? 'border-danger text-danger bg-danger bg-opacity-10 fw-bold shadow-sm' : 'border-ui text-muted bg-white'}`} htmlFor={`attr-${attrName}-${val}`}>
                                                                    {isColor && <span className="d-inline-block rounded-circle me-2 border border-ui shadow-sm" style={{width:'12px', height:'12px', verticalAlign:'middle', backgroundColor: val === 'مشکی' ? '#212529' : val === 'سفید' ? '#f8f9fa' : val === 'قرمز' ? '#dc3545' : val === 'سبز' ? '#198754' : val === 'آبی' ? '#0d6efd' : '#ccc'}}></span>}
                                                                    {val}
                                                                </label>
                                                            </React.Fragment>
                                                        );
                                                    })}
                                                </div>
                                            </div>
                                        )
                                    })}

                                    <div className="text-start my-4 bg-light p-3 rounded-4 border border-light position-relative overflow-hidden">
                                        {product.is_special_offer && product.special_offer_end && (
                                            <div className="position-absolute top-0 start-0 w-100 bg-danger text-center p-1 d-flex justify-content-center">
                                                <CountdownTimer endTime={product.special_offer_end} />
                                            </div>
                                        )}

                                        <div className={`text-muted font-13 mb-2 d-flex align-items-center justify-content-between ${product.is_special_offer ? 'mt-4 pt-3' : ''}`}>
                                            <span>قیمت کالا:</span>
                                            {hasDiscount && <del className="text-danger">{Number(originalPrice).toLocaleString()}</del>}
                                        </div>
                                        <div className="fs-3 fw-900 text-dark d-flex align-items-center justify-content-between m-0">
                                            <span className="font-16">مبلغ نهایی</span>
                                            <span className="text-success d-flex align-items-center gap-2">
                                                {hasDiscount && <span className="badge bg-danger rounded-pill font-13 px-2 py-1 align-middle" aria-label={`تخفیف ${discountPercent} درصدی`}>{discountPercent}%</span>}
                                                {Number(currentPrice).toLocaleString()} <span className="text-muted font-13 fw-normal ms-1">تومان</span>
                                            </span>
                                        </div>
                                    </div>
                                    
                                    <form onSubmit={handleAddToCart} className="w-100 d-flex flex-column align-items-center gap-3">
                                        {product.is_wholesale && (
                                            <div className="font-12 text-dark text-center bg-warning bg-opacity-25 py-2 px-3 rounded-pill w-100 border border-warning border-opacity-50">
                                                <i className="bi bi-info-circle-fill text-warning me-2"></i>حداقل خرید عمده: <strong className="text-danger fw-bold">{product.wholesale_min_quantity} عدد</strong>
                                            </div>
                                        )}
                                        
                                        <div className="counter bg-white border border-ui rounded-pill p-2 d-flex align-items-center justify-content-between w-100 shadow-sm">
                                            <span className="font-13 fw-bold text-muted ms-3">تعداد کالا:</span>
                                            <div className="d-flex align-items-center bg-light rounded-pill border border-light p-1">
                                                <button type="button" className="btn btn-sm btn-white rounded-circle shadow-sm border-0 d-flex align-items-center justify-content-center" style={{width:'32px', height:'32px'}} onClick={() => setQuantity(prev => Math.max(1, prev - 1))} disabled={quantity <= 1 || currentInventory === 0} aria-label="کاهش تعداد"><i className="bi bi-dash text-danger fw-bold"></i></button>
                                                <label htmlFor="product-qty" className="visually-hidden">تعداد</label>
                                                <input id="product-qty" type="text" className="form-control border-0 text-center bg-transparent fw-900 font-16 p-0" value={quantity} readOnly style={{width:'35px'}} aria-live="polite"/>
                                                <button type="button" className="btn btn-sm btn-white rounded-circle shadow-sm border-0 d-flex align-items-center justify-content-center" style={{width:'32px', height:'32px'}} onClick={() => setQuantity(prev => Math.min(currentInventory, prev + 1))} disabled={quantity >= currentInventory || currentInventory === 0} aria-label="افزایش تعداد"><i className="bi bi-plus text-success fw-bold"></i></button>
                                            </div>
                                        </div>

                                        {currentInventory > 0 ? (
                                            <button type="submit" disabled={isAddingToCart} className="btn main-color-two-bg w-100 text-center text-white rounded-pill shadow hover-lift py-3 font-16 fw-bold d-flex align-items-center justify-content-center gap-2" aria-label="افزودن به سبد خرید">
                                                {isAddingToCart ? <div className="spinner-border spinner-border-sm text-white" role="status" aria-hidden="true"></div> : <i className="bi bi-bag-check-fill fs-4" aria-hidden="true"></i>}
                                                افزودن به سبد خرید
                                            </button>
                                        ) : (
                                            <button type="button" className="btn btn-secondary w-100 text-center text-white rounded-pill disabled py-3 fw-bold font-16" disabled aria-label="محصول ناموجود است">
                                                ناموجود
                                            </button>
                                        )}
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

<section className="product-desc mt-5 mb-5">
                <div className="container-fluid">
                    <div className="bg-white rounded-4 shadow-sm border border-ui p-2 mb-4 d-flex justify-content-center overflow-auto custom-scrollbar">
                        <ul className="nav nav-pills flex-nowrap m-0 p-0 gap-2" role="tablist">
                            <li className="nav-item flex-shrink-0" role="presentation">
                                <button className={`nav-link rounded-pill px-4 py-2 font-14 transition fw-bold d-flex align-items-center gap-2 ${activeTab === 'desc' ? 'active bg-danger text-white shadow-sm' : 'text-muted hover-bg-light border border-transparent'}`} onClick={() => setActiveTab('desc')} role="tab" aria-selected={activeTab === 'desc'}>
                                    <i className="bi bi-file-text"></i> معرفی محصول
                                </button>
                            </li>
                            <li className="nav-item flex-shrink-0" role="presentation">
                                <button className={`nav-link rounded-pill px-4 py-2 font-14 transition fw-bold d-flex align-items-center gap-2 ${activeTab === 'specs' ? 'active bg-danger text-white shadow-sm' : 'text-muted hover-bg-light border border-transparent'}`} onClick={() => setActiveTab('specs')} role="tab" aria-selected={activeTab === 'specs'}>
                                    <i className="bi bi-sliders2"></i> مشخصات فنی
                                </button>
                            </li>
                            <li className="nav-item flex-shrink-0" role="presentation">
                                <button className={`nav-link rounded-pill px-4 py-2 font-14 transition fw-bold d-flex align-items-center gap-2 ${activeTab === 'comments' ? 'active bg-danger text-white shadow-sm' : 'text-muted hover-bg-light border border-transparent'}`} onClick={() => setActiveTab('comments')} role="tab" aria-selected={activeTab === 'comments'}>
                                    <i className="bi bi-chat-dots"></i> نظرات
                                    <span className={`badge rounded-pill ms-1 ${activeTab === 'comments' ? 'bg-white text-danger' : 'bg-secondary bg-opacity-25 text-dark'}`}>{product.comments?.length || 0}</span>
                                </button>
                            </li>
                            <li className="nav-item flex-shrink-0" role="presentation">
                                <button className={`nav-link rounded-pill px-4 py-2 font-14 transition fw-bold d-flex align-items-center gap-2 ${activeTab === 'qa' ? 'active bg-danger text-white shadow-sm' : 'text-muted hover-bg-light border border-transparent'}`} onClick={() => setActiveTab('qa')} role="tab" aria-selected={activeTab === 'qa'}>
                                    <i className="bi bi-question-circle"></i> پرسش و پاسخ
                                    <span className={`badge rounded-pill ms-1 ${activeTab === 'qa' ? 'bg-white text-danger' : 'bg-secondary bg-opacity-25 text-dark'}`}>{product.questions?.length || 0}</span>
                                </button>
                            </li>
                        </ul>
                    </div>
                    
                    <div className="row mt-4 justify-content-center">
                        <div className="col-xl-10">
                            <div className="content-box rounded-4 p-4 p-md-5 border-ui shadow-sm bg-white min-vh-50">
                                
                                <div className="product-descs">
                                    {activeTab === 'desc' && (
                                        <div className="product-desc-content animate-fade-in" role="tabpanel">
                                            <div className="d-flex align-items-center gap-3 mb-4 pb-3 border-bottom border-light">
                                                <div className="bg-danger bg-opacity-10 text-danger rounded-4 d-flex align-items-center justify-content-center" style={{ width: '50px', height: '50px' }}>
                                                    <i className="bi bi-file-earmark-text fs-4"></i>
                                                </div>
                                                <h3 className="fw-900 text-dark m-0 fs-5">بررسی تخصصی و معرفی</h3>
                                            </div>
                                            
                                            <div className="font-14 font-md-15 text-dark lh-lg text-justify custom-html-content" dangerouslySetInnerHTML={{ __html: product.description.replace(/\n/g, '<br/>') }}></div>
                                            
                                            {product.citations && Array.isArray(product.citations) && product.citations.length > 0 && (
                                                <div className="mt-5 pt-4 bg-light rounded-4 p-4 border border-light">
                                                    <h4 className="fw-bold text-dark mb-4 font-15 d-flex align-items-center gap-2 border-end border-danger border-4 pe-2">
                                                        <i className="bi bi-link-45deg text-muted fs-4" aria-hidden="true"></i> منابع و کاتالوگ محصول
                                                    </h4>
                                                    <div className="d-flex flex-wrap gap-2" dir="ltr">
                                                        {product.citations.map((cite, idx) => (
                                                            <a key={idx} href={cite} target="_blank" rel="nofollow noreferrer" className="btn bg-white border border-ui rounded-pill font-12 text-muted hover-text-danger hover-border-danger transition shadow-sm d-inline-flex align-items-center gap-2">
                                                                <i className="bi bi-box-arrow-up-right"></i> منبع [{idx + 1}]
                                                            </a>
                                                        ))}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {activeTab === 'specs' && (
                                        <div className="animate-fade-in" role="tabpanel">
                                            <div className="d-flex align-items-center gap-3 mb-4 pb-3 border-bottom border-light">
                                                <div className="bg-danger bg-opacity-10 text-danger rounded-4 d-flex align-items-center justify-content-center" style={{ width: '50px', height: '50px' }}>
                                                    <i className="bi bi-sliders2-vertical fs-4"></i>
                                                </div>
                                                <h3 className="fw-900 text-dark m-0 fs-5">مشخصات فنی کالا</h3>
                                            </div>
                                            
                                            <div className="table-responsive mt-4">
                                                <table className="table table-striped table-hover border-ui rounded-4 overflow-hidden shadow-sm m-0">
                                                    <tbody>
                                                        <tr>
                                                            <td className="bg-light text-muted fw-bold font-13 align-middle py-3 px-4" style={{width: '30%'}}>برند سازنده</td>
                                                            <td className="text-dark font-14 fw-bold align-middle py-3 px-4">{product.brand ? product.brand.title : 'متفرقه'}</td>
                                                        </tr>
                                                        <tr>
                                                            <td className="bg-light text-muted fw-bold font-13 align-middle py-3 px-4">گروه کالایی</td>
                                                            <td className="text-dark font-14 fw-bold align-middle py-3 px-4">{product.category ? product.category.title : '-'}</td>
                                                        </tr>
                                                        <tr>
                                                            <td className="bg-light text-muted fw-bold font-13 align-middle py-3 px-4">وزن و ابعاد پایه</td>
                                                            <td className="text-dark font-14 fw-bold align-middle py-3 px-4">{product.weight} گرم</td>
                                                        </tr>
                                                        {product.is_variable && Object.keys(availableAttributes).map((attrName, idx) => (
                                                            <tr key={idx} className="transition">
                                                                <td className="bg-light text-muted fw-bold font-13 align-middle py-3 px-4">{attrName}</td>
                                                                <td className="text-dark font-14 fw-bold align-middle py-3 px-4">
                                                                    {selectedOptions[attrName] || 'لطفاً انتخاب کنید'}
                                                                </td>
                                                            </tr>
                                                        ))}
                                                    </tbody>
                                                </table>
                                            </div>
                                        </div>
                                    )}

                                    {activeTab === 'comments' && (
                                        <div className="product-comment-content animate-fade-in" role="tabpanel">
                                            <div className="comment-form mb-5 bg-light border border-ui rounded-4 p-4 p-md-5 shadow-sm">
                                                <div className="d-flex align-items-center gap-3 mb-4 pb-3 border-bottom border-light">
                                                    <div className="bg-danger bg-opacity-10 text-danger rounded-4 d-flex align-items-center justify-content-center flex-shrink-0" style={{ width: '50px', height: '50px' }}>
                                                        <i className="bi bi-chat-quote-fill fs-4"></i>
                                                    </div>
                                                    <div>
                                                        <h3 className="fw-900 text-dark m-0 fs-5 mb-1">دیدگاه خود را بنویسید</h3>
                                                        <p className="font-12 text-muted m-0">تجربیات شما به سایر کاربران در انتخاب بهتر کمک می‌کند.</p>
                                                    </div>
                                                </div>
                                                
                                                {user ? (
                                                    <form onSubmit={handleCommentSubmit}>
                                                        <div className="row gy-4">
                                                            <div className="col-12">
                                                                <div className="form-group d-flex align-items-center gap-3 bg-white p-3 rounded-pill border border-ui w-fit-content shadow-sm">
                                                                    <label className="fw-bold font-14 m-0 text-dark">امتیاز شما:</label>
                                                                    <div className="d-flex flex-row-reverse rating-stars fs-4" role="radiogroup" aria-label="امتیاز کالا از 1 تا 5">
                                                                        {[5, 4, 3, 2, 1].map(star => (
                                                                            <React.Fragment key={star}>
                                                                                <input type="radio" name="rating" id={`star${star}`} value={star} checked={rating === star} onChange={() => setRating(star)} aria-label={`${star} ستاره`} />
                                                                                <label htmlFor={`star${star}`} className={rating >= star ? 'text-warning drop-shadow' : 'text-muted opacity-25'}><i className="bi bi-star-fill" aria-hidden="true"></i></label>
                                                                            </React.Fragment>
                                                                        ))}
                                                                    </div>
                                                                </div>
                                                            </div>
                                                            <div className="col-md-6">
                                                                <label htmlFor="prosInput" className="text-success mb-2 fw-bold font-13"><i className="bi bi-plus-circle-fill me-1" aria-hidden="true"></i> نقاط قوت</label>
                                                                <input id="prosInput" type="text" className="form-control border-0 shadow-sm py-3 px-4 rounded-pill font-13" placeholder="مثال: کیفیت ساخت بالا" value={pros} onChange={(e) => setPros(e.target.value)} />
                                                            </div>
                                                            <div className="col-md-6">
                                                                <label htmlFor="consInput" className="text-danger mb-2 fw-bold font-13"><i className="bi bi-dash-circle-fill me-1" aria-hidden="true"></i> نقاط ضعف</label>
                                                                <input id="consInput" type="text" className="form-control border-0 shadow-sm py-3 px-4 rounded-pill font-13" placeholder="مثال: قیمت بالا" value={cons} onChange={(e) => setCons(e.target.value)} />
                                                            </div>
                                                            <div className="col-12">
                                                                <label htmlFor="commentBody" className="fw-bold font-13 mb-2 text-dark">متن نقد و بررسی <span className="text-danger">*</span></label>
                                                                <textarea id="commentBody" className="form-control border-0 shadow-sm py-3 px-4 rounded-4 font-13" rows="4" placeholder="کامل‌ترین تجربه خود را بنویسید..." value={commentBody} onChange={(e) => setCommentBody(e.target.value)} required></textarea>
                                                            </div>
                                                            <div className="col-12 text-end mt-4">
                                                                <button type="submit" className="btn btn-danger px-4 px-md-5 py-2 py-md-3 rounded-pill fw-bold font-14 shadow hover-lift w-100 w-md-auto" disabled={submittingComment}>
                                                                    {submittingComment ? <div className="spinner-border spinner-border-sm text-white" role="status" aria-hidden="true"></div> : <i className="bi bi-send-check-fill me-2" aria-hidden="true"></i>}
                                                                    ارسال دیدگاه
                                                                </button>
                                                            </div>
                                                        </div>
                                                    </form>
                                                ) : (
                                                    <div className="alert bg-white text-center rounded-4 p-4 p-md-5 shadow-sm border-0">
                                                        <i className="bi bi-lock-fill fs-1 text-danger d-block mb-3" aria-hidden="true"></i>
                                                        <p className="font-14 font-md-16 text-dark fw-bold mb-4">برای ثبت نظر نیازمند ورود به حساب کاربری هستید.</p>
                                                        <Link to="/login" className="btn btn-outline-danger rounded-pill px-4 px-md-5 py-2 fw-bold shadow-sm hover-lift">ورود / ثبت‌نام</Link>
                                                    </div>
                                                )}
                                            </div>

                                            <div className="d-flex align-items-center gap-3 mb-4 pb-3 border-bottom border-light mt-5">
                                                <div className="bg-light text-muted rounded-4 d-flex align-items-center justify-content-center flex-shrink-0" style={{ width: '40px', height: '40px' }}>
                                                    <i className="bi bi-people-fill fs-5"></i>
                                                </div>
                                                <h4 className="fw-900 text-dark m-0 fs-5">نظرات سایر خریداران</h4>
                                            </div>

                                            {product.comments && product.comments.length > 0 ? (
                                                <div className="d-flex flex-column gap-3 gap-md-4">
                                                    {product.comments.map(comment => {
                                                        let prosText = '';
                                                        let consText = '';
                                                        let bodyText = comment.body;
                                                        
                                                        if (comment.body.includes('نقاط قوت:')) {
                                                            const parts = comment.body.split('\n\nتوضیحات: ');
                                                            bodyText = parts[1] || comment.body;
                                                            const lines = parts[0]?.split('\n');
                                                            prosText = lines?.find(l => l.startsWith('نقاط قوت:'))?.replace('نقاط قوت: ', '') || '';
                                                            consText = lines?.find(l => l.startsWith('نقاط ضعف:'))?.replace('نقاط ضعف: ', '') || '';
                                                        }

                                                        return (
                                                            <div key={comment.uuid} className="box_users_comment border border-light rounded-4 p-3 p-md-4 shadow-sm bg-white hover-shadow transition">
                                                                <div className="row">
                                                                    <div className="col-12 col-lg-3 border-end-lg border-light mb-3 mb-lg-0 d-flex flex-row flex-lg-column align-items-center align-items-lg-start justify-content-between">
                                                                        <div className="d-flex align-items-center gap-3 mb-0 mb-lg-3">
                                                                            <div className="bg-light rounded-circle border border-ui d-flex align-items-center justify-content-center d-none d-md-flex" style={{width:'50px', height:'50px'}}><i className="bi bi-person text-secondary fs-3" aria-hidden="true"></i></div>
                                                                            <div>
                                                                                <span className="fw-bold font-14 text-dark d-block mb-1">{comment.user_name}</span>
                                                                                <span className="font-11 text-muted px-2 py-1 bg-light rounded-pill border"><time dateTime={comment.created_at}>{new Date(comment.created_at).toLocaleDateString('fa-IR')}</time></span>
                                                                            </div>
                                                                        </div>
                                                                        <div className="d-flex text-warning font-13 bg-warning bg-opacity-10 px-3 py-1 rounded-pill border border-warning border-opacity-25 mt-0 mt-lg-auto" aria-label={`امتیاز ${comment.rating} از 5`}>
                                                                            {Array.from({ length: 5 }).map((_, i) => (
                                                                                <i key={i} className={i < comment.rating ? "bi bi-star-fill" : "bi bi-star text-muted opacity-25"} aria-hidden="true"></i>
                                                                            ))}
                                                                        </div>
                                                                    </div>
                                                                    <div className="col-12 col-lg-9 ps-lg-4 mt-3 mt-lg-0 border-top border-light border-top-lg-0 pt-3 pt-lg-0">
                                                                        {((prosText && prosText !== 'ندارد') || (consText && consText !== 'ندارد')) && (
                                                                            <div className="row mb-3 bg-light p-2 p-md-3 rounded-4 border border-ui mx-0">
                                                                                {prosText && prosText !== 'ندارد' && (
                                                                                    <div className="col-md-6 mb-2 mb-md-0">
                                                                                        <span className="text-success font-12 fw-bold d-block mb-1">نقاط قوت</span>
                                                                                        <div className="font-13 text-dark"><i className="bi bi-plus-circle-fill text-success me-1 fs-6 align-middle" aria-hidden="true"></i>{prosText}</div>
                                                                                    </div>
                                                                                )}
                                                                                {consText && consText !== 'ندارد' && (
                                                                                    <div className="col-md-6">
                                                                                        <span className="text-danger font-12 fw-bold d-block mb-1">نقاط ضعف</span>
                                                                                        <div className="font-13 text-dark"><i className="bi bi-dash-circle-fill text-danger me-1 fs-6 align-middle" aria-hidden="true"></i>{consText}</div>
                                                                                    </div>
                                                                                )}
                                                                            </div>
                                                                        )}
                                                                        <p className="font-14 text-muted lh-lg text-justify m-0">{bodyText}</p>
                                                                    </div>
                                                                </div>
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            ) : (
                                                <div className="text-center py-5 bg-light border border-light rounded-4">
                                                    <img src="/assets/image/cart/empty-cart.svg" alt="هیچ نظری ثبت نشده" style={{width:'80px', opacity:'0.5'}} className="mb-3"/>
                                                    <h6 className="font-15 fw-bold text-dark mb-2">نظری برای نمایش وجود ندارد</h6>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                    {activeTab === 'qa' && (
                                        <div className="animate-fade-in" role="tabpanel">
                                            <div className="d-flex align-items-center gap-3 mb-4 pb-3 border-bottom border-light">
                                                <div className="bg-danger bg-opacity-10 text-danger rounded-4 d-flex align-items-center justify-content-center flex-shrink-0" style={{ width: '50px', height: '50px' }}>
                                                    <i className="bi bi-question-diamond-fill fs-4"></i>
                                                </div>
                                                <div>
                                                    <h3 className="fw-900 text-dark m-0 fs-5 mb-1">پرسش و پاسخ کاربران</h3>
                                                    <p className="font-12 text-muted m-0">سوالات خود را درباره این محصول بپرسید</p>
                                                </div>
                                            </div>
                                            
                                            <div className="box_questions bg-light border border-light rounded-4 p-4 p-md-5 mb-5 shadow-sm">
                                                <form onSubmit={handleQuestionSubmit}>
                                                    <div className="row gy-3">
                                                        <div className="col-12">
                                                            <div className="alert bg-info bg-opacity-10 border border-info border-opacity-25 rounded-3 d-flex align-items-start gap-2 m-0 font-13 text-dark">
                                                                <i className="bi bi-info-circle-fill text-info fs-5" aria-hidden="true"></i> <span className="pt-1">ثبت پرسش برای تمامی افراد آزاد است.</span>
                                                            </div>
                                                        </div>
                                                        {!user && (
                                                            <div className="col-md-6">
                                                                <label htmlFor="guestName" className="font-13 fw-bold text-dark mb-2"><i className="bi bi-person me-1 text-muted" aria-hidden="true"></i> نام شما (اختیاری):</label>
                                                                <input id="guestName" type="text" className="form-control border-0 py-3 px-4 rounded-pill shadow-sm font-13" placeholder="مثال: رضا جعفری" value={guestName} onChange={(e) => setGuestName(e.target.value)} />
                                                            </div>
                                                        )}
                                                        <div className="col-12">
                                                            <label htmlFor="questionText" className="font-13 fw-bold text-dark mb-2"><i className="bi bi-pencil me-1 text-muted" aria-hidden="true"></i> پرسش خود را بنویسید <span className="text-danger">*</span></label>
                                                            <textarea id="questionText" className="form-control border-0 py-3 px-4 rounded-4 shadow-sm font-13" placeholder="سوال خود را درباره ویژگی‌ها یا کارایی این کالا بنویسید..." rows="3" value={questionText} onChange={(e) => setQuestionText(e.target.value)} required></textarea>
                                                        </div>
                                                        <div className="col-12 text-end mt-4">
                                                            <button className="btn btn-dark text-white px-4 py-2 py-md-3 px-md-5 rounded-pill fw-bold font-13 shadow-sm hover-lift w-100 w-md-auto" type="submit" disabled={submittingQuestion}>
                                                                {submittingQuestion ? <div className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></div> : <i className="bi bi-send-fill me-2" aria-hidden="true"></i>}
                                                                ارسال پرسش
                                                            </button>
                                                        </div>
                                                    </div>
                                                </form>
                                            </div>

                                            <div className="d-flex align-items-center gap-3 mb-4 pb-3 border-bottom border-light mt-5">
                                                <div className="bg-light text-muted rounded-4 d-flex align-items-center justify-content-center flex-shrink-0" style={{ width: '40px', height: '40px' }}>
                                                    <i className="bi bi-ui-checks fs-5"></i>
                                                </div>
                                                <h4 className="fw-900 text-dark m-0 fs-5">پاسخ‌های تایید شده</h4>
                                            </div>

                                            {product.questions && product.questions.length > 0 ? (
                                                <div className="d-flex flex-column gap-4">
                                                    {product.questions.map((q) => (
                                                        <div key={q.uuid} className="box_questions border border-ui rounded-4 p-3 p-md-4 bg-white shadow-sm hover-shadow transition">
                                                            <div className="row bs-qu align-items-start mb-3">
                                                                <div className="col-2 col-lg-2 bq1 text-center border-end border-light pe-2 pe-md-3">
                                                                    <i className="bi bi-person-circle text-muted fs-1 d-none d-md-block" aria-hidden="true"></i>
                                                                    <i className="bi bi-person-circle text-muted fs-3 d-block d-md-none" aria-hidden="true"></i>
                                                                </div>
                                                                <div className="col-10 col-lg-10 bq2 ps-2 ps-md-4 d-flex flex-column justify-content-center">
                                                                    <div className="d-flex align-items-center justify-content-between mb-2">
                                                                        <span className="span2 font-13 fw-bold text-dark">{q.user_name}</span>
                                                                        <span className="font-11 text-muted"><time dateTime={q.created_at}>{new Date(q.created_at).toLocaleDateString('fa-IR')}</time></span>
                                                                    </div>
                                                                    <div className="fw-bold text-danger mb-2 font-13"><i className="bi bi-question-circle-fill me-1" aria-hidden="true"></i> پرسش:</div>
                                                                    <p className="font-14 text-dark lh-lg text-justify m-0 bg-light p-2 p-md-3 rounded-3">{q.text}</p>
                                                                </div>
                                                            </div>
                                                            {q.answer_text && (
                                                                <div className="row bs-qu align-items-start pt-3 border-top border-light">
                                                                    <div className="col-2 col-lg-2 bq1 text-center border-end border-light pe-2 pe-md-3">
                                                                        <div className="bg-success rounded-circle d-flex align-items-center justify-content-center mx-auto shadow-sm" style={{width:'35px', height:'35px'}}><i className="bi bi-headset text-white font-16" aria-hidden="true"></i></div>
                                                                    </div>
                                                                    <div className="col-10 col-lg-10 bq2 ps-2 ps-md-4 d-flex flex-column justify-content-center">
                                                                        <span className="span1 font-12 fw-bold text-success d-block mb-2">پشتیبانی آرک کالا</span>
                                                                        <p className="font-14 text-dark lh-lg text-justify m-0 bg-success bg-opacity-10 border border-success border-opacity-25 p-2 p-md-3 rounded-3">{q.answer_text}</p>
                                                                    </div>
                                                                </div>
                                                            )}
                                                        </div>
                                                    ))}
                                                </div>
                                            ) : (
                                                <div className="text-center py-5 bg-light border border-light rounded-4">
                                                    <i className="bi bi-chat-left-dots fs-1 text-muted opacity-50 d-block mb-3" aria-hidden="true"></i>
                                                    <h5 className="font-15 fw-bold text-dark mb-2">سوالی ثبت نشده است</h5>
                                                </div>
                                            )}
                                        </div>
                                    )}

                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {suggestedProducts && suggestedProducts.length > 0 && (
                <section className="product-slider mt-5 mb-5 pb-5">
                    <div className="container-fluid">
                        <div className="section-title mb-4 border-bottom border-2 border-ui pb-3 d-flex align-items-center justify-content-between">
                            <h2 className="fw-900 h5 text-dark m-0 d-flex align-items-center gap-2"><i className="bi bi-bag-heart text-danger" aria-hidden="true"></i> محصولات <span className="text-danger">مرتبط</span></h2>
                            {product.category && <Link to={`/shop?category__slug=${product.category.slug}`} className="btn btn-outline-danger rounded-pill px-3 py-1 font-12 fw-bold shadow-sm hover-lift" aria-label={`مشاهده همه محصولات ${product.category.title}`}>مشاهده همه <i className="bi bi-chevron-left" aria-hidden="true"></i></Link>}
                        </div>
                        
                        <Swiper
                            dir="rtl"
                            spaceBetween={15}
                            slidesPerView={1.2}
                            breakpoints={{
                                576: { slidesPerView: 2.2 },
                                768: { slidesPerView: 3.2 },
                                992: { slidesPerView: 4 },
                                1200: { slidesPerView: 5 },
                            }}
                            navigation={true}
                            autoplay={{ delay: 4000, disableOnInteraction: false }}
                            modules={[Navigation, Autoplay]}
                            className="py-4 px-2"
                            aria-label="لیست محصولات مرتبط"
                        >
                            {suggestedProducts.map(prod => (
                                <SwiperSlide key={prod.uuid}>
                                    <Link to={`/product/${prod.slug}`} className="text-decoration-none">
                                        <div className="product-box border border-ui shadow-sm rounded-4 p-3 p-md-4 bg-white hover-shadow transition h-100 d-flex flex-column position-relative">
                                            {prod.is_wholesale && <span className="position-absolute top-0 start-0 badge bg-danger text-white rounded-end-pill py-1 px-2 mt-3 shadow-sm font-11 z-1">فروش عمده</span>}
                                            <div className="text-center mb-3 pt-2">
                                                <img 
                                                    src={resolveImageUrl(prod.image_url || prod.image || (prod.gallery && prod.gallery.length > 0 ? prod.gallery[0].url : ''))} 
                                                    alt={prod.gallery?.[0]?.image_alt || prod.title}
                                                    title={prod.gallery?.[0]?.image_alt || prod.title}
                                                    className="img-fluid object-fit-contain transition hover-lift" 
                                                    style={{height: '140px'}} 
                                                    loading="lazy"
                                                    decoding="async"
                                                    onError={(e)=>{e.target.src='/assets/image/product/product-no-bg.png';}} 
                                                />
                                            </div>
                                            <h3 className="font-13 text-dark lh-lg text-overflow-2 fw-bold mb-3">{prod.title}</h3>
                                            <div className="mt-auto d-flex justify-content-between align-items-center">
                                                <div className="d-flex align-items-center text-warning font-12 bg-warning bg-opacity-10 px-2 py-1 rounded-pill" aria-label={`امتیاز ${prod.average_rating ? prod.average_rating.toFixed(1) : '5.0'} از 5`}>
                                                    <i className="bi bi-star-fill me-1" aria-hidden="true"></i> {prod.average_rating ? prod.average_rating.toFixed(1) : '5.0'}
                                                </div>
                                                <div className="text-end">
                                                    <strong className="text-dark font-16 fw-900">{Number(prod.base_price).toLocaleString()} <span className="font-11 text-muted fw-normal">تومان</span></strong>
                                                </div>
                                            </div>
                                        </div>
                                    </Link>
                                </SwiperSlide>
                            ))}
                        </Swiper>
                    </div>
                </section>
            )}

            <div className="modal fade" id="videoModal" tabIndex="-1" aria-labelledby="videoModalLabel" aria-hidden="true">
                <div className="modal-dialog modal-lg modal-dialog-centered">
                    <div className="modal-content bg-dark border-0 overflow-hidden rounded-4 shadow-lg">
                        <div className="modal-header border-0 position-absolute top-0 end-0 z-3 w-100 p-3 d-flex justify-content-end bg-gradient-dark">
                            <button type="button" className="btn-close btn-close-white shadow-none" data-bs-dismiss="modal" aria-label="بستن"></button>
                        </div>
                        <div className="modal-body p-0 d-flex align-items-center justify-content-center bg-black" style={{minHeight:'400px'}}>
                            {mainVideo ? (
                                <video src={mainVideo.url} controls className="w-100 h-100" style={{maxHeight:'85vh'}} title="ویدیو معرفی محصول"></video>
                            ) : (
                                <div className="p-5 text-center text-white font-15 d-flex flex-column align-items-center"><i className="bi bi-camera-video-off fs-1 mb-3 text-muted" aria-hidden="true"></i> ویدیویی آپلود نشده است.</div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            <div className="share-modal py-0">
                <div className="modal fade" id="shareModal" tabIndex="-1" aria-labelledby="shareModalLabel" aria-hidden="true">
                    <div className="modal-dialog modal-sm modal-dialog-centered">
                        <div className="modal-content border-0 rounded-4 shadow-lg overflow-hidden glass-panel">
                            <div className="modal-header bg-light border-0 px-4 py-3">
                                <h5 className="modal-title font-15 fw-900 text-dark m-0 d-flex align-items-center gap-2" id="shareModalLabel"><i className="bi bi-share-fill text-danger fs-5" aria-hidden="true"></i> اشتراک گذاری</h5>
                                <button type="button" className="btn-close shadow-none" data-bs-dismiss="modal" aria-label="بستن"></button>
                            </div>
                            <div className="modal-body text-center p-4">
                                <p className="font-13 text-muted mb-4 lh-base">ارسال این محصول شگفت‌انگیز به دوستان!</p>
                                <button type="button" onClick={copyToClipboard} className="btn my-3 d-block text-center btn-dark w-100 rounded-pill py-2 font-14 fw-bold transition shadow-sm hover-lift">
                                    <i className="bi bi-files me-2 fs-5 align-middle" aria-hidden="true"></i> کپی لینک محصول
                                </button>
                                <div className="d-flex justify-content-center gap-4 social-link fs-3 mt-4">
                                    <a href={`https://t.me/share/url?url=${window.location.href}`} target="_blank" rel="noreferrer" className="text-primary transition hover-lift" aria-label="اشتراک‌گذاری در تلگرام"><i className="bi bi-telegram" aria-hidden="true"></i></a>
                                    <a href={`https://wa.me/?text=${window.location.href}`} target="_blank" rel="noreferrer" className="text-success transition hover-lift" aria-label="اشتراک‌گذاری در واتساپ"><i className="bi bi-whatsapp" aria-hidden="true"></i></a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="modal fade" id="chartModal" tabIndex="-1" aria-labelledby="chartModalLabel" aria-hidden="true">
                <div className="modal-dialog modal-dialog-centered modal-lg">
                    <div className="modal-content border-0 rounded-4 shadow-lg overflow-hidden">
                        <div className="modal-header bg-light border-0 px-4 py-3 d-flex align-items-start">
                            <div>
                                <h5 className="modal-title fw-900 text-dark font-16 d-flex align-items-center gap-2" id="chartModalLabel"><i className="bi bi-graph-up-arrow text-danger fs-4" aria-hidden="true"></i> نمودار تغییرات قیمت فروش</h5>
                                <p className="text-muted mt-2 font-12 m-0 text-overflow-1">{product.title}</p>
                            </div>
                            <button type="button" className="btn-close shadow-none mt-1" data-bs-dismiss="modal" aria-label="بستن"></button>
                        </div>
                        <div className="modal-body p-3 p-md-4 bg-white">
                            <div className="w-100 d-flex justify-content-center chart-container">
                                <canvas id="myChart" ref={chartRef} aria-label="نمودار قیمت محصول"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <style jsx="true">{`
                .cursor-pointer { cursor: pointer; }
                .hover-shadow:hover { box-shadow: 0 1rem 2rem rgba(0,0,0,.08)!important; transform: translateY(-3px); }
                .hover-lift { transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1), box-shadow 0.2s; }
                .hover-lift:hover { transform: translateY(-2px); box-shadow: 0 .5rem 1rem rgba(0,0,0,.15)!important; }
                .hover-bg-light:hover { background-color: #f8f9fa!important; }
                .hover-text-dark:hover { color: #212529!important; }
                .hover-text-danger:hover { color: #dc3545!important; }
                .transition { transition: all 0.3s ease; }
                .w-fit-content { width: fit-content; }
                
                .visually-hidden { position: absolute !important; width: 1px !important; height: 1px !important; padding: 0 !important; margin: -1px !important; overflow: hidden !important; clip: rect(0, 0, 0, 0) !important; white-space: nowrap !important; border: 0 !important; }
                
                .text-overflow-1 { overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; }
                .text-overflow-2 { overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
                .font-en { font-family: Arial, sans-serif; letter-spacing: 0.5px; }
                .border-dashed { border-style: dashed !important; border-color: #dee2e6 !important;}
                
                .bg-gradient-dark { background: linear-gradient(180deg, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0) 100%); }
                .glass-panel { background: rgba(255, 255, 255, 0.95) !important; backdrop-filter: blur(10px); }
                .pointer-events-none { pointer-events: none; }
                
                .sticky-sidebar { position: sticky; top: 100px; z-index: 10; }
                .main-gallery-img { height: 400px; }
                .chart-container { height: 350px; }

                @media (max-width: 991px) {
                    .h-lg-100 { height: auto !important; }
                    .sticky-sidebar { position: relative; top: 0; margin-top: 1rem; }
                    .main-gallery-img { height: 250px !important; }
                    .chart-container { height: 250px !important; }
                }
                
                .custom-toast { position: fixed; bottom: 30px; left: -400px; min-width: 300px; padding: 16px 24px; border-radius: 16px; z-index: 999999; transition: left 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
                .custom-toast.show { left: 30px; }
                
                @media (max-width: 768px) {
                    .custom-toast { left: 50% !important; transform: translateX(-50%); bottom: -100px; width: 90%; min-width: unset; transition: bottom 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
                    .custom-toast.show { bottom: 20px !important; left: 50% !important; }
                }
                
                .product-gallery { --swiper-theme-color: #ef4056; }
                .product-gallery-thumb .swiper-slide { opacity: 0.4; transition: opacity 0.3s; border: 2px solid transparent; border-radius: 0.5rem; overflow:hidden;}
                .product-gallery-thumb .swiper-slide-thumb-active { opacity: 1; border-color: #ef4056 !important; }

                .animate-fade-in { animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
                
                .animate-pulse { animation: pulse 2s infinite; }
                @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(220,53,69, 0.4); } 70% { box-shadow: 0 0 0 10px rgba(220,53,69, 0); } 100% { box-shadow: 0 0 0 0 rgba(220,53,69, 0); } }
                
                .active-favorite i { animation: pop 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards; }
                @keyframes pop { 0% { transform: scale(1); } 50% { transform: scale(1.3); } 100% { transform: scale(1); } }

                .rating-stars input[type="radio"] { display: none; }
                .rating-stars label { cursor: pointer; padding: 0 4px; transition: color 0.2s, transform 0.2s;}
                .rating-stars label:hover, .rating-stars label:hover ~ label { color: #ffc107 !important; opacity: 1 !important; transform: scale(1.2); }
                .drop-shadow { filter: drop-shadow(0px 2px 4px rgba(255,193,7,0.4)); }

                .custom-scrollbar::-webkit-scrollbar { height: 4px; width: 4px;}
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #e0e0e0; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #bdbdbd; }

                .hide-panel { max-height: 0; opacity: 0; transition: all 0.3s ease; }
                .show-panel { max-height: 1000px; opacity: 1; transition: all 0.4s ease; }
                .rotate-180 { transform: rotate(180deg); }
            `}</style>
        </React.Fragment>
    );
};

export default ProductDetailPage;