import React, { useState, useEffect, useRef, useContext } from 'react';
import { useSearchParams, useParams, Link, useLocation } from 'react-router-dom';
import Slider from 'rc-slider';
import 'rc-slider/assets/index.css';
import { Swiper, SwiperSlide } from 'swiper/react';
import { FreeMode } from 'swiper/modules';

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
    const { slug: categorySlugParam } = useParams();
    const { settings } = useContext(SiteContext); 
    const topRef = useRef(null);
    
    const isSpecialOffers = location.pathname.includes('special-offers');
    const isBestSellers = location.pathname.includes('best-sellers');

    const [products, setProducts] = useState([]);
    const [totalCount, setTotalCount] = useState(0);
    const [categories, setCategories] = useState([]);
    const [brands, setBrands] = useState([]);
    
    const [loading, setLoading] = useState(true);
    const [filtersLoading, setFiltersLoading] = useState(true);
    const [isMaxPriceLoaded, setIsMaxPriceLoaded] = useState(false);
    
    const [maxPriceLimit, setMaxPriceLimit] = useState(MAX_PRICE_LIMIT);

    const page = parseInt(searchParams.get('page') || '1');
    const ordering = searchParams.get('ordering') || (isBestSellers ? '-sold_count' : '-created_at');
    const searchQuery = searchParams.get('search') || '';
    const categorySlug = searchParams.get('category__slug') || categorySlugParam || '';
    const selectedBrands = searchParams.get('brands') ? searchParams.get('brands').split(',') : [];
    const hasDiscount = searchParams.get('has_discount') === 'true' || isSpecialOffers;
    const hasStock = searchParams.get('has_stock') === 'true';
    const minPriceParam = searchParams.get('min_price') ? parseInt(searchParams.get('min_price')) : 0;
    const maxPriceParam = searchParams.get('max_price') ? parseInt(searchParams.get('max_price')) : null;

    const [localPriceRange, setLocalPriceRange] = useState([minPriceParam, maxPriceParam || MAX_PRICE_LIMIT]);
    const [isMobileFilterOpen, setIsMobileFilterOpen] = useState(false);
    const [isReadMoreOpen, setIsReadMoreOpen] = useState(false);

    useEffect(() => {
        const fetchFiltersData = async () => {
            try {
                setFiltersLoading(true);
                const [catsData, brandsData, fetchedMaxPrice] = await Promise.all([
                    getCategoryTree(),
                    getBrandsList(),
                    getMaxPrice()
                ]);
                
                setCategories(catsData || []);
                setBrands(brandsData?.results || brandsData || []);
                
                const finalMaxPrice = fetchedMaxPrice > 0 ? fetchedMaxPrice : MAX_PRICE_LIMIT;
                setMaxPriceLimit(finalMaxPrice);
                
                if (maxPriceParam === null) {
                    setLocalPriceRange([minPriceParam, finalMaxPrice]);
                } else {
                    setLocalPriceRange([minPriceParam, maxPriceParam]);
                }
                setIsMaxPriceLoaded(true);

            } catch (error) {
                console.error("Error fetching filter data:", error);
            } finally {
                setFiltersLoading(false);
            }
        };
        fetchFiltersData();
    }, []);

    useEffect(() => {
        const fetchProducts = async () => {
            setLoading(true);
            try {
                const apiParams = new URLSearchParams();
                
                if (page > 1) apiParams.set('page', page);
                if (ordering) apiParams.set('ordering', ordering);
                if (searchQuery) apiParams.set('search', searchQuery);
                if (categorySlug) apiParams.set('category__slug', categorySlug);
                if (selectedBrands.length > 0) apiParams.set('brands', selectedBrands.join(','));
                
                if (hasStock) apiParams.set('has_stock', 'true');
                
                if (isSpecialOffers) {
                    apiParams.set('is_special_offer', 'true');
                } else if (hasDiscount) {
                    apiParams.set('has_discount', 'true');
                }

                if (minPriceParam > 0) apiParams.set('min_price', minPriceParam);
                if (maxPriceParam && maxPriceParam < maxPriceLimit) apiParams.set('max_price', maxPriceParam);

                const data = await getProductsList(apiParams.toString());
                setProducts(data.results || data || []);
                setTotalCount(data.count || 0);

                if (topRef.current) {
                    topRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            } catch (error) {
                console.error("Error fetching products:", error);
            } finally {
                setLoading(false);
            }
        };

        if (isMaxPriceLoaded) {
            fetchProducts();
        }
    }, [searchParams, isMaxPriceLoaded]);

    const updateQueryParam = (key, value) => {
        const newParams = new URLSearchParams(searchParams);
        if (value === null || value === '' || value === false) {
            newParams.delete(key);
        } else {
            newParams.set(key, value);
        }
        if (key !== 'page') newParams.set('page', '1');
        setSearchParams(newParams);
    };

    const handleBrandToggle = (slug) => {
        const current = [...selectedBrands];
        const index = current.indexOf(slug);
        if (index > -1) current.splice(index, 1);
        else current.push(slug);
        
        updateQueryParam('brands', current.join(','));
    };

    const applyPriceFilter = () => {
        const newParams = new URLSearchParams(searchParams);
        
        if (localPriceRange[0] > 0) newParams.set('min_price', localPriceRange[0]);
        else newParams.delete('min_price');
        
        if (localPriceRange[1] < maxPriceLimit) newParams.set('max_price', localPriceRange[1]);
        else newParams.delete('max_price');
        
        newParams.set('page', '1');
        setSearchParams(newParams);
    };

    const clearFilters = () => {
        setSearchParams(new URLSearchParams());
        setLocalPriceRange([0, maxPriceLimit]);
    };

    const totalPages = Math.ceil(totalCount / 9);

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
        let foundTitle = 'دسته‌بندی';
        const searchTree = (nodes) => {
            for (let node of nodes) {
                if (node.slug === categorySlug) foundTitle = node.title;
                if (node.children) searchTree(node.children);
            }
        };
        searchTree(categories);
        
        pageTitleText = 'محصولات';
        pageTitleHighlight = foundTitle;
        pageIcon = 'bi-box-seam text-primary';
    } else {
        pageTitleText = 'فروشگاه';
        pageTitleHighlight = settings?.site_name || '...';
        pageIcon = 'bi-shop text-success';
    }

    const renderCategoriesTree = (nodes) => {
        return nodes.map(cat => (
            <div key={cat.uuid} className="mb-1">
                <div 
                    className={`d-flex align-items-center justify-content-between p-2 rounded-3 cursor-pointer transition ${categorySlug === cat.slug ? 'bg-danger text-white' : 'hover-bg-light text-dark'}`}
                    onClick={() => updateQueryParam('category__slug', categorySlug === cat.slug ? null : cat.slug)}
                >
                    <span className="font-13 fw-bold">{cat.title}</span>
                    {cat.children && cat.children.length > 0 && <i className="bi bi-chevron-down font-10"></i>}
                </div>
                {cat.children && cat.children.length > 0 && categorySlug !== cat.slug && (
                    <div className="ps-3 border-start border-light ms-2 mt-1">
                        {renderCategoriesTree(cat.children)}
                    </div>
                )}
            </div>
        ));
    };

    const renderSidebarFilters = (isMobile) => {
        const prefixId = isMobile ? 'mob-' : 'desk-'; 
        
        return (
            <aside>
                <div className="d-flex align-items-center justify-content-between mb-4 d-lg-none p-3 border-bottom bg-white sticky-top">
                    <h5 className="fw-900 m-0"><i className="bi bi-funnel text-danger me-2"></i> فیلتر محصولات</h5>
                    <button className="btn p-0 text-dark" onClick={() => setIsMobileFilterOpen(false)}><i className="bi bi-x-lg fs-4"></i></button>
                </div>

                <section className="mb-4 border-ui shadow-sm filter-container bg-white p-4 rounded-4 mx-3 mx-lg-0">
                    <div className="d-flex justify-content-between align-items-center mb-3">
                        <label htmlFor={`${prefixId}search-products`} className="filter-title fw-bold m-0 font-15">جستجو</label>
                        {(searchQuery || hasDiscount || hasStock || selectedBrands.length > 0 || minPriceParam > 0 || maxPriceParam) && (
                            <button onClick={clearFilters} className="btn btn-sm btn-link text-danger font-12 p-0 text-decoration-none fw-bold">حذف همه</button>
                        )}
                    </div>
                    <div className="position-relative">
                        <input 
                            id={`${prefixId}search-products`}
                            type="text" 
                            className="form-control py-3 rounded-3 w-100 bg-light border-0 shadow-none font-13 pe-5" 
                            placeholder="نام محصول، برند و..."
                            value={searchQuery}
                            onChange={(e) => updateQueryParam('search', e.target.value)}
                        />
                        <span className="position-absolute me-3 end-0 top-50 translate-middle-y text-muted"><i className="bi bi-search fs-5"></i></span>
                    </div>
                </section>

                {categories.length > 0 && (
                    <section className="mb-4 border-ui shadow-sm filter-container bg-white p-4 rounded-4 mx-3 mx-lg-0">
                        <h2 className="filter-title fw-bold mb-4 font-15">دسته‌بندی‌ها</h2>
                        <div className="categories-tree custom-scrollbar pe-2" style={{maxHeight: '200px', overflowY: 'auto'}}>
                            {renderCategoriesTree(categories)}
                        </div>
                    </section>
                )}

                <section className="mb-4 border-ui shadow-sm filter-container bg-white p-4 rounded-4 mx-3 mx-lg-0 d-flex flex-column gap-3">
                    <div className="form-check form-switch d-flex justify-content-between ps-0 m-0 cursor-pointer" onClick={() => updateQueryParam('has_stock', hasStock ? null : 'true')}>
                        <label className="form-check-label font-13 fw-bold text-dark cursor-pointer pt-1">فقط کالاهای موجود</label>
                        <input className="form-check-input cursor-pointer m-0 shadow-none border-ui" type="checkbox" role="switch" checked={hasStock} readOnly />
                    </div>
                    {!isSpecialOffers && (
                        <div className="form-check form-switch d-flex justify-content-between ps-0 m-0 cursor-pointer" onClick={() => updateQueryParam('has_discount', hasDiscount ? null : 'true')}>
                            <label className="form-check-label font-13 fw-bold text-dark cursor-pointer pt-1">فقط تخفیف‌دارها</label>
                            <input className="form-check-input cursor-pointer m-0 shadow-none border-ui" type="checkbox" role="switch" checked={hasDiscount} readOnly />
                        </div>
                    )}
                </section>

                <section className="mb-4 border-ui shadow-sm filter-container bg-white p-4 rounded-4 mx-3 mx-lg-0">
                    <h2 className="filter-title fw-bold mb-4 font-15">محدوده قیمت</h2>
                    <div className="px-3 mb-5 mt-4" dir="rtl">
                        {isMaxPriceLoaded ? (
                            <Slider
                                range
                                reverse={true}
                                min={0}
                                max={maxPriceLimit}
                                step={50000}
                                value={localPriceRange}
                                onChange={(val) => setLocalPriceRange(val)}
                                className="custom-rc-slider"
                            />
                        ) : (
                            <div className="text-center text-muted font-12"><div className="spinner-grow spinner-grow-sm text-danger me-2"></div>بارگذاری بازه قیمت...</div>
                        )}
                    </div>
                    
                    <div className="d-flex align-items-center justify-content-between mt-4 bg-light rounded-3 p-3 border border-ui mb-3">
                        <div className="d-flex flex-column align-items-start">
                            <span className="font-11 text-muted mb-1">از</span>
                            <span className="font-13 fw-bold text-dark">
                                {new Intl.NumberFormat('fa-IR').format(localPriceRange[0])} <span className="font-10 fw-normal text-muted">تومان</span>
                            </span>
                        </div>
                        <div className="text-muted"><i className="bi bi-arrow-left"></i></div>
                        <div className="d-flex flex-column align-items-end">
                            <span className="font-11 text-muted mb-1">تا</span>
                            <span className="font-13 fw-bold text-dark">
                                {new Intl.NumberFormat('fa-IR').format(localPriceRange[1])} <span className="font-10 fw-normal text-muted">تومان</span>
                            </span>
                        </div>
                    </div>
                    <button onClick={applyPriceFilter} className="btn btn-outline-danger w-100 rounded-pill py-2 font-12 fw-bold hover-lift shadow-sm">اعمال محدوده قیمت</button>
                </section>

                {brands.length > 0 && (
                    <section className="mb-4 border-ui shadow-sm filter-container bg-white p-4 rounded-4 mx-3 mx-lg-0">
                        <h2 className="filter-title fw-bold mb-4 font-15">برندها</h2>
                        <div className="brands-list custom-scrollbar pe-2 d-flex flex-column gap-2" style={{maxHeight: '220px', overflowY: 'auto'}}>
                            {brands.map(brand => (
                                <div key={brand.uuid} className="form-check d-flex align-items-center m-0 p-0 cursor-pointer hover-bg-light rounded-3 transition p-2" onClick={() => handleBrandToggle(brand.slug)}>
                                    <input 
                                        className="form-check-input ms-2 cursor-pointer shadow-none flex-shrink-0" 
                                        type="checkbox" 
                                        checked={selectedBrands.includes(brand.slug)} 
                                        readOnly 
                                    />
                                    <label className="form-check-label font-13 text-dark flex-grow-1 cursor-pointer pt-1 text-truncate" style={{maxWidth: '130px'}}>
                                        {brand.title}
                                    </label>
                                    <span className="badge bg-secondary bg-opacity-10 text-muted font-10 rounded-pill px-2">{brand.product_count || 0}</span>
                                </div>
                            ))}
                        </div>
                    </section>
                )}
            </aside>
        );
    };

    return (
        <main className="shop-page-wrapper py-4 bg-light" ref={topRef}>
            
            <section className="card-categories site-slider bg-white pt-4 pb-2 border-bottom mb-4 shadow-sm">
                <div className="container-fluid container-xl">
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
                                    <Link to={`/shop?category__slug=${cat.slug}`} className="text-decoration-none">
                                        <div className="cat-item d-flex flex-column align-items-center mx-2 mx-md-3 group-cat-item">
                                            <div className="cat-item-image bg-light rounded-4 d-flex align-items-center justify-content-center mb-3 position-relative z-1 shadow-sm border border-ui" style={{ width: '110px', height: '110px', padding: '10px' }}>
                                                <div className="bg-white rounded-circle w-100 h-100 d-flex align-items-center justify-content-center overflow-hidden inner-cat-circle" style={{ transition: 'all 0.3s ease' }}>
                                                    <img 
                                                        src={imgUrl ? resolveImageUrl(imgUrl) : '/assets/image/category/kalaye-degital.png'} 
                                                        style={{ width: '70%', height: '70%', objectFit: 'contain', transition: 'transform 0.4s ease' }} 
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
                    )}
                </div>
            </section>

            <div className="container-fluid container-xl">
                <div className="row gy-4">
                    
                    <div className="col-12 d-lg-none d-block">
                        <div className="d-flex align-items-center justify-content-between bg-white rounded-pill shadow-sm border border-ui p-2">
                            <button className="btn btn-danger rounded-pill font-13 fw-bold d-flex align-items-center gap-2" onClick={() => setIsMobileFilterOpen(true)}>
                                <i className="bi bi-funnel"></i> فیلتر محصولات
                            </button>
                            <div className="font-12 text-muted fw-bold pe-3">
                                <span className="text-dark fs-6 ms-1">{totalCount}</span> کالا
                            </div>
                        </div>

                        {isMobileFilterOpen && <div className="modal-backdrop fade show d-lg-none" style={{zIndex: 1040}} onClick={() => setIsMobileFilterOpen(false)}></div>}

                        <div className={`filter-sidebar-mobile d-lg-none ${isMobileFilterOpen ? 'show' : ''}`}>
                            <div className="filter-sidebar-content bg-light h-100 overflow-auto">
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
                        
                        <div className="category-sort mb-4 bg-white rounded-4 shadow-sm border border-ui p-3 d-none d-lg-block">
                            <div className="d-flex align-items-center justify-content-between">
                                <ul className="list-inline text-start mb-0 d-flex align-items-center m-0 p-0 gap-3">
                                    <li className="list-inline-item ms-3 fw-bold text-muted font-13"><i className="bi bi-sort-down me-1 fs-5 align-middle"></i> مرتب‌سازی بر اساس:</li>
                                    <li className="list-inline-item m-0"><button onClick={() => updateQueryParam('ordering', '-created_at')} className={`btn btn-sm rounded-pill font-13 px-3 transition ${ordering === '-created_at' ? 'bg-danger text-white fw-bold shadow-sm' : 'text-muted hover-bg-light'}`}>جدیدترین</button></li>
                                    <li className="list-inline-item m-0"><button onClick={() => updateQueryParam('ordering', '-sold_count')} className={`btn btn-sm rounded-pill font-13 px-3 transition ${ordering === '-sold_count' ? 'bg-danger text-white fw-bold shadow-sm' : 'text-muted hover-bg-light'}`}>پرفروش‌ترین</button></li>
                                    <li className="list-inline-item m-0"><button onClick={() => updateQueryParam('ordering', 'base_price')} className={`btn btn-sm rounded-pill font-13 px-3 transition ${ordering === 'base_price' ? 'bg-danger text-white fw-bold shadow-sm' : 'text-muted hover-bg-light'}`}>ارزان‌ترین</button></li>
                                    <li className="list-inline-item m-0"><button onClick={() => updateQueryParam('ordering', '-base_price')} className={`btn btn-sm rounded-pill font-13 px-3 transition ${ordering === '-base_price' ? 'bg-danger text-white fw-bold shadow-sm' : 'text-muted hover-bg-light'}`}>گران‌ترین</button></li>
                                    <li className="list-inline-item m-0"><button onClick={() => updateQueryParam('ordering', '-view_count')} className={`btn btn-sm rounded-pill font-13 px-3 transition ${ordering === '-view_count' ? 'bg-danger text-white fw-bold shadow-sm' : 'text-muted hover-bg-light'}`}>محبوب‌ترین</button></li>
                                </ul>
                                <div className="font-13 text-muted fw-bold bg-light px-3 py-2 rounded-pill border border-ui">
                                    <i className="bi bi-box-seam me-2"></i> {totalCount} کالا
                                </div>
                            </div>
                        </div>

                        <div className="d-lg-none d-block w-100 mb-4 bg-white rounded-pill shadow-sm border border-ui px-3 py-1">
                            <div className="d-flex align-items-center">
                                <i className="bi bi-sort-down me-2 text-danger fs-4"></i>
                                <select className="form-select border-0 shadow-none fw-bold text-dark font-13 bg-transparent p-2" value={ordering} onChange={(e) => updateQueryParam('ordering', e.target.value)}>
                                    <option value="-created_at">جدیدترین محصولات</option>
                                    <option value="-sold_count">پرفروش‌ترین محصولات</option>
                                    <option value="base_price">ارزان‌ترین محصولات</option>
                                    <option value="-base_price">گران‌ترین محصولات</option>
                                    <option value="-view_count">محبوب‌ترین محصولات</option>
                                </select>
                            </div>
                        </div>

                        <div className="row gy-4 gx-3">
                            {loading ? (
                                <div className="col-12 text-center py-5 my-5">
                                    <div className="spinner-border text-danger mb-3" style={{width: '3.5rem', height: '3.5rem', borderWidth: '0.25rem'}} role="status"></div>
                                    <p className="fw-bold text-muted font-14">در حال جستجو و دریافت محصولات...</p>
                                </div>
                            ) : products.length > 0 ? (
                                products.map(product => (
                                    <div className="col-6 col-md-4 col-xl-4" key={product.uuid}>
                                        <ProductCard product={product} />
                                    </div>
                                ))
                            ) : (
                                <div className="col-12 text-center py-5 my-5 bg-white rounded-4 shadow-sm border border-ui d-flex flex-column align-items-center">
                                    <i className="bi bi-search fs-1 text-muted opacity-25 mb-4 d-block" style={{fontSize: '5rem !important'}}></i>
                                    <h4 className="text-dark fw-900 mb-3">محصولی با این مشخصات یافت نشد!</h4>
                                    <p className="text-muted font-13 mb-4">لطفاً فیلترها را تغییر دهید یا عبارت دیگری را جستجو کنید.</p>
                                    <button className="btn btn-danger rounded-pill px-5 py-2 font-13 fw-bold shadow-sm hover-lift" onClick={clearFilters}>
                                        حذف فیلترها و مشاهده همه
                                    </button>
                                </div>
                            )}
                        </div>

                        {!loading && totalPages > 1 && (
                            <div className="d-flex justify-content-center mt-5 mb-3">
                                <nav aria-label="Page navigation">
                                    <ul className="pagination gap-2 m-0 bg-white p-2 rounded-pill shadow-sm border border-ui">
                                        <li className={`page-item ${page === 1 ? 'disabled' : ''}`}>
                                            <button className="page-link rounded-circle border-0 d-flex align-items-center justify-content-center shadow-none bg-light text-dark hover-bg-danger hover-text-white transition" style={{width:'40px', height:'40px'}} onClick={() => updateQueryParam('page', page - 1)}>
                                                <i className="bi bi-chevron-right font-14"></i>
                                            </button>
                                        </li>
                                        
                                        {Array.from({ length: totalPages }, (_, i) => i + 1).map(p => {
                                            if (p === 1 || p === totalPages || (p >= page - 1 && p <= page + 1)) {
                                                return (
                                                    <li key={p} className="page-item">
                                                        <button 
                                                            className={`page-link rounded-circle border-0 d-flex align-items-center justify-content-center shadow-none transition font-14 fw-bold ${page === p ? 'bg-danger text-white shadow-sm' : 'bg-transparent text-dark hover-bg-light'}`} 
                                                            style={{width:'40px', height:'40px'}}
                                                            onClick={() => updateQueryParam('page', p)}
                                                        >
                                                            {p}
                                                        </button>
                                                    </li>
                                                );
                                            } else if (p === page - 2 || p === page + 2) {
                                                return <li key={p} className="page-item disabled"><span className="page-link border-0 bg-transparent text-muted">...</span></li>;
                                            }
                                            return null;
                                        })}

                                        <li className={`page-item ${page === totalPages ? 'disabled' : ''}`}>
                                            <button className="page-link rounded-circle border-0 d-flex align-items-center justify-content-center shadow-none bg-light text-dark hover-bg-danger hover-text-white transition" style={{width:'40px', height:'40px'}} onClick={() => updateQueryParam('page', page + 1)}>
                                                <i className="bi bi-chevron-left font-14"></i>
                                            </button>
                                        </li>
                                    </ul>
                                </nav>
                            </div>
                        )}
                        
                        <div className="content-box bg-white p-4 p-md-5 rounded-4 shadow-sm border border-ui position-relative overflow-hidden mt-5 mb-2">
                            <input className="read-more-state d-none" id="readMoreShop" type="checkbox" checked={isReadMoreOpen} onChange={() => setIsReadMoreOpen(!isReadMoreOpen)} />
                            <div className="read-more-wrap">
                                <h6 className="font-18 mb-4 title-font fw-900 border-bottom pb-3 d-inline-block border-danger border-3 rounded-1">
                                    فروشگاه اینترنتی {settings?.site_name || '...'}
                                </h6>
                                <div className={`text-muted lh-lg text-justify font-14 ${isReadMoreOpen ? '' : 'text-truncate-3'}`} style={!isReadMoreOpen ? {maxHeight: '85px', overflow: 'hidden'} : {}}>
                                    <p dangerouslySetInnerHTML={{ __html: settings?.about_us_footer?.replace(/\n/g, '<br/>') || 'توضیحاتی برای فروشگاه ثبت نشده است.' }}></p>
                                </div>
                            </div>
                            <label className="read-more-trigger text-center mt-4 d-block w-100 cursor-pointer position-relative z-3" htmlFor="readMoreShop">
                                <span className="btn btn-sm bg-white border border-danger rounded-pill px-4 py-2 fw-bold text-danger hover-lift shadow-sm">
                                    {isReadMoreOpen ? 'بستن توضیحات' : 'مشاهده بیشتر'} <i className={`bi bi-chevron-${isReadMoreOpen ? 'up' : 'down'} ms-1`}></i>
                                </span>
                            </label>
                            {!isReadMoreOpen && <div className="position-absolute bottom-0 start-0 w-100 h-50 pointer-events-none z-2" style={{background: 'linear-gradient(to top, white 20%, transparent)'}}></div>}
                        </div>
                    </div>
                </div>
            </div>

            <style jsx="true">{`
                .hover-lift { transition: transform 0.2s ease, box-shadow 0.2s ease; }
                .hover-lift:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important; }
                .cursor-pointer { cursor: pointer; }
                .transition-all { transition: all 0.3s ease; }
                .hover-bg-light:hover { background-color: #f8f9fa !important; }
                .hover-text-danger:hover { color: #ef4056 !important; }

                .custom-checkbox { width: 18px; height: 18px; border-radius: 4px; }
                .custom-checkbox:checked { background-color: #ef4056 !important; border-color: #ef4056 !important; }

                .custom-scrollbar::-webkit-scrollbar { width: 5px; height: 5px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #dee2e6; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #ef4056; }
                
                .group-cat-item { cursor: pointer; }
                .group-cat-item:hover .inner-cat-circle { 
                    border-color: #ef4056 !important; 
                    box-shadow: 0 0 0 4px rgba(239, 64, 86, 0.15) !important; 
                }
                .group-cat-item:hover .cat-img { transform: scale(1.15) !important; }
                .group-cat-item:hover .group-cat-text { color: #ef4056 !important; }

                @media (max-width: 991.98px) {
                    .filter-sidebar-mobile {
                        position: fixed;
                        top: 0;
                        right: -100%;
                        width: 320px;
                        max-width: 85vw;
                        height: 100vh;
                        z-index: 1050;
                        transition: right 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                        box-shadow: -5px 0 25px rgba(0,0,0,0.1);
                    }
                    .filter-sidebar-mobile.show { right: 0; }
                }
            `}</style>
        </main>
    );
};

export default ShopPage;