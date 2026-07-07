import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getUserComments } from '../api/shopApi';

const UserComments = () => {
    const [comments, setComments] = useState([]); 
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchComments = async () => {
            try {
                const data = await getUserComments();
                setComments(data.results || data || []);
            } catch (error) {
                console.error("Error fetching user comments:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchComments();
    }, []);

    const getStatusBadge = (status) => {
        if (status === true) return <span className="badge bg-success bg-opacity-10 text-success border border-success border-opacity-25 px-2 py-1 font-11 rounded-pill"><i className="bi bi-check-circle-fill me-1"></i> تایید شده</span>;
        if (status === false) return <span className="badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25 px-2 py-1 font-11 rounded-pill"><i className="bi bi-x-circle-fill me-1"></i> رد شده</span>;
        return <span className="badge bg-warning bg-opacity-10 text-warning border border-warning border-opacity-25 px-2 py-1 font-11 rounded-pill"><i className="bi bi-clock-history me-1"></i> در انتظار تایید</span>;
    };

    if (loading) {
        return (
            <div className="text-center py-5 d-flex flex-column align-items-center justify-content-center bg-white rounded-4 shadow-sm border border-ui" style={{ minHeight: '400px' }}>
                <div className="spinner-border text-danger mb-3" style={{width: '3rem', height:'3rem'}}></div>
                <h6 className="font-14 fw-bold text-muted">در حال دریافت دیدگاه‌ها...</h6>
            </div>
        );
    }

    return (
        <div className="user-comments">
            <div className="bg-white p-3 p-md-4 rounded-4 border border-ui shadow-sm mb-4 d-flex align-items-center gap-3">
                <div className="bg-warning bg-opacity-10 p-2 rounded-circle d-flex align-items-center justify-content-center">
                    <i className="bi bi-chat-quote-fill text-warning fs-3"></i>
                </div>
                <h2 className="fw-900 h5 m-0 text-dark">نظرات <span className="text-danger">و دیدگاه‌ها</span></h2>
            </div>

            <div className="bg-white rounded-4 shadow-sm border border-ui p-4 min-vh-50">
                {comments.length === 0 ? (
                    <div className="text-center py-5 my-3 bg-light border border-light rounded-4">
                        <i className="bi bi-chat-square-text text-muted opacity-25 d-block mb-3" style={{ fontSize: '5rem' }}></i>
                        <h5 className="fw-bold text-dark mb-2 font-16">شما هنوز هیچ دیدگاهی ثبت نکرده‌اید!</h5>
                        <p className="text-muted font-13 mb-4">نظرات و تجربیات شما راهنمای خوبی برای سایر خریداران خواهد بود.</p>
                        <Link to="/shop" className="btn btn-outline-danger rounded-pill px-4 py-2 font-13 fw-bold shadow-sm hover-lift">ثبت نظر برای کالاها</Link>
                    </div>
                ) : (
                    <div className="d-flex flex-column gap-3">
                        {comments.map(comment => (
                            <div className="comment-card bg-light border border-ui rounded-4 p-3 p-md-4 shadow-sm hover-shadow transition" key={comment.id}>
                                <div className="d-flex flex-column flex-md-row align-items-start gap-4">
                                    
                                    {comment.product_slug && (
                                        <div className="product-info-sm text-center flex-shrink-0" style={{width: '120px'}}>
                                            <Link to={`/product/${comment.product_slug}`} className="d-block text-decoration-none">
                                                <div className="bg-white border border-light rounded-3 p-2 shadow-sm mb-2 hover-lift transition h-100 d-flex align-items-center justify-content-center">
                                                    <img src={comment.product_image || '/assets/image/product/product-no-bg.png'} alt={comment.product_title} className="img-fluid object-fit-contain w-100" style={{height:'90px'}} />
                                                </div>
                                                <span className="font-11 text-muted text-overflow-2 lh-base fw-bold">{comment.product_title}</span>
                                            </Link>
                                        </div>
                                    )}

                                    <div className="flex-grow-1 w-100">
                                        <div className="d-flex align-items-center justify-content-between mb-3 border-bottom border-light pb-3 flex-wrap gap-2">
                                            <div className="d-flex align-items-center gap-3">
                                                {getStatusBadge(comment.is_approved)}
                                                <span className="font-12 text-muted"><i className="bi bi-calendar2-week me-1"></i> {new Date(comment.created_at).toLocaleDateString('fa-IR')}</span>
                                            </div>
                                            <div className="rating-stars text-warning font-14 bg-warning bg-opacity-10 px-2 py-1 rounded-pill">
                                                {Array.from({ length: 5 }).map((_, i) => (
                                                    <i key={i} className={i < (comment.rating || 5) ? "bi bi-star-fill me-1" : "bi bi-star text-muted opacity-25 me-1"}></i>
                                                ))}
                                            </div>
                                        </div>
                                        <div className="comment-body">
                                            <p className="font-14 text-dark lh-lg text-justify m-0" dangerouslySetInnerHTML={{__html: comment.body?.replace(/\n/g, '<br/>')}}></p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
            <style jsx="true">{`
                .hover-lift { transition: transform 0.2s ease, box-shadow 0.2s; }
                .hover-lift:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.08) !important; }
                .hover-shadow:hover { box-shadow: 0 10px 25px rgba(0,0,0,0.06) !important; background-color: #fff !important; border-color: #dee2e6 !important;}
                .transition { transition: all 0.3s ease; }
                .text-overflow-2 { overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
            `}</style>
        </div>
    );
};

export default UserComments;