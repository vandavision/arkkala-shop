import React, { useState, useEffect, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Navigation, Thumbs } from 'swiper/modules';
import 'swiper/css';
import 'swiper/css/navigation';
import 'swiper/css/thumbs';

import { getProductDetail, submitComment } from '../api/shopApi';
import SeoMeta from '../components/SeoMeta';

const ProductDetailPage = () => {
    const { id } = useParams();
    const [product, setProduct] = useState(null);
    const [selectedOptions, setSelectedOptions] = useState({});
    const [thumbsSwiper, setThumbsSwiper] = useState(null);
    const [comment, setComment] = useState({ text: '', rating: 5 });

    useEffect(() => {
        const fetchProduct = async () => {
            try {
                const data = await getProductDetail(id);
                setProduct(data);
                
                // مقداردهی اولیه متغیرها (انتخاب اولین واریانت به صورت پیش‌فرض)
                if (data.is_variable && data.variants.length > 0) {
                    const initialOptions = {};
                    data.variants[0].attributes.forEach(attr => {
                        initialOptions[attr.attribute_name] = attr.value;
                    });
                    setSelectedOptions(initialOptions);
                }
            } catch (error) {
                console.error("Error fetching product:", error);
            }
        };
        fetchProduct();
    }, [id]);

    // استخراج تمام ویژگی‌های موجود از واریانت‌ها (برای ساخت دکمه‌ها)
    const availableAttributes = useMemo(() => {
        if (!product?.variants) return {};
        const attrs = {};
        product.variants.forEach(variant => {
            variant.attributes.forEach(attr => {
                if (!attrs[attr.attribute_name]) attrs[attr.attribute_name] = new Set();
                attrs[attr.attribute_name].add(attr.value);
            });
        });
        return attrs;
    }, [product]);

    // یافتن واریانت منطبق با انتخاب‌های فعلی کاربر
    const matchingVariant = useMemo(() => {
        if (!product?.variants) return null;
        return product.variants.find(variant => 
            variant.attributes.every(attr => selectedOptions[attr.attribute_name] === attr.value)
        );
    }, [product, selectedOptions]);

    const handleOptionSelect = (attrName, value) => {
        setSelectedOptions(prev => ({ ...prev, [attrName]: value }));
    };

    const handleCommentSubmit = async (e) => {
        e.preventDefault();
        try {
            await submitComment(id, { body: comment.text, rating: comment.rating });
            setComment({ text: '', rating: 5 });
            alert("دیدگاه شما با موفقیت ثبت شد.");
        } catch (error) {
            alert("خطا در ثبت دیدگاه.");
        }
    };

    if (!product) return <div className="loader">در حال بارگذاری...</div>;

    const currentPrice = matchingVariant ? matchingVariant.price : product.base_price;
    const isOutOfStock = matchingVariant ? matchingVariant.inventory === 0 : product.base_inventory === 0;

    return (
        <>
            <SeoMeta seoData={product.seo} title={product.title} price={currentPrice} />
            
            <main className="product-single-container">
                <div className="container">
                    {/* Breadcrumb */}
                    <nav className="breadcrumb-container">
                        <ol className="breadcrumb">
                            <li><a href="/">ارک کالا</a></li>
                            <li><span>/</span> {product.title}</li>
                        </ol>
                    </nav>

                    <div className="product-main-row">
                        {/* گالری تصاویر */}
                        <div className="product-gallery">
                            <Swiper
                                modules={[Navigation, Thumbs]}
                                navigation
                                thumbs={{ swiper: thumbsSwiper }}
                                className="main-swiper"
                            >
                                {product.gallery?.map((img, idx) => (
                                    <SwiperSlide key={idx}>
                                        <img src={img.url} alt={product.title} />
                                    </SwiperSlide>
                                ))}
                            </Swiper>
                        </div>

                        {/* اطلاعات محصول */}
                        <div className="product-info">
                            <h1 className="title">{product.title}</h1>
                            <h2 className="english-title">{product.english_title}</h2>
                            
                            <div className="price-section">
                                <span className="price">{Number(currentPrice).toLocaleString()} تومان</span>
                            </div>

                            {/* رندر داینامیک ویژگی‌ها (رنگ، وزن، نوع پایه و...) */}
                            {product.is_variable && Object.keys(availableAttributes).map(attrName => (
                                <div key={attrName} className="attribute-group">
                                    <h4 className="attribute-name">{attrName}:</h4>
                                    <div className="attribute-options">
                                        {[...availableAttributes[attrName]].map(value => (
                                            <button
                                                key={value}
                                                className={`option-btn ${selectedOptions[attrName] === value ? 'active' : ''}`}
                                                onClick={() => handleOptionSelect(attrName, value)}
                                            >
                                                {value}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            ))}

                            <div className="action-buttons">
                                {isOutOfStock ? (
                                    <button className="btn btn-danger disabled">ناموجود</button>
                                ) : (
                                    <button className="btn btn-primary add-to-cart">افزودن به سبد خرید</button>
                                )}
                            </div>

                            <div className="short-description" dangerouslySetInnerHTML={{ __html: product.short_description }} />
                        </div>
                    </div>

                    {/* تب‌های توضیحات و نظرات */}
                    <div className="product-tabs">
                        <div className="description-content" dangerouslySetInnerHTML={{ __html: product.description }} />
                        
                        <div className="comments-section mt-5">
                            <h3>دیدگاه‌ها</h3>
                            {product.comments?.length === 0 ? (
                                <p>هیچ دیدگاهی ثبت نشده است.</p>
                            ) : (
                                product.comments?.map(c => (
                                    <div key={c.id} className="comment-card">
                                        <strong>{c.user_name}</strong>
                                        <span className="rating">امتیاز: {c.rating} از 5</span>
                                        <p>{c.body}</p>
                                    </div>
                                ))
                            )}

                            <form className="comment-form mt-4" onSubmit={handleCommentSubmit}>
                                <h4>دیدگاه خود را بنویسید</h4>
                                <textarea 
                                    value={comment.text}
                                    onChange={(e) => setComment({ ...comment, text: e.target.value })}
                                    placeholder="نظر شما در مورد این محصول..."
                                    required
                                />
                                <button type="submit" className="btn btn-primary">ثبت دیدگاه</button>
                            </form>
                        </div>
                    </div>
                </div>
            </main>
        </>
    );
};

export default ProductDetailPage;