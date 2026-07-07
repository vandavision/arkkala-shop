import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getUserOrders } from '../api/cartApi';
import { getFavoritesList, getUserComments } from '../api/shopApi';

const DashboardSummary = () => {
    const { user } = useAuth();
    const [stats, setStats] = useState({ orders: 0, favorites: 0, comments: 0 });
    const [recentOrders, setRecentOrders] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = async () => {
            try {
                const [ordersData, favoritesData, commentsData] = await Promise.all([
                    getUserOrders('limit=5'), 
                    getFavoritesList(), 
                    getUserComments()
                ]);

                setStats({
                    orders: ordersData.count !== undefined ? ordersData.count : (ordersData.length || 0),
                    favorites: favoritesData.count !== undefined ? favoritesData.count : (favoritesData.length || 0),
                    comments: commentsData.count !== undefined ? commentsData.count : (commentsData.length || 0)
                });

                setRecentOrders(ordersData.results || ordersData || []);
            } catch (error) {
                console.error("Error fetching dashboard summary data:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchDashboardData();
    }, []);

    const getStatusBadge = (status) => {
        switch(status) {
            case 'pending': return <span className="badge bg-warning text-dark px-3 py-2 rounded-pill font-12 fw-bold shadow-sm">در انتظار پرداخت</span>;
            case 'processing': return <span className="badge bg-info text-dark px-3 py-2 rounded-pill font-12 fw-bold shadow-sm">در حال پردازش</span>;
            case 'shipped': return <span className="badge bg-primary text-white px-3 py-2 rounded-pill font-12 fw-bold shadow-sm">ارسال شده</span>;
            case 'delivered': return <span className="badge bg-success text-white px-3 py-2 rounded-pill font-12 fw-bold shadow-sm">تحویل شده</span>;
            case 'cancelled': return <span className="badge bg-danger text-white px-3 py-2 rounded-pill font-12 fw-bold shadow-sm">لغو شده</span>;
            default: return <span className="badge bg-secondary text-white px-3 py-2 rounded-pill font-12 fw-bold shadow-sm">{status}</span>;
        }
    };

    if (loading) {
        return (
            <div className="d-flex justify-content-center align-items-center h-100 min-vh-50">
                <div className="spinner-border text-danger" style={{width: '3rem', height:'3rem'}}></div>
            </div>
        );
    }

    return (
        <div className="dashboard-summary">
            <div className="bg-white rounded-4 shadow-sm border border-ui p-4 p-md-5 mb-4 position-relative overflow-hidden">
                <div className="position-relative z-1">
                    <h2 className="fw-900 h4 text-dark mb-2">سلام، <span className="text-danger">{user?.first_name || 'کاربر عزیز'}</span> خوش آمدید!</h2>
                    <p className="text-muted font-14 m-0">از طریق پنل کاربری خود می‌توانید سفارشات، علاقه‌مندی‌ها و مشخصات خود را مدیریت کنید.</p>
                </div>
            </div>

            <div className="row gy-4 mb-4">
                <div className="col-md-4 col-sm-6">
                    <Link to="/dashboard/orders" className="text-decoration-none">
                        <div className="bg-white rounded-4 shadow-sm border border-ui p-4 d-flex align-items-center gap-3 hover-lift transition">
                            <div className="bg-primary bg-opacity-10 text-primary rounded-circle d-flex justify-content-center align-items-center flex-shrink-0" style={{width: '60px', height: '60px'}}>
                                <i className="bi bi-box-seam fs-3"></i>
                            </div>
                            <div>
                                <h6 className="font-14 text-muted fw-bold mb-1">سفارش‌های من</h6>
                                <h4 className="fw-900 text-dark m-0">{stats.orders} <span className="font-12 fw-normal text-muted">سفارش</span></h4>
                            </div>
                        </div>
                    </Link>
                </div>
                <div className="col-md-4 col-sm-6">
                    <Link to="/dashboard/favorites" className="text-decoration-none">
                        <div className="bg-white rounded-4 shadow-sm border border-ui p-4 d-flex align-items-center gap-3 hover-lift transition">
                            <div className="bg-danger bg-opacity-10 text-danger rounded-circle d-flex justify-content-center align-items-center flex-shrink-0" style={{width: '60px', height: '60px'}}>
                                <i className="bi bi-heart fs-3"></i>
                            </div>
                            <div>
                                <h6 className="font-14 text-muted fw-bold mb-1">علاقه‌مندی‌ها</h6>
                                <h4 className="fw-900 text-dark m-0">{stats.favorites} <span className="font-12 fw-normal text-muted">کالا</span></h4>
                            </div>
                        </div>
                    </Link>
                </div>
                <div className="col-md-4 col-sm-12">
                    <Link to="/dashboard/comments" className="text-decoration-none">
                        <div className="bg-white rounded-4 shadow-sm border border-ui p-4 d-flex align-items-center gap-3 hover-lift transition">
                            <div className="bg-warning bg-opacity-10 text-warning rounded-circle d-flex justify-content-center align-items-center flex-shrink-0" style={{width: '60px', height: '60px'}}>
                                <i className="bi bi-chat-square-text fs-3"></i>
                            </div>
                            <div>
                                <h6 className="font-14 text-muted fw-bold mb-1">دیدگاه‌های من</h6>
                                <h4 className="fw-900 text-dark m-0">{stats.comments} <span className="font-12 fw-normal text-muted">دیدگاه</span></h4>
                            </div>
                        </div>
                    </Link>
                </div>
            </div>

            <div className="bg-white rounded-4 shadow-sm border border-ui p-4 p-md-5">
                <div className="d-flex align-items-center justify-content-between border-bottom border-light pb-3 mb-4">
                    <h5 className="fw-900 text-dark m-0"><i className="bi bi-clock-history text-danger me-2"></i> آخرین سفارشات شما</h5>
                    <Link to="/dashboard/orders" className="font-13 text-danger fw-bold text-decoration-none">مشاهده همه <i className="bi bi-chevron-left"></i></Link>
                </div>
                
                {recentOrders.length === 0 ? (
                    <div className="text-center py-5">
                        <i className="bi bi-cart-x text-muted opacity-25 d-block mb-3" style={{ fontSize: '4rem' }}></i>
                        <h6 className="font-14 fw-bold text-dark mb-2">شما هنوز هیچ سفارشی ثبت نکرده‌اید!</h6>
                        <p className="text-muted font-13 mb-4">برای مشاهده محصولات و ثبت سفارش به فروشگاه مراجعه کنید.</p>
                        <Link to="/shop" className="btn btn-danger rounded-pill px-4 py-2 font-13 fw-bold shadow-sm hover-lift">رفتن به فروشگاه</Link>
                    </div>
                ) : (
                    <div className="table-responsive">
                        <table className="table table-hover align-middle mb-0 text-center">
                            <thead className="table-light text-muted font-13">
                                <tr>
                                    <th className="py-3 fw-bold rounded-end-4 border-0">شماره سفارش</th>
                                    <th className="py-3 fw-bold border-0">تاریخ ثبت</th>
                                    <th className="py-3 fw-bold border-0">مبلغ کل (تومان)</th>
                                    <th className="py-3 fw-bold border-0">وضعیت</th>
                                    <th className="py-3 fw-bold rounded-start-4 border-0">جزئیات</th>
                                </tr>
                            </thead>
                            <tbody className="border-top-0">
                                {recentOrders.map(order => (
                                    <tr key={order.id} className="border-bottom border-light">
                                        <td className="py-3 font-14 fw-bold text-dark" dir="ltr">#{order.id.slice(0, 8)}</td>
                                        <td className="py-3 font-14 text-muted">{new Date(order.created_at).toLocaleDateString('fa-IR')}</td>
                                        <td className="py-3 font-14 fw-bold text-dark">{Number(order.payable_amount).toLocaleString()}</td>
                                        <td className="py-3">{getStatusBadge(order.status)}</td>
                                        <td className="py-3">
                                            <Link to={`/dashboard/orders/${order.id}`} className="btn btn-light btn-sm rounded-pill px-3 py-1 font-12 fw-bold text-danger border border-ui shadow-sm hover-lift">
                                                مشاهده
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
            <style jsx="true">{`
                .hover-lift { transition: transform 0.2s ease, box-shadow 0.2s; }
                .hover-lift:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important; }
            `}</style>
        </div>
    );
};

export default DashboardSummary;