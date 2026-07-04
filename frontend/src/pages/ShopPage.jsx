// arkkala/frontend/src/pages/ShopPage.jsx
import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, useParams, Link } from 'react-router-dom';
import Nouislider from 'nouislider-react';
import 'nouislider/dist/nouislider.css';
import { Swiper, SwiperSlide } from 'swiper/react';
import { FreeMode } from 'swiper/modules';

import { getProductsList } from '../api/shopApi';
import { getCategoryTree, getBrandsList } from '../api/searchApi';
import ProductCard from '../components/ProductCard';

const ShopPage = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const { slug: categorySlug } = useParams();
    
    // --- Data States ---
    const [products, setProducts] = useState([]);
    const [pagination, setPagination] = useState({ count: 0, next: null, previous: null });
    const [categories, setCategories] = useState([]);
    const [brands, setBrands] = useState([]);
    const [loading, setLoading] = useState(true);
    
    // --- Filter States ---
    const initialMin = Number(searchParams.get('min_price')) || 0;
    const initialMax = Number(searchParams.get('max_price')) || 17700000;
    
    const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '');
    const [ordering, setOrdering] = useState(searchParams.get('ordering') || '-created_at');
    
    const [priceRange, setPriceRange] = useState([initialMin, initialMax]);
    const [displayPrice, setDisplayPrice] = useState([initialMin, initialMax]);
    const [sliderKey, setSliderKey] = useState(Date.now());

    const [stockStatus, setStockStatus] = useState(searchParams.get('has_stock') || 'all'); 
    const [hasDiscount, setHasDiscount] = useState(searchParams.get('has_discount') === 'true');
    const [selectedBrands, setSelectedBrands] = useState(searchParams.get('brands') ? searchParams.get('brands').split(',') : []);
    const [page, setPage] = useState(Number(searchParams.get('page')) || 1);
    
    // --- UI States ---
    const [isReadMoreOpen, setIsReadMoreOpen] = useState(false);
    const filterTimeoutRef = useRef(null);

    useEffect(() => {
        getCategoryTree().then(setCategories).catch(console.error);
        getBrandsList().then(data => setBrands(data.results || data)).catch(console.error);
    }, []);

    const fetchProducts = async (queryString) => {
        setLoading(true);
        try {
            const data = await getProductsList(queryString);
            setProducts(data.results || data);
            if (data.count !== undefined) {
                setPagination({ count: data.count, next: data.next, previous: data.previous });
            }
        } catch (error) {
            console.error("Error fetching products:", error);
        } finally {
            setLoading(false);
        }
    };

    const applyFilters = () => {
        const params = new URLSearchParams();
        if (searchQuery) params.set('search', searchQuery);
        if (ordering) params.set('ordering', ordering);
        
        if (stockStatus === 'available') params.set('has_stock', 'true');
        if (stockStatus === 'unavailable') params.set('has_stock', 'false');
        
        if (hasDiscount) params.set('has_discount', 'true');
        if (priceRange[0] > 0) params.set('min_price', priceRange[0]);
        if (priceRange[1] < 17700000) params.set('max_price', priceRange[1]);
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
        // eslint-disable-next-line
    }, [searchQuery, ordering, stockStatus, hasDiscount, priceRange[0], priceRange[1], selectedBrands.join(','), page, categorySlug]);

    const handleSliderUpdate = (render, handle, value) => {
        setDisplayPrice([Math.round(value[0]), Math.round(value[1])]);
    };

    const handleSliderChange = (render, handle, value) => {
        setPriceRange([Math.round(value[0]), Math.round(value[1])]);
        setPage(1);
    };

    const toggleBrand = (slug) => {
        setSelectedBrands(prev => prev.includes(slug) ? prev.filter(b => b !== slug) : [...prev, slug]);
        setPage(1);
    };

    const clearAllFilters = () => {
        setSearchQuery('');
        setPriceRange([0, 17700000]);
        setDisplayPrice([0, 17700000]);
        setHasDiscount(false);
        setStockStatus('all');
        setSelectedBrands([]);
        setPage(1);
        setSliderKey(Date.now());
    };

    const totalPages = Math.ceil(pagination.count / 15);


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
                        <div className="px-2 mb-5">
                            <Nouislider 
                                key={sliderKey}
                                className="custom-react-slider"
                                range={{ min: 0, max: 17700000 }} 
                                start={displayPrice} 
                                connect={true} 
                                step={100000}
                                direction="rtl" 
                                onUpdate={handleSliderUpdate}
                                onChange={handleSliderChange}
                            />
                        </div>
                        
                        <div className="d-flex align-items-center justify-content-between mt-4 gap-2">
                            <div className="d-flex flex-column align-items-center flex-grow-1 w-45">
                                <input 
                                    type="text" 
                                    value={new Intl.NumberFormat('fa-IR').format(displayPrice[0])} 
                                    className="form-control text-center font-14 fw-bold bg-light border-0 shadow-none py-2 rounded-3" 
                                    disabled 
                                />
                                <span className="font-12 text-muted mt-2">تومان</span>
                            </div>
                            
                            <div className="fw-bold text-muted font-14 mb-4">تا</div>
                            
                            <div className="d-flex flex-column align-items-center flex-grow-1 w-45">
                                <input 
                                    type="text" 
                                    value={new Intl.NumberFormat('fa-IR').format(displayPrice[1])} 
                                    className="form-control text-center font-14 fw-bold bg-light border-0 shadow-none py-2 rounded-3" 
                                    disabled 
                                />
                                <span className="font-12 text-muted mt-2">تومان</span>
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
                        <label className="form-check-label ms-3 font-14 cursor-pointer text-dark pt-1" htmlFor={`${prefixId}stock-available`}>محصولات موجود</label>
                    </div>
                    
                    <div className="form-check mt-3 d-flex align-items-center p-0">
                        <input 
                            className="form-check-input m-0 cursor-pointer shadow-none custom-checkbox border-secondary" 
                            type="checkbox" 
                            id={`${prefixId}has-discount`}
                            checked={hasDiscount}
                            onChange={(e) => { setHasDiscount(e.target.checked); setPage(1); }}
                        />
                        <label className="form-check-label ms-3 font-14 cursor-pointer text-dark pt-1" htmlFor={`${prefixId}has-discount`}>فقط تخفیف خورده‌ها</label>
                    </div>
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
            {categories.length > 0 && !categorySlug && (
                <section className="card-categories site-slider bg-white pt-4 pb-2 border-bottom mb-4 shadow-sm">
                    <div className="container-fluid">
                        <div className="section-title mb-2">
                            <div className="section-title-title d-flex align-items-center">
                                <h1 className="fw-900 h4 mb-0">دسته‌بندی <span className="with-highlight ms-1 text-danger">محصولات</span></h1>
                                <div className="Dottedsquare ms-2"></div>
                            </div>
                        </div>
                        <Swiper modules={[FreeMode]} freeMode={true} slidesPerView="auto" className="pro-slider py-3 px-2">
                            {categories.map(cat => (
                                <SwiperSlide key={cat.uuid} style={{ width: 'auto' }}>
                                    <Link to={`/category/${cat.slug}`} className="text-decoration-none text-dark">
                                        <div className="cat-item d-flex flex-column align-items-center mx-3 hover-lift">
                                            <div className="cat-item-image bg-light border border-ui rounded-circle d-flex align-items-center justify-content-center mb-2 shadow-sm" style={{ width: '80px', height: '80px', transition: '0.3s' }}>
                                                <img src={'/assets/image/category/kalaye-degital.png'} style={{ width: '50%', height: '50%', objectFit: 'contain' }} alt={cat.title} onError={(e)=>{e.target.src='/assets/image/category/boomi.png'}} />
                                            </div>
                                            <div className="cat-item-desc text-center">
                                                <h6 className="font-13 fw-bold">{cat.title}</h6>
                                            </div>
                                        </div>
                                    </Link>
                                </SwiperSlide>
                            ))}
                        </Swiper>
                    </div>
                </section>
            )}

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
                                        <li className="list-inline-item"><button onClick={() => { setOrdering('-base_price'); setPage(1); }} className={`btn btn-sm ${ordering === '-base_price' ? 'text-danger fw-bold border-bottom border-danger rounded-0' : 'text-muted'}`}>گران‌ترین</button></li>
                                        <li className="list-inline-item"><button onClick={() => { setOrdering('base_price'); setPage(1); }} className={`btn btn-sm ${ordering === 'base_price' ? 'text-danger fw-bold border-bottom border-danger rounded-0' : 'text-muted'}`}>ارزان‌ترین</button></li>
                                        <li className="list-inline-item"><button onClick={() => { setOrdering('-sold_count'); setPage(1); }} className={`btn btn-sm ${ordering === '-sold_count' ? 'text-danger fw-bold border-bottom border-danger rounded-0' : 'text-muted'}`}>پرفروش‌ترین</button></li>
                                        <li className="list-inline-item"><button onClick={() => { setOrdering('-view_count'); setPage(1); }} className={`btn btn-sm ${ordering === '-view_count' ? 'text-danger fw-bold border-bottom border-danger rounded-0' : 'text-muted'}`}>محبوب‌ترین</button></li>
                                        <li className="list-inline-item"><button onClick={() => { setOrdering('-created_at'); setPage(1); }} className={`btn btn-sm ${ordering === '-created_at' ? 'text-danger fw-bold border-bottom border-danger rounded-0' : 'text-muted'}`}>جدیدترین</button></li>
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
                                    <i className="bi bi-card-list me-2"></i> {pagination.count} کالا
                                </div>
                            </div>
                        </div>

                        <div className="row gy-4">
                            {loading ? (
                                <div className="col-12 text-center py-5 my-5">
                                    <div className="spinner-border text-danger" role="status" style={{width: '3rem', height: '3rem'}}></div>
                                    <p className="mt-3 fw-bold text-muted font-16">در حال جستجو...</p>
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
                                    <h4 className="text-muted fw-bold mb-3">کالایی با این مشخصات یافت نشد!</h4>
                                    <button className="btn btn-outline-danger rounded-pill px-4" onClick={clearAllFilters}>
                                        حذف همه فیلترها
                                    </button>
                                </div>
                            )}
                        </div>

                        {totalPages > 1 && (
                            <div className="my-paginate mt-5 d-flex justify-content-center">
                                <nav aria-label="Page navigation">
                                    <ul className="pagination flex-wrap justify-content-center gap-2">
                                        <li className={`page-item ${!pagination.previous ? 'disabled' : ''}`}>
                                            <button className="page-link rounded-3 border border-ui shadow-sm text-dark hover-bg-light" onClick={() => setPage(p => Math.max(1, p - 1))}>قبلی</button>
                                        </li>
                                        {[...Array(totalPages)].map((_, i) => {
                                            const pageNum = i + 1;
                                            if (pageNum === 1 || pageNum === totalPages || (pageNum >= page - 2 && pageNum <= page + 2)) {
                                                return (
                                                    <li key={i} className={`page-item ${page === pageNum ? 'active' : ''}`}>
                                                        <button className={`page-link rounded-3 border shadow-sm ${page === pageNum ? 'bg-danger border-danger text-white' : 'border-ui text-dark hover-bg-light'}`} onClick={() => setPage(pageNum)}>{pageNum}</button>
                                                    </li>
                                                );
                                            } else if (pageNum === page - 3 || pageNum === page + 3) {
                                                return <li key={i} className="page-item disabled"><span className="page-link border-0 bg-transparent text-muted">...</span></li>;
                                            }
                                            return null;
                                        })}
                                        <li className={`page-item ${!pagination.next ? 'disabled' : ''}`}>
                                            <button className="page-link rounded-3 border border-ui shadow-sm text-dark hover-bg-light" onClick={() => setPage(p => Math.min(totalPages, p + 1))}>بعدی</button>
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
                                        {categorySlug ? `خرید آنلاین محصولات دسته‌بندی` : 'فروشگاه اینترنتی آبتین'}
                                    </h6>
                                    <div className={`text-muted lh-lg text-justify font-14 ${isReadMoreOpen ? '' : 'text-truncate-3'}`} style={!isReadMoreOpen ? {maxHeight: '75px', overflow: 'hidden'} : {}}>
                                        <p>
                                            لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ، و با استفاده از طراحان گرافیک است. چاپگرها و متون بلکه روزنامه و مجله در ستون و سطرآنچنان که لازم است، و برای شرایط فعلی تکنولوژی مورد نیاز، و کاربردهای متنوع با هدف بهبود ابزارهای کاربردی می باشد.
                                        </p>
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
                .hover-lift { transition: transform 0.2s ease; }
                .hover-lift:hover { transform: translateY(-3px); }
                .cursor-pointer { cursor: pointer; }

                .custom-react-slider.noUi-target { 
                    position: relative !important;
                    background: #e9ecef !important; 
                    border-radius: 10px !important; 
                    border: none !important; 
                    height: 6px !important; 
                    box-shadow: none !important; 
                }
                .custom-react-slider .noUi-base,
                .custom-react-slider .noUi-connects {
                    position: absolute !important;
                    width: 100% !important;
                    height: 100% !important;
                    z-index: 1 !important;
                }
                .custom-react-slider .noUi-connect { 
                    position: absolute !important;
                    background: #ef4056 !important; 
                    height: 100% !important;
                    top: 0 !important;
                }
                .custom-react-slider .noUi-origin {
                    position: absolute !important;
                    height: 0 !important;
                    width: 0 !important;
                }
                .custom-react-slider .noUi-handle { 
                    position: absolute !important;
                    border: 2px solid #ef4056 !important; 
                    background: #fff !important; 
                    border-radius: 50% !important; 
                    box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important; 
                    cursor: pointer !important;
                    width: 22px !important; 
                    height: 22px !important; 
                    top: -8px !important; 
                    right: -11px !important;
                    z-index: 5 !important;
                }
                .custom-react-slider .noUi-handle::before, 
                .custom-react-slider .noUi-handle::after { 
                    display: none !important; 
                }

                .custom-checkbox { width: 18px; height: 18px; border-radius: 4px; }
                .custom-checkbox:checked { background-color: #ef4056 !important; border-color: #ef4056 !important; }

                .custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #ddd; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #ef4056; }
            `}</style>
        </main>
    );
};

export default ShopPage;