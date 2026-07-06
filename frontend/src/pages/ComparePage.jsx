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

    const handleAddToCart = (product) => {
        const variantId = product.is_variable && product.variants?.length > 0 ? product.variants[0].uuid : null;
        addToCart(product.uuid, variantId, 1);
    };

    const emptySlots = Array.from({ length: Math.max(0, 4 - products.length) });

    if (loading) return <div className="text-center py-5 my-5 min-vh-100 d-flex align-items-center justify-content-center"><div className="spinner-border text-danger" style={{width: '4rem', height:'4rem', borderWidth:'0.3rem'}}></div></div>;

    return (
        <section className="content min-vh-100 py-4 bg-light">
            <div className="container-fluid">
                <div className="content-box bg-white p-4 rounded-4 shadow-sm border border-ui mb-4">
                    <nav aria-label="breadcrumb">
                        <ol className="breadcrumb mb-0">
                            <li className="breadcrumb-item"><Link to="/" className="font-14 text-muted text-decoration-none hover-text-danger transition">خانه</Link></li>
                            <li className="breadcrumb-item"><Link to="/shop" className="font-14 text-muted text-decoration-none hover-text-danger transition">فروشگاه</Link></li>
                            <li className="breadcrumb-item active main-color-one-color font-14 fw-bold" aria-current="page">مقایسه محصولات</li>
                        </ol>
                    </nav>
                </div>
            </div>

            <div className="container-fluid">
                <div className="content-box bg-white rounded-4 shadow-sm border border-ui p-4">
                    <div className="compare-title mb-4 border-bottom border-light pb-3 d-flex align-items-center">
                        <i className="bi bi-arrow-left-right text-danger fs-3 ms-2"></i>
                        <h6 className="fw-900 text-dark fs-4 m-0 pt-1">مقایسه محصولات</h6>
                    </div>

                    <div className="compare">
                        <div className="table-responsive custom-scrollbar pb-3">
                            <table className="table table-bordered fixed compare-table align-middle">
                                <tbody>
                                    <tr>
                                        <td className="align-middle text-center bg-light" style={{ minWidth: '220px', maxWidth: '320px' }}>
                                            <h6 className="fw-900 text-muted m-0 fs-5"><i className="bi bi-box-seam me-2"></i> لیست محصولات</h6>
                                        </td>
                                        {products.map(item => (
                                            <td key={item.uuid} style={{ minWidth: '280px', maxWidth: '320px', verticalAlign: 'top' }}>
                                                <div className="product-box border-ui h-100 position-relative shadow-none border-0">
                                                    <div className="compare-box my-2">
                                                        <div className="compare-delete text-center">
                                                            <button onClick={() => removeFromCompare(item.uuid)} className="btn btn-danger btn-sm rounded-circle shadow-sm hover-lift" title="حذف از مقایسه" style={{width:'35px', height:'35px'}}>
                                                                <i className="bi bi-x-lg"></i>
                                                            </button>
                                                        </div>
                                                    </div>
                                                    <Link to={`/product/${item.slug}`} className="d-block text-center mt-4 text-decoration-none">
                                                        <div className="product-image d-flex justify-content-center mb-3">
                                                            <img src={item.gallery?.[0]?.url || '/assets/image/product/product-no-bg.png'} loading="lazy" alt={item.title} className="img-fluid object-fit-contain" style={{height: '180px'}} />
                                                        </div>
                                                        <h6 className="font-14 text-dark text-overflow-2 my-3 lh-lg fw-bold px-2 hover-text-danger transition">{item.title}</h6>
                                                    </Link>
                                                </div>
                                            </td>
                                        ))}
                                        
                                        {emptySlots.map((_, i) => (
                                            <td key={`empty-img-${i}`} style={{ minWidth: '280px', maxWidth: '320px', verticalAlign: 'middle' }}>
                                                <div className="compare-add h-100 d-flex justify-content-center align-items-center p-3">
                                                    <div className="compare-add-product d-flex flex-column align-items-center justify-content-center w-100" style={{border: '2px dashed #dee2e6', minHeight: '300px', backgroundColor: '#f8f9fa', borderRadius: '15px'}}>
                                                        <div className="cap-icon mb-3 bg-white p-3 rounded-circle shadow-sm">
                                                            <i className="bi bi-box-arrow-in-down text-muted fs-1"></i>
                                                        </div>
                                                        <div className="cap-title mb-4">
                                                            <p className="text-muted font-14 fw-bold">برای افزودن کلیک کنید</p>
                                                        </div>
                                                        <div className="cap-btn">
                                                            <Link to="/shop" className="btn border-0 main-color-one-bg text-white rounded-pill px-4 py-2 fw-bold shadow-sm hover-lift">انتخاب کالا</Link>
                                                        </div>
                                                    </div>
                                                </div>
                                            </td>
                                        ))}
                                    </tr>

                                    <tr>
                                        <td className="fw-bold bg-light text-muted font-15 text-center">وضعیت و قیمت</td>
                                        {products.map(item => {
                                            const currentPrice = item.is_variable && item.variants?.length > 0 ? item.variants[0].price : item.base_price;
                                            return (
                                                <td key={`price-${item.uuid}`}>
                                                    <div className="d-flex flex-column align-items-center justify-content-center gap-3">
                                                        <span className="d-block fw-900 text-success fs-5">{Number(currentPrice).toLocaleString()} <span className="font-13 fw-normal text-muted">تومان</span></span>
                                                        <button onClick={() => handleAddToCart(item)} className="btn main-color-two-bg text-white shadow-sm rounded-pill font-13 fw-bold px-4 py-2 hover-lift w-100 d-flex align-items-center justify-content-center gap-2">
                                                            <i className="bi bi-cart-plus fs-5"></i> افزودن به سبد
                                                        </button>
                                                    </div>
                                                </td>
                                            );
                                        })}
                                        {emptySlots.map((_, i) => <td key={`empty-price-${i}`}><div className="empty-cell"></div></td>)}
                                    </tr>

                                    <tr>
                                        <td colSpan={products.length < 4 ? 4 : 5} className="td-head py-3 bg-light text-end fw-bold text-dark font-15 border-bottom border-light shadow-sm">
                                            <i className="bi bi-chevron-double-left text-danger ms-2"></i> مشخصات اصلی
                                        </td>
                                    </tr>
                                    <tr>
                                        <td className="fw-bold bg-light text-muted font-14 text-center">برند سازنده</td>
                                        {products.map(item => <td key={`brand-${item.uuid}`} className="font-14 text-dark fw-bold">{item.brand ? item.brand.title : '-'}</td>)}
                                        {emptySlots.map((_, i) => <td key={`empty-brand-${i}`}><div className="empty-cell"></div></td>)}
                                    </tr>
                                    <tr>
                                        <td className="fw-bold bg-light text-muted font-14 text-center">دسته‌بندی</td>
                                        {products.map(item => <td key={`cat-${item.uuid}`} className="font-14 text-dark fw-bold">{item.category ? item.category.title : '-'}</td>)}
                                        {emptySlots.map((_, i) => <td key={`empty-cat-${i}`}><div className="empty-cell"></div></td>)}
                                    </tr>
                                    <tr>
                                        <td className="fw-bold bg-light text-muted font-14 text-center">وزن حدودی</td>
                                        {products.map(item => <td key={`weight-${item.uuid}`} className="font-14 text-dark">{item.weight ? `${item.weight} گرم` : '-'}</td>)}
                                        {emptySlots.map((_, i) => <td key={`empty-weight-${i}`}><div className="empty-cell"></div></td>)}
                                    </tr>

                                    {allAttributes.length > 0 && (
                                        <tr>
                                            <td colSpan={products.length < 4 ? 4 : 5} className="td-head py-3 bg-light text-end fw-bold text-dark font-15 border-bottom border-light shadow-sm mt-3">
                                                <i className="bi bi-sliders2 text-danger ms-2"></i> مشخصات فنی مدل
                                            </td>
                                        </tr>
                                    )}
                                    {allAttributes.map((attrName, idx) => (
                                        <tr key={idx}>
                                            <td className="fw-bold bg-light text-muted font-14 text-center">{attrName}</td>
                                            {products.map(item => {
                                                let attrValue = '-';
                                                if (item.is_variable && item.variants?.length > 0) {
                                                    const foundAttr = item.variants[0].attributes.find(a => a.attribute_name === attrName);
                                                    if (foundAttr) attrValue = foundAttr.value;
                                                }
                                                return <td key={`${attrName}-${item.uuid}`} className="font-14 text-dark">{attrValue}</td>;
                                            })}
                                            {emptySlots.map((_, i) => <td key={`empty-attr-${idx}-${i}`}><div className="empty-cell"></div></td>)}
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
                
                .compare table { border: 1px solid #dee2e6; border-radius: 10px; overflow: hidden; }
                .compare table tr th, .compare table tr td { font-size: 14px; vertical-align: middle; text-align: center; border: 1px solid #dee2e6; padding: 15px; }
                .compare table tr td:nth-child(1) { font-weight: bold; background-color: #f8f9fa; }
                
                .td-head { font-size: 16px; text-align: right !important; background-color: #f1f3f5 !important; }
                
                .compare-box { position: relative; }
                .compare-box .compare-delete { position: absolute; top: -10px; left: 50%; transform: translateX(-50%); z-index: 10;}
                
                .empty-cell { position: relative; text-align: center; height: 100%; min-height: 30px; }
                .empty-cell:after { content: ''; position: absolute; width: 30px; height: 3px; border-radius: 5px; background: #e9ecef; top: 50%; left: 50%; transform: translate(-50%, -50%); }
                
                .custom-scrollbar::-webkit-scrollbar { width: 6px; height: 6px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #ddd; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #ef4056; }
            `}</style>
        </section>
    );
};

export default ComparePage;