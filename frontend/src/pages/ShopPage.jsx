import React, { useState, useEffect, useRef, useContext } from 'react';
import { useSearchParams, useParams, Link, useLocation } from 'react-router-dom';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import { Swiper, SwiperSlide } from 'swiper/react';
import { FreeMode, Navigation } from 'swiper/modules';

import { getProductsList, getMaxPrice } from '../api/shopApi';
import { getCategoryTree, getBrandsList } from '../api/searchApi';
import ProductCard from '../components/ProductCard';
import { SiteContext } from '../context/SiteContext';

const MAX_PRICE_LIMIT = 50000000; 

const resolveImageUrl = (url) => {
    if (!url) return null;
    if (url.startsWith('http') || url.startsWith('data:')) return url;
    
    let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    baseUrl = baseUrl.replace(/\/api\/?$/, '');
    if (baseUrl.endsWith('/')) {
        baseUrl = baseUrl.slice(0, -1);
    }
    
    let path = url;
    if (!path.startsWith('/')) {
        path = '/media/' + path;
    } else if (!path.startsWith('/media/')) {
        path = '/media' + path;
    }
    
    return `${baseUrl}${path}`;
};

const ShopPage = () => {
    const location = useLocation();
    const [searchParams, setSearchParams] = useSearchParams();
    const { slug: categorySlug } = useParams();
    const { settings } = useContext(SiteContext); 
    
    const isSpecialOffers = location.pathname.includes('special-offers');
    const isBestSellers = location.pathname.includes('best-sellers');

    const [products, setProducts] = useState([]);
    const [pagination, setPagination] = useState({ count: 0, next: null, previous: null });
    const [categories, setCategories] = useState([]);
    const [brands, setBrands] = useState([]);
    const [loading, setLoading] = useState(true);
    
    const [maxPriceLimit, setMaxPriceLimit] = useState(0);
    const [isMaxPriceLoaded, setIsMaxPriceLoaded] = useState(false);

    const urlMin = parseInt(searchParams.get('min_price'), 10) || 0;
    const urlMax = parseInt(searchParams.get('max_price'), 10) || null;
    
    const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '');
    
    const [ordering, setOrdering] = useState(
        isBestSellers ? '-sold_count' : (searchParams.get('ordering') || '-created_at')
    );
    
    const [priceRange, setPriceRange] = useState([urlMin, 0]);
    const [displayPrice, setDisplayPrice] = useState([urlMin, 0]);
    const [sliderStart] = useState([urlMin, urlMax || MAX_PRICE_LIMIT]);

    const [stockStatus, setStockStatus] = useState(searchParams.get('has_stock') || 'all'); 
    const [hasDiscount, setHasDiscount] = useState(searchParams.get('has_discount') === 'true');
    const [selectedBrands, setSelectedBrands] = useState(searchParams.get('brands') ? searchParams.get('brands').split(',') : []);
    const [page, setPage] = useState(Number(searchParams.get('page')) || 1);
    
    const [isReadMoreOpen, setIsReadMoreOpen] = useState(false);
    const filterTimeoutRef = useRef(null);

    useEffect(() => {
        if (isSpecialOffers) {
            setOrdering('-created_at'); 
            setHasDiscount(false);
        } else if (isBestSellers) {
            setOrdering('-sold_count');
            setHasDiscount(false); 
        }
    }, [location.pathname]);

    useEffect(() => {
        getCategoryTree().then(setCategories).catch(console.error);
        getBrandsList().then(data => setBrands(data.results || data)).catch(console.error);
        
        getMaxPrice().then(fetchedMaxPrice => {
            const finalMaxPrice = fetchedMaxPrice > 0 ? fetchedMaxPrice : MAX_PRICE_LIMIT;
            setMaxPriceLimit(finalMaxPrice);
            
            const currentMax = urlMax !== null ? urlMax : finalMaxPrice;
            setPriceRange([urlMin, currentMax]);
            setDisplayPrice([urlMin, currentMax]);
            
            setIsMaxPriceLoaded(true);
        });
    }, []);

    const fetchProducts = async (queryString) => {
        setLoading(true);
        try {
            const data = await getProductsList(queryString);
            setProducts(data.results || data);
            
            if (data && data.count !== undefined) {
                setPagination({ count: data.count, next: data.next, previous: data.previous });
            } else if (Array.isArray(data)) {
                setPagination({ count: data.length, next: null, previous: null });
            }
        } catch (error) {
            console.error("Error fetching products:", error);
        } finally {
            setLoading(false);
        }
    };

    const applyFilters = () => {
        if (!isMaxPriceLoaded) return; 

        const params = new URLSearchParams();
        if (searchQuery) params.set('search', searchQuery);
        if (ordering) params.set('ordering', ordering);
        
        if (stockStatus === 'available') params.set('has_stock', 'true');
        if (stockStatus === 'unavailable') params.set('has_stock', 'false');
        
        if (isSpecialOffers) {
            params.set('is_special_offer', 'true');
        } else if (hasDiscount) {
            params.set('has_discount', 'true');
        }
        
        if (priceRange[0] > 0) params.set('min_price', priceRange[0]);
        if (priceRange[1] < maxPriceLimit) params.set('max_price', priceRange[1]);
        
        if (selectedBrands.length > 0) params.set('brands', selectedBrands.join(','));
        if (page > 1) params.set('page', page);
        if (categorySlug) params.set('category__slug', categorySlug);

        setSearchParams(params);
        fetchProducts(params.toString());
    };

    useEffect(() => {
        if (filterTimeoutRef.current) clearTimeout(filterTimeoutRef.current);
        filterTimeoutRef.current = setTimeout(() => {
            applyFilters();
        }, 600);
    }, [searchQuery, ordering, stockStatus, hasDiscount, priceRange[0], priceRange[1], selectedBrands.join(','), page, categorySlug, isMaxPriceLoaded, location.pathname]);

    const handleSliderUpdate = (value) => {
        setDisplayPrice(value);
    };

    const handleSliderChange = (value) => {
        setPriceRange(value);
        setPage(1);
    };

    const toggleBrand = (slug) => {
        setSelectedBrands(prev => prev.includes(slug) ? prev.filter(b => b !== slug) : [...prev, slug]);
        setPage(1);
    };

    const clearAllFilters = () => {
        setSearchQuery('');
        setPriceRange([0, maxPriceLimit]);
        setDisplayPrice([0, maxPriceLimit]);
        setHasDiscount(false);
        setStockStatus('all');
        setSelectedBrands([]);
        setOrdering(isBestSellers ? '-sold_count' : '-created_at');
        setPage(1);
    };

    const handlePageChange = (newPage) => {
        setPage(newPage);
        window.scrollTo({ top: 100, behavior: 'smooth' });
    };

    const totalPages = Math.ceil(pagination.count / 9);

    let pageTitleText = 'دسته‌بندی محصولات';
    let pageTitleHighlight = '';
    let pageIcon = '';

    if (isSpecialOffers) {
        pageTitleText = 'پیشنهادهای';
        pageTitleHighlight = 'شگفت‌انگیز';
        pageIcon = 'bi-lightning-charge-fill text-danger';
    } else if (isBestSellers) {
        pageTitleText = 'پرفروش‌ترین';
        pageTitleHighlight = 'محصولات';
        pageIcon = 'bi-fire text-warning';
    } else if (categorySlug) {
        const foundCat = categories.find(c => c.slug === categorySlug);
        pageTitleText = 'محصولات';
        pageTitleHighlight = foundCat ? foundCat.title : 'دسته‌بندی';
        pageIcon = 'bi-box-seam text-primary';
    } else {
        pageTitleText = 'فروشگاه';
        pageTitleHighlight = settings?.site_name || '...';
        pageIcon = 'bi-shop text-success';
    }

    const renderSidebarFilters = (isMobile) => {
        const prefixId = isMobile ? 'mob-' : 'desk-'; 
        
        return (
            <aside>
                <section className="mb-4 border-ui shadow-sm filter-container bg-white p-4 rounded-4">
                    <h4 className="section-title visually-hidden">جستجوی محصولات</h4>
                    <label htmlFor={`${prefixId}search-products`} className="filter-title fw-bold mb-3 d-block font-16">جستجو محصولات</label>
                    <div className="position-relative">
                        <input 
                            id={`${prefixId}search-products`}
                            type="text" 
                            className="form-control py-3 rounded-3 w-100 bg-light border-0 shadow-none font-14 pe-5" 
                            placeholder="نام محصول، برند و..."
                            value={searchQuery}
                            onChange={(e) => { setSearchQuery(e.target.value); setPage(1); }}
                        />
                        <span className="position-absolute me-3 end-0 top-50 translate-middle-y text-muted"><i className="bi bi-search fs-5"></i></span>
                    </div>
                </section>

                <section className="mb-4 border-ui shadow-sm filter-container bg-white p-4 rounded-4">
                    <h2 className="filter-title fw-bold mb-4 font-16">فیلتر قیمت</h2>
                    <div className="filter-price mt-4">
                        <div className="px-3 mb-5 mt-4" dir="rtl">
                            {isMaxPriceLoaded ? (
                                <Slider
                                    range
                                    reverse={true}
                                    min={0}
                                    max={maxPriceLimit}
                                    step={50000}
                                    value={displayPrice}
                                    start={sliderStart}
                                    onChange={handleSliderUpdate}
                                    onChangeComplete={handleSliderChange}
                                    className="custom-rc-slider"
                                />
                            ) : (
                                <div className="text-center text-muted font-12"><div className="spinner-grow spinner-grow-sm text-danger me-2"></div>در حال بارگذاری بازه قیمت...</div>
                            )}
                        </div>
                        
                        <div className="d-flex align-items-center justify-content-between mt-4 bg-light rounded-3 p-3 border border-ui">
                            <div className="d-flex flex-column align-items-start">
                                <span className="font-12 text-muted mb-1">از قیمت</span>
                                <span className="font-15 fw-bold text-dark">
                                    {new Intl.NumberFormat('fa-IR').format(displayPrice[0])} <span className="font-11 fw-normal text-muted">تومان</span>
                                </span>
                            </div>
                            <div className="text-muted"><i className="bi bi-arrow-left"></i></div>
                            <div className="d-flex flex-column align-items-end">
                                <span className="font-12 text-muted mb-1">تا قیمت</span>
                                <span className="font-15 fw-bold text-dark">
                                    {new Intl.NumberFormat('fa-IR').format(displayPrice[1])} <span className="font-11 fw-normal text-muted">تومان</span>
                                </span>
                            </div>
                        </div>
                    </div>

                    <hr className="my-4 border-light" />

                    <div className="form-check mt-3 d-flex align-items-center p-0">
                        <input 
                            className="form-check-input m-0 cursor-pointer shadow-none custom-checkbox border-secondary" 
                            type="checkbox" 
                            id={`${prefixId}stock-available`}
                            checked={stockStatus === 'available'} 
                            onChange={(e) => { setStockStatus(e.target.checked ? 'available' : 'all'); setPage(1); }}
                        />
                        <label className="form-check-label ms-3 font-14 cursor-pointer text-dark pt-1" htmlFor={`${prefixId}stock-available`}>فقط کالاهای موجود</label>
                    </div>
                    
                    {!isSpecialOffers && (
                        <div className="form-check mt-3 d-flex align-items-center p-0">
                            <input 
                                className="form-check-input m-0 cursor-pointer shadow-none custom-checkbox border-secondary" 
                                type="checkbox" 
                                id={`${prefixId}has-discount`}
                                checked={hasDiscount}
                                onChange={(e) => { setHasDiscount(e.target.checked); setPage(1); }}
                            />
                            <label className="form-check-label ms-3 font-14 cursor-pointer text-dark pt-1" htmlFor={`${prefixId}has-discount`}>فقط محصولات تخفیف‌دار</label>
                        </div>
                    )}
                </section>

                {brands.length > 0 && (
                    <section className="mb-4 border-ui shadow-sm filter-container bg-white p-4 rounded-4">
                        <h2 className="filter-title fw-bold mb-4 font-16">برند</h2>
                        <div className="custom-scrollbar pe-2" style={{maxHeight: '220px', overflowY: 'auto'}}>
                            {brands.map(brand => (
                                <div className="d-flex align-items-center justify-content-between mb-3" key={brand.uuid}>
                                    <div className="form-check m-0 p-0 d-flex align-items-center flex-grow-1">
                                        <input 
                                            className="form-check-input m-0 cursor-pointer shadow-none custom-checkbox border-secondary flex-shrink-0" 
                                            type="checkbox" 
                                            id={`${prefixId}brand-${brand.slug}`}
                                            checked={selectedBrands.includes(brand.slug)}
                                            onChange={() => toggleBrand(brand.slug)}
                                        />
                                        <label className="form-check-label font-14 cursor-pointer text-dark ms-3 pt-1 text-truncate" style={{maxWidth: '130px'}} htmlFor={`${prefixId}brand-${brand.slug}`}>
                                            {brand.title}
                                        </label>
                                    </div>
                                    <span className="badge bg-light text-muted border font-12 fw-normal px-2 py-1 ms-2">{brand.product_count || 0}</span>
                                </div>
                            ))}
                        </div>
                    </section>
                )}
                
                <button className="btn btn-outline-danger rounded-3 w-100 fw-bold py-2 mb-4 d-flex align-items-center justify-content-center gap-2 shadow-sm" onClick={clearAllFilters}>
                    <i className="bi bi-trash3"></i> حذف همه فیلترها
                </button>
            </aside>
        );
    };

    return (
        <main className="shop-page-wrapper py-4 bg-light">
            
            <section className="card-categories site-slider bg-white pt-4 pb-2 border-bottom mb-4 shadow-sm">
                <div className="container-fluid">
                    <div className="section-title mb-4">
                        <div className="d-flex flex-wrap align-items-center justify-content-between border-bottom border-light pb-3">
                            <div className="d-flex align-items-center gap-2">
                                <i className={`bi ${pageIcon} fs-3`}></i>
                                <h1 className="fw-900 h4 m-0 text-dark d-flex align-items-center gap-2">
                                    <span>{pageTitleText}</span> <span className="text-danger">{pageTitleHighlight}</span>
                                </h1>
                            </div>
                        </div>
                    </div>

                    {!categorySlug && !isSpecialOffers && !isBestSellers && categories.length > 0 && (
                        <Swiper modules={[FreeMode]} freeMode={true} slidesPerView="auto" className="pro-slider py-3 px-2">
                            {categories.map(cat => {
                                const imgUrl = cat.image || cat.image_url || cat.icon || cat.logo;
                                return (
                                <SwiperSlide key={cat.uuid} style={{ width: 'auto' }}>
                                    <Link to={`/category/${cat.slug}`} className="text-decoration-none">
                                        <div className="cat-item d-flex flex-column align-items-center mx-2 mx-md-3 group-cat-item">
                                            <div className="cat-item-image bg-light rounded-4 d-flex align-items-center justify-content-center mb-3 position-relative z-1 shadow-sm border border-ui" style={{ width: '110px', height: '110px', padding: '10px' }}>
                                                <div className="bg-white rounded-circle w-100 h-100 d-flex align-items-center justify-content-center overflow-hidden inner-cat-circle" style={{ transition: 'all 0.3s ease' }}>
                                                    <img 
                                                        src={imgUrl ? resolveImageUrl(imgUrl) : '/assets/image/category/kalaye-degital.png'} 
                                                        style={{ width: '70%', height: '70%', objectFit: 'contain', transition: 'transform 0.4s ease' }} 
                                                        alt={cat.title} 
                                                        className="cat-img"
                                                        onError={(e) => { 
                                                            e.target.onerror = null; 
                                                            e.target.src = '/assets/image/category/kalaye-degital.png'; 
                                                        }}
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
                    )}
                </div>
            </section>

            <div className="container-fluid">
                <div className="row gy-4">
                    
                    <div className="col-lg-3 d-lg-none d-block">
                        <button className="btn btn-filter-float border-0 bg-danger shadow-lg px-4 py-2 rounded-3 position-fixed d-flex flex-column align-items-center justify-content-center" style={{zIndex: 1040, bottom: '80px', left: '20px'}} type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasFilter" aria-controls="offcanvasFilter">
                            <i className="bi bi-funnel font-20 fw-bold text-white"></i>
                            <span className="d-block font-12 fw-bold text-white mt-1">فیلترها</span>
                        </button>

                        <div className="offcanvas offcanvas-start" tabIndex="-1" id="offcanvasFilter">
                            <div className="offcanvas-header border-bottom">
                                <h5 className="offcanvas-title fw-bold">فیلتر محصولات</h5>
                                <button type="button" className="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
                            </div>
                            <div className="offcanvas-body bg-light">
                                {renderSidebarFilters(true)}
                            </div>
                        </div>
                    </div>

                    <div className="col-lg-3 d-lg-block d-none">
                        <div className="sticky-top" style={{top: '100px', zIndex: 10}}>
                            {renderSidebarFilters(false)}
                        </div>
                    </div>

                    <div className="col-lg-9">
                        
                        <div className="category-sort mb-4 bg-white rounded-4 shadow-sm border border-ui p-3">
                            <div className="d-flex align-items-center justify-content-between flex-wrap gap-3">
                                
                                <div className="box_filter d-lg-block d-none">
                                    <ul className="list-inline text-start mb-0 d-flex align-items-center m-0 p-0">
                                        <li className="list-inline-item title-font ms-3 fw-bold text-muted"><i className="bi bi-sort-down me-1"></i> مرتب‌سازی بر اساس:</li>
                                        <li className="list-inline-item"><button onClick={() => { setOrdering('-base_price'); setPage(1); }} className={`btn btn-sm ${ordering === '-base_price' ? 'text-danger fw-bold border-bottom border-danger border-2 rounded-0 pb-1' : 'text-muted'}`}>گران‌ترین</button></li>
                                        <li className="list-inline-item"><button onClick={() => { setOrdering('base_price'); setPage(1); }} className={`btn btn-sm ${ordering === 'base_price' ? 'text-danger fw-bold border-bottom border-danger border-2 rounded-0 pb-1' : 'text-muted'}`}>ارزان‌ترین</button></li>
                                        <li className="list-inline-item"><button onClick={() => { setOrdering('-sold_count'); setPage(1); }} className={`btn btn-sm ${ordering === '-sold_count' ? 'text-danger fw-bold border-bottom border-danger border-2 rounded-0 pb-1' : 'text-muted'}`}>پرفروش‌ترین</button></li>
                                        <li className="list-inline-item"><button onClick={() => { setOrdering('-view_count'); setPage(1); }} className={`btn btn-sm ${ordering === '-view_count' ? 'text-danger fw-bold border-bottom border-danger border-2 rounded-0 pb-1' : 'text-muted'}`}>محبوب‌ترین</button></li>
                                        <li className="list-inline-item"><button onClick={() => { setOrdering('-created_at'); setPage(1); }} className={`btn btn-sm ${ordering === '-created_at' ? 'text-danger fw-bold border-bottom border-danger border-2 rounded-0 pb-1' : 'text-muted'}`}>جدیدترین</button></li>
                                    </ul>
                                </div>
                                
                                <div className="d-lg-none d-block w-100">
                                    <h6 className="font-14 text-muted mb-2"><i className="bi bi-sort-down me-1"></i> مرتب‌سازی:</h6>
                                    <select className="form-select bg-light border-0 shadow-none fw-bold text-dark font-14" value={ordering} onChange={(e) => { setOrdering(e.target.value); setPage(1); }}>
                                        <option value="-created_at">جدیدترین</option>
                                        <option value="-base_price">گران‌ترین</option>
                                        <option value="base_price">ارزان‌ترین</option>
                                        <option value="-sold_count">پرفروش‌ترین</option>
                                        <option value="-view_count">محبوب‌ترین</option>
                                    </select>
                                </div>

                                <div className="box_filter_counter font-14 text-muted fw-bold d-none d-sm-block bg-light px-3 py-2 rounded-pill">
                                    <i className="bi bi-box-seam me-2"></i> {pagination.count} کالا
                                </div>
                            </div>
                        </div>

                        <div className="row gy-4">
                            {loading ? (
                                <div className="col-12 text-center py-5 my-5">
                                    <div className="spinner-border text-danger" role="status" style={{width: '3rem', height: '3rem'}}></div>
                                    <p className="mt-3 fw-bold text-muted font-16">در حال دریافت کالاها...</p>
                                </div>
                            ) : products.length > 0 ? (
                                products.map(product => (
                                    <div className="col-xl-4 col-md-6 col-sm-6 col-12" key={product.uuid}>
                                        <ProductCard product={product} />
                                    </div>
                                ))
                            ) : (
                                <div className="col-12 text-center py-5 my-5 bg-white rounded-4 shadow-sm border border-ui">
                                    <i className="bi bi-search fs-1 text-muted opacity-50 mb-3 d-block"></i>
                                    <h4 className="text-muted fw-bold mb-3">کالایی در این بخش یافت نشد!</h4>
                                    <button className="btn btn-outline-danger rounded-pill px-4" onClick={clearAllFilters}>
                                        حذف همه فیلترها و مشاهده کل فروشگاه
                                    </button>
                                </div>
                            )}
                        </div>

                        {totalPages > 1 && (
                            <div className="my-paginate mt-5 d-flex justify-content-center">
                                <nav aria-label="Page navigation">
                                    <ul className="pagination flex-wrap justify-content-center gap-2">
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
                        
                        <div className="col-12 mt-5 mb-3">
                            <div className="content-box bg-white p-4 rounded-4 shadow-sm border border-ui position-relative overflow-hidden">
                                <input className="read-more-state d-none" id="readMoreShop" type="checkbox" checked={isReadMoreOpen} onChange={() => setIsReadMoreOpen(!isReadMoreOpen)} />
                                <div className="read-more-wrap">
                                    <h6 className="font-20 mb-3 title-font fw-900 border-bottom pb-2 d-inline-block border-danger border-2">
                                        فروشگاه اینترنتی {settings?.site_name || '...'}
                                    </h6>
                                    <div className={`text-muted lh-lg text-justify font-14 ${isReadMoreOpen ? '' : 'text-truncate-3'}`} style={!isReadMoreOpen ? {maxHeight: '75px', overflow: 'hidden'} : {}}>
                                        <p dangerouslySetInnerHTML={{ __html: settings?.about_us_footer?.replace(/\n/g, '<br/>') || '' }}></p>
                                    </div>
                                </div>
                                <label className="read-more-trigger text-center mt-3 d-block w-100 cursor-pointer" htmlFor="readMoreShop">
                                    <span className="btn btn-sm btn-light border rounded-pill px-4 fw-bold text-danger hover-lift">
                                        {isReadMoreOpen ? 'بستن توضیحات' : 'مشاهده بیشتر'} <i className={`bi bi-chevron-${isReadMoreOpen ? 'up' : 'down'} ms-1`}></i>
                                    </span>
                                </label>
                                {!isReadMoreOpen && <div className="position-absolute bottom-0 start-0 w-100 h-50 pointer-events-none" style={{background: 'linear-gradient(to top, white 20%, transparent)'}}></div>}
                            </div>
                        </div>

                    </div>
                </div>
            </div>

            <style jsx="true">{`
                .hover-lift { transition: transform 0.2s ease, box-shadow 0.2s ease; }
                .hover-lift:hover { transform: translateY(-4px); box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important; }
                .cursor-pointer { cursor: pointer; }
                .transition-all { transition: all 0.3s ease; }

                .custom-checkbox { width: 18px; height: 18px; border-radius: 4px; }
                .custom-checkbox:checked { background-color: #ef4056 !important; border-color: #ef4056 !important; }

                .custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #ddd; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #ef4056; }
                
                .group-cat-item { cursor: pointer; }
                .group-cat-item:hover .inner-cat-circle { 
                    border-color: #ef4056 !important; 
                    box-shadow: 0 0 0 4px rgba(239, 64, 86, 0.15) !important; 
                }
                .group-cat-item:hover .cat-img { transform: scale(1.15) !important; }
                .group-cat-item:hover .group-cat-text { color: #ef4056 !important; }
            `}</style>
        </main>
    );
};

export default ShopPage;