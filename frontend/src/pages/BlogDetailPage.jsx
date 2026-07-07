import React, { useState, useEffect, useContext } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getPostDetail, getPostsList, submitPostComment } from '../api/blogApi';
import { AuthContext } from '../context/AuthContext';
import { SiteContext } from '../context/SiteContext'; 

const resolveImageUrl = (url) => {
    if (!url) return '/assets/image/blog/blog-1.jpg';
    if (typeof url !== 'string') {
        if (url.url) url = url.url;
        else return '/assets/image/blog/blog-1.jpg';
    }
    if (url.startsWith('http') || url.startsWith('data:') || url.startsWith('blob:')) return url;
    let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    baseUrl = baseUrl.replace(/\/api\/?$/, '').replace(/\/$/, '');
    let path = url.startsWith('/') ? url : `/${url}`;
    if (!path.startsWith('/media/')) path = `/media${path}`;
    return `${baseUrl}${path}`;
};

const BlogDetailPage = () => {
    const { slug } = useParams();
    const { user } = useContext(AuthContext);
    const { settings } = useContext(SiteContext); 

    const siteName = settings?.site_name || 'فروشگاه';

    const [post, setPost] = useState(null);
    const [latestPosts, setLatestPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const [commentBody, setCommentBody] = useState('');
    const [submittingComment, setSubmittingComment] = useState(false);
    const [toast, setToast] = useState({ show: false, message: '', type: 'success' });

    const showToast = (message, type = 'success') => {
        setToast({ show: true, message, type });
        setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 4000);
    };

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const postData = await getPostDetail(slug);
                setPost(postData);

                const latestData = await getPostsList('limit=3');
                setLatestPosts(latestData.results || latestData || []);
            } catch (err) {
                setError("مقاله‌ای با این آدرس یافت نشد!");
            } finally {
                setLoading(false);
            }
        };
        fetchData();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }, [slug]);

    const handleCommentSubmit = async (e) => {
        e.preventDefault();
        if (!commentBody.trim()) return showToast('لطفا متن دیدگاه را وارد کنید.', 'warning');
        
        setSubmittingComment(true);
        try {
            await submitPostComment(slug, { body: commentBody });
            showToast('دیدگاه شما با موفقیت ثبت شد و پس از تایید نمایش داده می‌شود.', 'success');
            setCommentBody('');
        } catch (err) {
            showToast('خطا در ثبت دیدگاه. لطفا مجددا تلاش کنید.', 'danger');
        } finally {
            setSubmittingComment(false);
        }
    };

    const handleShare = (network) => {
        const currentUrl = window.location.href;
        const title = encodeURIComponent(post.title);
        let shareUrl = '';
        
        switch(network) {
            case 'telegram': shareUrl = `https://t.me/share/url?url=${currentUrl}&text=${title}`; break;
            case 'whatsapp': shareUrl = `https://wa.me/?text=${title} - ${currentUrl}`; break;
            case 'twitter': shareUrl = `https://twitter.com/intent/tweet?url=${currentUrl}&text=${title}`; break;
            case 'linkedin': shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${currentUrl}`; break;
            default: navigator.clipboard.writeText(currentUrl); showToast('لینک کپی شد', 'success'); return;
        }
        window.open(shareUrl, '_blank');
    };

    if (loading) {
        return (
            <div className="d-flex flex-column justify-content-center align-items-center min-vh-100 bg-light">
                <div className="spinner-border text-danger mb-4" style={{width: '4rem', height:'4rem', borderWidth: '0.3rem'}} role="status"></div>
                <h5 className="fw-900 text-dark animate-pulse">در حال بارگذاری مقاله...</h5>
            </div>
        );
    }

    if (error || !post) {
        return (
            <div className="text-center py-5 my-5 min-vh-100 bg-light d-flex flex-column align-items-center justify-content-center">
                <i className="bi bi-file-earmark-x fs-1 text-danger mb-3" style={{fontSize: '4rem'}}></i>
                <h3 className="fw-900 text-dark mb-4">{error}</h3>
                <Link to="/blog" className="btn btn-danger rounded-pill px-5 py-3 shadow-sm hover-lift fw-bold">بازگشت به مجله {siteName}</Link>
            </div>
        );
    }

    return (
        <main className="blog-detail-page bg-light min-vh-100 pb-5">
            <div className={`custom-toast ${toast.show ? 'show' : ''} bg-${toast.type} shadow-lg d-flex align-items-center gap-3`}>
                <i className={`bi ${toast.type === 'success' ? 'bi-check-circle-fill' : toast.type === 'warning' ? 'bi-exclamation-triangle-fill' : 'bi-x-circle-fill'} fs-3 text-white`}></i>
                <span className="font-14 fw-bold text-white lh-base">{toast.message}</span>
            </div>

            <section className="bread-crumb py-3 bg-white shadow-sm border-bottom border-light mb-4">
                <div className="container-fluid container-xl">
                    <nav aria-label="breadcrumb">
                        <ol className="breadcrumb mb-0 px-2">
                            <li className="breadcrumb-item"><Link to="/" className="font-13 text-muted text-decoration-none hover-text-danger transition"><i className="bi bi-house me-1"></i>خانه</Link></li>
                            <li className="breadcrumb-item"><Link to="/blog" className="font-13 text-muted text-decoration-none hover-text-danger transition">مجله {siteName}</Link></li>
                            {post.category && (
                                <li className="breadcrumb-item"><Link to={`/blog?category__slug=${post.category.slug}`} className="font-13 text-muted text-decoration-none hover-text-danger transition">{post.category.title}</Link></li>
                            )}
                            <li className="breadcrumb-item active text-danger font-13 fw-bold text-truncate" aria-current="page" style={{maxWidth: '200px'}}>{post.title}</li>
                        </ol>
                    </nav>
                </div>
            </section>

            <div className="container-fluid container-xl">
                <div className="row gy-4">
                    <div className="col-lg-8 col-xl-9 order-1">
                        
                        <div className="bg-white rounded-4 shadow-sm border border-ui p-4 p-md-5 mb-4 animate-fade-in">
                            <h1 className="fw-900 h3 text-dark mb-4 lh-base title-line-bottom pb-3">{post.title}</h1>
                            
                            <div className="row gy-3 justify-content-start align-items-center mb-4">
                                {post.category && (
                                    <div className="col-auto">
                                        <div className="d-flex align-items-center gap-2 bg-light px-3 py-2 rounded-pill border border-light">
                                            <i className="bi bi-stack text-danger fs-5"></i>
                                            <span className="font-13 text-muted">دسته بندی:</span>
                                            <Link to={`/blog?category__slug=${post.category.slug}`} className="badge bg-danger font-13 fw-normal text-decoration-none">{post.category.title}</Link>
                                        </div>
                                    </div>
                                )}
                                <div className="col-auto">
                                    <div className="d-flex align-items-center gap-2 bg-light px-3 py-2 rounded-pill border border-light">
                                        <i className="bi bi-clock text-primary fs-5"></i>
                                        <span className="font-13 text-muted">زمان مطالعه:</span>
                                        <span className="font-13 fw-bold text-dark">{post.read_time || '۵'} دقیقه</span>
                                    </div>
                                </div>
                                <div className="col-auto">
                                    <div className="d-flex align-items-center gap-2 bg-light px-3 py-2 rounded-pill border border-light">
                                        <i className="bi bi-calendar-check text-success fs-5"></i>
                                        <span className="font-13 text-muted">تاریخ انتشار:</span>
                                        <span className="font-13 fw-bold text-dark">{new Date(post.created_at).toLocaleDateString('fa-IR')}</span>
                                    </div>
                                </div>
                                <div className="col-auto">
                                    <div className="d-flex align-items-center gap-2 bg-light px-3 py-2 rounded-pill border border-light">
                                        <i className="bi bi-chat-text text-warning fs-5"></i>
                                        <span className="font-13 text-muted">نظرات:</span>
                                        <span className="font-13 fw-bold text-dark">{post.comments?.length || 0} نظر</span>
                                    </div>
                                </div>
                            </div>

                            <div className="text-center mb-5">
                                <img 
                                    src={resolveImageUrl(post.image)} 
                                    className="img-fluid rounded-4 shadow-sm w-100 object-fit-cover" 
                                    style={{maxHeight: '450px'}} 
                                    alt={post.title} 
                                    onError={(e) => { e.target.onerror = null; e.target.src = '/assets/image/blog/blog-1.jpg'; }}
                                />
                            </div>

                            <div className="blog-content-body font-15 text-dark lh-lg text-justify" dangerouslySetInnerHTML={{ __html: post.body || post.content || post.description || '<p>محتوایی برای این مقاله ثبت نشده است.</p>' }}></div>
                        </div>

                        <div className="bg-white rounded-4 shadow-sm border border-ui p-4 p-md-5 mt-4" id="comments">
                            <h4 className="fw-900 text-dark mb-4 border-bottom border-light pb-3 d-flex align-items-center gap-2">
                                <i className="bi bi-chat-dots text-danger"></i> نظرات کاربران ({post.comments?.length || 0})
                            </h4>

                            {post.comments && post.comments.length > 0 ? (
                                <div className="comments-list d-flex flex-column gap-3 mb-5">
                                    {post.comments.map(comment => (
                                        <div key={comment.uuid || comment.id} className="comment-box bg-light border border-ui rounded-4 p-3 p-md-4 shadow-sm">
                                            <div className="d-flex justify-content-between align-items-start mb-3">
                                                <div className="d-flex align-items-center gap-3">
                                                    <div className="bg-white rounded-circle shadow-sm border border-light d-flex align-items-center justify-content-center" style={{width: '50px', height: '50px'}}>
                                                        <i className="bi bi-person text-secondary fs-3"></i>
                                                    </div>
                                                    <div>
                                                        <h6 className="font-14 fw-bold text-dark mb-1">{comment.user_name || 'کاربر مهمان'}</h6>
                                                        <span className="font-11 text-muted px-2 py-1 bg-white rounded-pill border border-light">{new Date(comment.created_at).toLocaleDateString('fa-IR')}</span>
                                                    </div>
                                                </div>
                                            </div>
                                            <p className="font-14 text-dark lh-lg text-justify m-0 ps-md-5 ms-md-4">{comment.body}</p>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-5 bg-light border border-light rounded-4 mb-5">
                                    <i className="bi bi-chat-square-text fs-1 text-muted opacity-25 d-block mb-3"></i>
                                    <h6 className="font-14 fw-bold text-dark mb-1">هنوز هیچ دیدگاهی ثبت نشده است.</h6>
                                    <p className="font-13 text-muted">اولین نفری باشید که برای این مطلب دیدگاه می‌نویسد!</p>
                                </div>
                            )}

                            <div className="comment-form bg-danger bg-opacity-10 border border-danger border-opacity-25 rounded-4 p-4 p-md-5">
                                <h5 className="fw-900 text-dark mb-3"><i className="bi bi-pencil-square text-danger me-2"></i> دیدگاه خود را بنویسید</h5>
                                <p className="font-13 text-muted mb-4">نشانی ایمیل شما منتشر نخواهد شد. بخش‌های موردنیاز با علامت * مشخص شده‌اند.</p>
                                
                                <form onSubmit={handleCommentSubmit}>
                                    <div className="row gy-3">
                                        {!user && (
                                            <div className="col-12 mb-2">
                                                <div className="alert bg-white border border-ui rounded-3 d-flex align-items-center gap-3">
                                                    <i className="bi bi-info-circle-fill text-primary fs-4"></i>
                                                    <span className="font-13 text-dark">شما به عنوان <strong>کاربر مهمان</strong> در حال ثبت نظر هستید. برای نمایش نام کاربری خود <Link to="/login" className="text-danger fw-bold text-decoration-none">وارد شوید</Link>.</span>
                                                </div>
                                            </div>
                                        )}
                                        <div className="col-12">
                                            <label className="font-14 fw-bold mb-2 text-dark">متن دیدگاه <span className="text-danger">*</span></label>
                                            <textarea 
                                                rows="5" 
                                                className="form-control border-0 shadow-sm py-3 px-4 rounded-4 font-14 focus-danger" 
                                                placeholder="تجربه یا نظر خود را درباره این مطلب بنویسید..." 
                                                value={commentBody}
                                                onChange={(e) => setCommentBody(e.target.value)}
                                                required
                                            ></textarea>
                                        </div>
                                        <div className="col-12 text-end mt-4">
                                            <button type="submit" disabled={submittingComment} className="btn btn-danger px-5 py-3 rounded-pill fw-bold font-14 shadow-sm hover-lift w-100 w-md-auto">
                                                {submittingComment ? <div className="spinner-border spinner-border-sm text-white"></div> : <><i className="bi bi-send-fill me-2"></i> ثبت دیدگاه</>}
                                            </button>
                                        </div>
                                    </div>
                                </form>
                            </div>
                        </div>
                    </div>

                    <div className="col-lg-4 col-xl-3 order-2">
                        <div className="position-sticky" style={{top: '100px'}}>
                            
                            <div className="bg-white rounded-4 shadow-sm border border-ui p-4 text-center mb-4 hover-shadow transition">
                                <div className="position-relative d-inline-block mb-3">
                                    <img src="/assets/image/user/user.jpg" className="rounded-circle border border-3 border-danger p-1 object-fit-cover" style={{width: '90px', height: '90px'}} alt="نویسنده" onError={(e)=>{e.target.src='/assets/image/user/user.png'}} />
                                    <span className="position-absolute bottom-0 end-0 bg-success border border-white border-2 rounded-circle" style={{width: '20px', height: '20px'}}></span>
                                </div>
                                <h5 className="fw-bold text-dark mb-1 font-16">{post.author?.first_name ? `${post.author.first_name} ${post.author.last_name}` : `تیم تحریریه ${siteName}`}</h5>
                                <p className="font-12 text-muted mb-4 bg-light rounded-pill px-3 py-1 d-inline-block">نویسنده و محقق</p>
                                
                                <div className="d-flex align-items-center justify-content-center gap-3 pt-3 border-top border-light">
                                    <button onClick={() => handleShare('telegram')} className="btn btn-light rounded-circle text-primary hover-lift p-0 d-flex align-items-center justify-content-center shadow-sm" style={{width:'38px',height:'38px'}} title="تلگرام"><i className="bi bi-telegram fs-5"></i></button>
                                    <button onClick={() => handleShare('whatsapp')} className="btn btn-light rounded-circle text-success hover-lift p-0 d-flex align-items-center justify-content-center shadow-sm" style={{width:'38px',height:'38px'}} title="واتس‌اپ"><i className="bi bi-whatsapp fs-5"></i></button>
                                    <button onClick={() => handleShare('twitter')} className="btn btn-light rounded-circle text-info hover-lift p-0 d-flex align-items-center justify-content-center shadow-sm" style={{width:'38px',height:'38px'}} title="توییتر"><i className="bi bi-twitter fs-5"></i></button>
                                    <button onClick={() => handleShare('copy')} className="btn btn-light rounded-circle text-secondary hover-lift p-0 d-flex align-items-center justify-content-center shadow-sm" style={{width:'38px',height:'38px'}} title="کپی لینک"><i className="bi bi-link-45deg fs-5"></i></button>
                                </div>
                            </div>

                            {latestPosts.length > 0 && (
                                <div className="bg-white rounded-4 shadow-sm border border-ui p-4 mb-4">
                                    <h6 className="fw-900 text-dark mb-4 border-bottom border-danger border-2 pb-2 d-inline-block">مطالب پیشنهادی</h6>
                                    <div className="d-flex flex-column gap-3">
                                        {latestPosts.map(p => (
                                            <Link to={`/blog/${p.slug}`} key={p.uuid} className="d-flex align-items-center gap-3 text-decoration-none hover-bg-light p-2 rounded-3 transition">
                                                <img src={resolveImageUrl(p.image)} className="rounded-3 object-fit-cover shadow-sm" style={{width: '70px', height: '70px'}} alt={p.title} onError={(e)=>{e.target.src='/assets/image/blog/blog-1.jpg'}} />
                                                <div>
                                                    <h6 className="font-13 fw-bold text-dark text-overflow-2 m-0 lh-base hover-text-danger transition">{p.title}</h6>
                                                    <span className="font-11 text-muted d-block mt-2"><i className="bi bi-clock me-1"></i>{new Date(p.created_at).toLocaleDateString('fa-IR')}</span>
                                                </div>
                                            </Link>
                                        ))}
                                    </div>
                                </div>
                            )}
                            
                        </div>
                    </div>
                </div>
            </div>

            <style jsx="true">{`
                .animate-pulse { animation: pulse 2s infinite; }
                @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
                
                .animate-fade-in { animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1); }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

                .transition { transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1); }
                .hover-lift { transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), box-shadow 0.3s; }
                .hover-lift:hover { transform: translateY(-5px); box-shadow: 0 10px 25px rgba(0,0,0,0.08) !important; }
                .hover-shadow:hover { box-shadow: 0 15px 35px rgba(0,0,0,0.08) !important; }
                
                .hover-text-danger:hover { color: #ef4056 !important; }
                .hover-bg-light:hover { background-color: #f8f9fa !important; }

                .text-overflow-1 { overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical; }
                .text-overflow-2 { overflow: hidden; text-overflow: ellipsis; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }

                .title-line-bottom { position: relative; }
                .title-line-bottom::after { content: ''; position: absolute; bottom: 0; right: 0; width: 60px; height: 3px; background-color: #ef4056; border-radius: 5px; }

                .blog-content-body img { max-width: 100%; height: auto; border-radius: 12px; margin: 20px 0; box-shadow: 0 5px 15px rgba(0,0,0,0.05); display: block; margin-left: auto; margin-right: auto;}
                .blog-content-body h2, .blog-content-body h3, .blog-content-body h4 { font-weight: 900; color: #212529; margin-top: 30px; margin-bottom: 15px; }
                .blog-content-body p { margin-bottom: 20px; font-size: 15px; line-height: 2.2; }
                .blog-content-body ul { padding-right: 20px; margin-bottom: 20px; }
                .blog-content-body li { margin-bottom: 10px; }
                .blog-content-body a { color: #ef4056; text-decoration: none; font-weight: bold; }
                .blog-content-body a:hover { text-decoration: underline; }

                .focus-danger:focus { background-color: #fff !important; box-shadow: 0 0 0 4px rgba(239, 64, 86, 0.1) !important; border: 1px solid #ef4056 !important; outline: none; }

                .custom-toast { position: fixed; bottom: 30px; left: -400px; min-width: 300px; padding: 16px 24px; border-radius: 16px; z-index: 999999; transition: left 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
                .custom-toast.show { left: 30px; }
                @media (max-width: 768px) {
                    .custom-toast { left: 50% !important; transform: translateX(-50%); bottom: -100px; width: 90%; min-width: unset; transition: bottom 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
                    .custom-toast.show { bottom: 20px !important; left: 50% !important; }
                }
            `}</style>
        </main>
    );
};

export default BlogDetailPage;