import React, { useContext, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { CompareContext } from '../context/CompareContext';
import { CartContext } from '../context/CartContext';
import { getProductDetail } from '../api/shopApi';

const ComparePage = () => {
    const { compareIds, removeFromCompare } = useContext(CompareContext);
    const { addToCart } = useContext(CartContext);
    
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(true);

    const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
    const showToast = (message, type = 'success') => {
        setToast({ show: true, message, type });
        setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 4000);
    };

    useEffect(() => {
        const fetchComparedProducts = async () => {
            if (compareIds.length === 0) {
                setProducts([]);
                setLoading(false);
                return;
            }
            setLoading(true);
            try {
                const promises = compareIds.map(id => getProductDetail(id));
                const results = await Promise.all(promises);
                setProducts(results.filter(Boolean));
            } catch (error) {
                console.error("Error fetching compared products", error);
            } finally {
                setLoading(false);
            }
        };
        fetchComparedProducts();
        window.scrollTo(0, 0);
    }, [compareIds]);

    const allAttributes = Array.from(new Set(
        products.flatMap(p => 
            p.is_variable && p.variants?.length > 0 
                ? p.variants[0].attributes.map(a => a.attribute_name) 
                : []
        )
    ));

    const handleAddToCart = async (product) => {
        const currentInventory = product.is_variable && product.variants?.length > 0 
            ? product.variants[0].inventory 
            : product.base_inventory || 0;
            
        if (currentInventory === 0) {
            return showToast("این کالا در حال حاضر ناموجود است.", "danger");
        }

        try {
            const variantId = product.is_variable && product.variants?.length > 0 ? product.variants[0].uuid : null;
            await addToCart(product.uuid, variantId, 1);
            showToast("کالا با موفقیت به سبد خرید اضافه شد.", "success");
        } catch (error) {
            if(error.response?.status !== 401) {
                showToast(error.response?.data?.error || "خطا در افزودن به سبد خرید.", "danger");
            }
        }
    };

    const emptySlots = Array.from({ length: Math.max(0, 4 - products.length) });

    if (loading) return <div className="text-center py-5 my-5 min-vh-100 d-flex align-items-center justify-content-center"><div className="spinner-border text-danger" style={{width: '4rem', height:'4rem', borderWidth:'0.3rem'}}></div></div>;

    return (
        <section className="content min-vh-100 py-4 bg-light">
            <div className={`custom-toast ${toast.show ? 'show' : ''} bg-${toast.type} shadow-lg d-flex align-items-center gap-3`}>
                <i className={`bi ${toast.type === 'success' ? 'bi-check-circle-fill' : toast.type === 'warning' ? 'bi-exclamation-triangle-fill' : 'bi-x-circle-fill'} fs-3 text-white`}></i>
                <span className="font-14 fw-bold text-white lh-base">{toast.message}</span>
            </div>

            <div className="container-fluid">
                <div className="content-box bg-white p-3 p-md-4 rounded-4 shadow-sm border border-ui mb-4">
                    <nav aria-label="breadcrumb">
                        <ol className="breadcrumb mb-0">
                            <li className="breadcrumb-item"><Link to="/" className="font-13 font-md-14 text-muted text-decoration-none hover-text-danger transition">خانه</Link></li>
                            <li className="breadcrumb-item"><Link to="/shop" className="font-13 font-md-14 text-muted text-decoration-none hover-text-danger transition">فروشگاه</Link></li>
                            <li className="breadcrumb-item active main-color-one-color font-13 font-md-14 fw-bold" aria-current="page">مقایسه محصولات</li>
                        </ol>
                    </nav>
                </div>
            </div>

            <div className="container-fluid">
                <div className="content-box bg-white rounded-4 shadow-sm border border-ui p-3 p-md-4">
                    <div className="compare-title mb-4 border-bottom border-light pb-3 d-flex align-items-center">
                        <i className="bi bi-shuffle text-danger fs-4 fs-md-3 ms-2"></i>
                        <h6 className="fw-900 text-dark fs-5 fs-md-4 m-0 pt-1">مقایسه محصولات</h6>
                    </div>

                    <div className="compare">
                        <div className="table-responsive custom-scrollbar pb-3">
                            <table className="table table-bordered fixed compare-table align-middle m-0">
                                <tbody>
                                    <tr>
                                        <td className="align-middle text-center bg-light sticky-col compare-header-col">
                                            <h6 className="fw-900 text-muted m-0 font-14 font-md-16"><i className="bi bi-box-seam me-2"></i>لیست محصولات</h6>
                                        </td>
                                        
                                        {products.map(item => {
                                            const imageUrl = item.image_url || (item.gallery && item.gallery.length > 0 ? item.gallery[0].url : '/assets/image/product/product-no-bg.png');
                                            
                                            return (
                                                <td key={item.uuid} className="compare-col">
                                                    <div className="product-box border-ui h-100 position-relative shadow-none border-0">
                                                        <div className="compare-box my-2">
                                                            <div className="compare-delete text-center">
                                                                <button onClick={() => removeFromCompare(item.uuid)} className="btn btn-danger btn-sm rounded-circle shadow-sm hover-lift d-flex align-items-center justify-content-center mx-auto" title="حذف از مقایسه" style={{width:'32px', height:'32px'}}>
                                                                    <i className="bi bi-x-lg"></i>
                                                                </button>
                                                            </div>
                                                        </div>
                                                        <Link to={`/product/${item.slug}`} className="d-block text-center mt-3 mt-md-4 text-decoration-none">
                                                            <div className="product-image d-flex justify-content-center mb-3">
                                                                <img src={imageUrl} loading="lazy" alt={item.title} className="img-fluid object-fit-contain compare-img transition hover-lift" onError={(e) => { e.target.src = '/assets/image/product/product-no-bg.png'; }} />
                                                            </div>
                                                            <h6 className="font-13 font-md-14 text-dark text-overflow-2 my-2 my-md-3 lh-lg fw-bold px-2 hover-text-danger transition">{item.title}</h6>
                                                        </Link>
                                                    </div>
                                                </td>
                                            );
                                        })}
                                        
                                        {emptySlots.map((_, i) => (
                                            <td key={`empty-img-${i}`} className="compare-col align-middle">
                                                <div className="compare-add h-100 d-flex justify-content-center align-items-center p-2 p-md-3">
                                                    <div className="compare-add-product d-flex flex-column align-items-center justify-content-center w-100 bg-light border-ui">
                                                        <div className="cap-icon mb-2 mb-md-3 bg-white rounded-circle shadow-sm d-flex align-items-center justify-content-center">
                                                            <i className="bi bi-box-arrow-in-down text-muted"></i>
                                                        </div>
                                                        <div className="cap-title mb-3 mb-md-4 px-2 text-center">
                                                            <p className="text-muted font-12 font-md-14 fw-bold m-0">برای افزودن کلیک کنید</p>
                                                        </div>
                                                        <div className="cap-btn">
                                                            <Link to="/shop" className="btn border-0 main-color-one-bg text-white rounded-pill px-3 px-md-4 py-2 font-12 font-md-14 fw-bold shadow-sm hover-lift">انتخاب کالا</Link>
                                                        </div>
                                                    </div>
                                                </div>
                                            </td>
                                        ))}
                                    </tr>

                                    <tr>
                                        <td className="fw-bold bg-light text-muted font-13 font-md-15 text-center sticky-col compare-header-col">وضعیت و قیمت</td>
                                        {products.map(item => {
                                            const currentPrice = item.is_variable && item.variants?.length > 0 ? item.variants[0].price : item.base_price;
                                            const currentInventory = item.is_variable && item.variants?.length > 0 ? item.variants[0].inventory : item.base_inventory || 0;
                                            return (
                                                <td key={`price-${item.uuid}`} className="compare-col">
                                                    <div className="d-flex flex-column align-items-center justify-content-center gap-2 gap-md-3 p-2">
                                                        <span className="d-block fw-900 text-success font-16 font-md-20">{Number(currentPrice).toLocaleString()} <span className="font-11 font-md-13 fw-normal text-muted">تومان</span></span>
                                                        {currentInventory > 0 ? (
                                                            <button onClick={() => handleAddToCart(item)} className="btn main-color-two-bg text-white shadow-sm rounded-pill font-12 font-md-13 fw-bold px-3 px-md-4 py-2 hover-lift w-100 d-flex align-items-center justify-content-center gap-2">
                                                                <i className="bi bi-cart-plus fs-6 fs-md-5"></i> افزودن به سبد
                                                            </button>
                                                        ) : (
                                                            <button className="btn btn-secondary text-white shadow-sm rounded-pill font-12 font-md-13 fw-bold px-3 px-md-4 py-2 w-100 disabled">
                                                                ناموجود
                                                            </button>
                                                        )}
                                                    </div>
                                                </td>
                                            );
                                        })}
                                        {emptySlots.map((_, i) => <td key={`empty-price-${i}`} className="compare-col"><div className="empty-cell"></div></td>)}
                                    </tr>

                                    <tr>
                                        <td colSpan={products.length < 4 ? 4 : 5} className="td-head py-3 bg-light text-end fw-bold text-dark font-14 font-md-15 border-bottom border-light shadow-sm sticky-row-title">
                                            <i className="bi bi-chevron-double-left text-danger ms-2"></i> مشخصات اصلی
                                        </td>
                                    </tr>
                                    <tr>
                                        <td className="fw-bold bg-light text-muted font-13 font-md-14 text-center sticky-col compare-header-col">برند سازنده</td>
                                        {products.map(item => <td key={`brand-${item.uuid}`} className="font-13 font-md-14 text-dark fw-bold compare-col">{item.brand ? item.brand.title : '-'}</td>)}
                                        {emptySlots.map((_, i) => <td key={`empty-brand-${i}`} className="compare-col"><div className="empty-cell"></div></td>)}
                                    </tr>
                                    <tr>
                                        <td className="fw-bold bg-light text-muted font-13 font-md-14 text-center sticky-col compare-header-col">دسته‌بندی</td>
                                        {products.map(item => <td key={`cat-${item.uuid}`} className="font-13 font-md-14 text-dark fw-bold compare-col">{item.category ? item.category.title : '-'}</td>)}
                                        {emptySlots.map((_, i) => <td key={`empty-cat-${i}`} className="compare-col"><div className="empty-cell"></div></td>)}
                                    </tr>
                                    <tr>
                                        <td className="fw-bold bg-light text-muted font-13 font-md-14 text-center sticky-col compare-header-col">وزن حدودی</td>
                                        {products.map(item => <td key={`weight-${item.uuid}`} className="font-13 font-md-14 text-dark compare-col">{item.weight ? `${item.weight} گرم` : '-'}</td>)}
                                        {emptySlots.map((_, i) => <td key={`empty-weight-${i}`} className="compare-col"><div className="empty-cell"></div></td>)}
                                    </tr>

                                    {allAttributes.length > 0 && (
                                        <tr>
                                            <td colSpan={products.length < 4 ? 4 : 5} className="td-head py-3 bg-light text-end fw-bold text-dark font-14 font-md-15 border-bottom border-light shadow-sm mt-3 sticky-row-title">
                                                <i className="bi bi-sliders2 text-danger ms-2"></i> مشخصات فنی مدل
                                            </td>
                                        </tr>
                                    )}
                                    {allAttributes.map((attrName, idx) => (
                                        <tr key={idx}>
                                            <td className="fw-bold bg-light text-muted font-13 font-md-14 text-center sticky-col compare-header-col">{attrName}</td>
                                            {products.map(item => {
                                                let attrValue = '-';
                                                if (item.is_variable && item.variants?.length > 0) {
                                                    const foundAttr = item.variants[0].attributes.find(a => a.attribute_name === attrName);
                                                    if (foundAttr) attrValue = foundAttr.value;
                                                }
                                                return <td key={`${attrName}-${item.uuid}`} className="font-13 font-md-14 text-dark compare-col">{attrValue}</td>;
                                            })}
                                            {emptySlots.map((_, i) => <td key={`empty-attr-${idx}-${i}`} className="compare-col"><div className="empty-cell"></div></td>)}
                                        </tr>
                                    ))}

                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <style jsx="true">{`
                .hover-lift { transition: transform 0.2s ease; }
                .hover-lift:hover { transform: translateY(-3px); }
                .transition { transition: all 0.2s ease-in-out; }
                .hover-text-danger:hover { color: #ef4056 !important; }
                
                .text-overflow-2 { overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
                
                .compare table { border: 1px solid #dee2e6; border-radius: 12px; overflow: hidden; border-collapse: separate; border-spacing: 0; }
                .compare table tr th, .compare table tr td { vertical-align: middle; text-align: center; border: 1px solid #dee2e6; padding: 15px; }
                
                .compare-col { min-width: 280px; max-width: 320px; vertical-align: top; }
                .compare-header-col { min-width: 180px; max-width: 200px; vertical-align: middle; }
                .compare-img { height: 180px; width: auto; }
                
                .compare-add-product { border: 2px dashed #dee2e6; min-height: 250px; background-color: #f8f9fa; border-radius: 15px; }
                .cap-icon { width: 60px; height: 60px; }
                .cap-icon i { font-size: 28px; }
                
                .sticky-col { position: sticky !important; right: 0; z-index: 5; background-color: #f8f9fa !important; border-left: 2px solid #dee2e6 !important; box-shadow: -3px 0 10px rgba(0,0,0,0.03); }
                .td-head { font-size: 16px; text-align: right !important; background-color: #f1f3f5 !important; position: sticky; right: 0; left: 0; }
                
                .compare-box { position: relative; }
                .compare-box .compare-delete { position: absolute; top: -15px; left: 50%; transform: translateX(-50%); z-index: 10;}
                
                .empty-cell { position: relative; text-align: center; height: 100%; min-height: 30px; }
                .empty-cell:after { content: ''; position: absolute; width: 30px; height: 3px; border-radius: 5px; background: #e9ecef; top: 50%; left: 50%; transform: translate(-50%, -50%); }
                
                .custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #ddd; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #ef4056; }
                
                .custom-toast { position: fixed; bottom: 30px; left: -400px; min-width: 300px; padding: 16px 24px; border-radius: 16px; z-index: 999999; transition: left 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
                .custom-toast.show { left: 30px; }

                @media (max-width: 768px) {
                    .compare-col { min-width: 190px !important; max-width: 220px !important; padding: 10px !important; }
                    .compare-header-col { min-width: 110px !important; max-width: 130px !important; padding: 10px 5px !important; }
                    .compare-img { height: 120px !important; }
                    .compare-add-product { min-height: 180px !important; padding: 15px !important; }
                    .cap-icon { width: 45px !important; height: 45px !important; margin-bottom: 10px !important;}
                    .cap-icon i { font-size: 20px !important; }
                    .custom-toast { left: 50% !important; transform: translateX(-50%); bottom: -100px; width: 90%; min-width: unset; transition: bottom 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
                    .custom-toast.show { bottom: 20px !important; left: 50% !important; }
                }
            `}</style>
        </section>
    );
};

export default ComparePage;