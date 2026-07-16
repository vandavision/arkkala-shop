import React, { useRef, useEffect } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const DashboardSidebar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();
    
    const menuRef = useRef(null);

    const handleLogout = (e) => {
        e.preventDefault();
        logout();
        navigate('/login');
    };

    useEffect(() => {
        if (window.innerWidth < 992 && menuRef.current) {
            const activeEl = menuRef.current.querySelector('.active');
            if (activeEl) {
                activeEl.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
            }
        }
    }, [location.pathname]);

    const navLinkClass = ({ isActive }) => 
        `d-flex align-items-center gap-2 gap-lg-3 p-2 px-3 p-lg-3 rounded-pill rounded-lg-4 text-decoration-none transition fw-bold font-13 font-lg-14 flex-shrink-0 mb-lg-2 dashboard-nav-link ${
            isActive ? 'active' : ''
        }`;

    return (
        <aside className="profile-sidebar bg-white rounded-4 shadow-sm border border-ui sticky-top mb-1 mb-lg-0 overflow-hidden" style={{ top: '80px', zIndex: 1020 }}>
            
            <div className="profile-header d-flex align-items-center p-3 p-lg-4 border-bottom border-light">
                <div className="position-relative flex-shrink-0">
                    <img 
                        src={user?.avatar || "/assets/image/user/user.png"} 
                        alt="کاربر" 
                        className="rounded-circle object-fit-cover border border-ui shadow-sm p-1 profile-avatar bg-white" 
                        onError={(e) => { e.target.src = '/assets/image/user/user.png'; }}
                    />
                    <span className="position-absolute bottom-0 end-0 bg-success border border-white rounded-circle status-dot"></span>
                </div>
                <div className="ms-3 flex-grow-1 text-truncate">
                    <h6 className="fw-900 text-dark font-14 font-lg-16 mb-1 text-truncate">
                        {user?.first_name || user?.last_name ? `${user?.first_name || ''} ${user?.last_name || ''}` : 'کاربر مهمان'}
                    </h6>
                    <p className="text-muted font-12 font-lg-13 mb-0 text-truncate" dir="ltr">{user?.phone_number || user?.email || '---'}</p>
                </div>
                
                <div className="d-lg-none ms-2 flex-shrink-0">
                    <button onClick={handleLogout} className="btn btn-light text-danger rounded-circle p-0 shadow-sm d-flex align-items-center justify-content-center transition border border-ui" style={{width: '40px', height: '40px'}} title="خروج از حساب">
                        <i className="bi bi-box-arrow-right fs-5"></i>
                    </button>
                </div>
            </div>
            
            <div ref={menuRef} className="profile-menu p-2 p-lg-4 d-flex flex-row flex-lg-column overflow-auto custom-scrollbar gap-2 gap-lg-0 align-items-center align-items-lg-stretch hide-scroll-mobile bg-light bg-lg-white m-0">
                <NavLink to="/dashboard" end className={navLinkClass}>
                    <i className="bi bi-grid-1x2-fill fs-5"></i> 
                    <span className="d-none d-md-inline d-lg-inline">خلاصه فعالیت</span>
                    <span className="d-inline d-md-none">داشبورد</span>
                </NavLink>
                <NavLink to="/dashboard/orders" className={navLinkClass}>
                    <i className="bi bi-box-seam-fill fs-5"></i> 
                    <span className="d-none d-md-inline d-lg-inline">سفارش‌های من</span>
                    <span className="d-inline d-md-none">سفارشات</span>
                </NavLink>
                <NavLink to="/dashboard/addresses" className={navLinkClass}>
                    <i className="bi bi-geo-alt-fill fs-5"></i> 
                    <span className="d-none d-md-inline d-lg-inline">آدرس‌های من</span>
                    <span className="d-inline d-md-none">آدرس‌ها</span>
                </NavLink>
                <NavLink to="/dashboard/favorites" className={navLinkClass}>
                    <i className="bi bi-heart-fill fs-5"></i> علاقه‌مندی‌ها
                </NavLink>
                <NavLink to="/dashboard/comments" className={navLinkClass}>
                    <i className="bi bi-chat-quote-fill fs-5"></i> دیدگاه‌ها
                </NavLink>
                <NavLink to="/dashboard/profile" className={navLinkClass}>
                    <i className="bi bi-person-vcard-fill fs-5"></i> 
                    <span className="d-none d-md-inline d-lg-inline">اطلاعات کاربری</span>
                    <span className="d-inline d-md-none">پروفایل من</span>
                </NavLink>
                
                <hr className="border-light my-3 d-none d-lg-block" />
                
                <a href="#" onClick={handleLogout} className="d-none d-lg-flex align-items-center gap-3 p-3 rounded-4 text-decoration-none transition fw-bold font-14 text-danger hover-bg-danger-light mt-auto border border-transparent">
                    <i className="bi bi-box-arrow-right fs-5"></i> خروج از حساب
                </a>
            </div>

            <style jsx="true">{`
                .transition { transition: all 0.3s ease; }
                
                .dashboard-nav-link { border: 1px solid transparent; color: #6c757d; }
                .dashboard-nav-link:hover { color: #ef4056; }
                
                @media (min-width: 992px) {
                    .dashboard-nav-link { color: #212529; }
                    .dashboard-nav-link:hover { background-color: #f8f9fa; border-color: #dee2e6; }
                    .dashboard-nav-link.active { background-color: rgba(239, 64, 86, 0.1) !important; color: #ef4056 !important; border-color: rgba(239, 64, 86, 0.25) !important; }
                    .profile-avatar { width: 70px; height: 70px; }
                    .status-dot { width: 16px; height: 16px; border-width: 2px !important;}
                    .hover-bg-danger-light:hover { background-color: #ffe6e9 !important; }
                }
                
                @media (max-width: 991.98px) {
                    .dashboard-nav-link { background-color: #fff; border-color: #dee2e6; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
                    .dashboard-nav-link.active { background-color: #ef4056 !important; color: #fff !important; border-color: #ef4056 !important; box-shadow: 0 4px 8px rgba(239, 64, 86, 0.25) !important; }
                    .profile-avatar { width: 48px; height: 48px; }
                    .status-dot { width: 13px; height: 13px; border-width: 2px !important; right: 2px !important; bottom: 0px !important; }
                    
                    .hide-scroll-mobile::-webkit-scrollbar { display: none !important; }
                    .hide-scroll-mobile { -ms-overflow-style: none !important; scrollbar-width: none !important; }
                    .bg-lg-white { background-color: #f8f9fa !important; }
                }

                .custom-scrollbar::-webkit-scrollbar { height: 4px; width: 4px; }
                .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
                .custom-scrollbar::-webkit-scrollbar-thumb { background: #dee2e6; border-radius: 10px; }
                .custom-scrollbar::-webkit-scrollbar-thumb:hover { background: #ced4da; }
            `}</style>
        </aside>
    );
};

export default DashboardSidebar;