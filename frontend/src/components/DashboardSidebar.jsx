import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const DashboardSidebar = () => {
    const { user, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = (e) => {
        e.preventDefault();
        logout();
        navigate('/login');
    };

    const navLinkClass = ({ isActive }) => 
        `d-flex align-items-center gap-3 p-3 rounded-4 text-decoration-none transition fw-bold font-14 mb-2 ${
            isActive 
            ? 'bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25 shadow-sm' 
            : 'text-dark hover-bg-light border border-transparent'
        }`;

    return (
        <aside className="profile-sidebar bg-white rounded-4 shadow-sm border border-ui p-4 sticky-top" style={{ top: '100px' }}>
            <div className="profile-header d-flex align-items-center border-bottom border-light pb-4 mb-4">
                <div className="position-relative">
                    <img 
                        src={user?.avatar || "/assets/image/user/user.png"} 
                        alt="کاربر" 
                        className="rounded-circle object-fit-cover border border-ui shadow-sm p-1" 
                        width="70" 
                        height="70" 
                        onError={(e) => { e.target.src = '/assets/image/user/user.png'; }}
                    />
                    <span className="position-absolute bottom-0 end-0 bg-success border border-white border-2 rounded-circle" style={{ width: '16px', height: '16px' }}></span>
                </div>
                <div className="ms-3 flex-grow-1 text-truncate">
                    <h6 className="mt-2 fw-900 text-dark font-16 mb-1 text-truncate">
                        {user?.first_name || user?.last_name ? `${user?.first_name || ''} ${user?.last_name || ''}` : 'کاربر مهمان'}
                    </h6>
                    <p className="text-muted font-13 mb-0 text-truncate" dir="ltr">{user?.phone_number || user?.email || '---'}</p>
                </div>
            </div>
            
            <div className="profile-menu d-flex flex-column">
                <NavLink to="/dashboard" end className={navLinkClass}>
                    <i className="bi bi-grid-1x2-fill fs-5"></i> خلاصه فعالیت
                </NavLink>
                <NavLink to="/dashboard/orders" className={navLinkClass}>
                    <i className="bi bi-box-seam-fill fs-5"></i> سفارش‌های من
                </NavLink>
                <NavLink to="/dashboard/favorites" className={navLinkClass}>
                    <i className="bi bi-heart-fill fs-5"></i> لیست علاقه‌مندی‌ها
                </NavLink>
                <NavLink to="/dashboard/comments" className={navLinkClass}>
                    <i className="bi bi-chat-quote-fill fs-5"></i> نظرات و دیدگاه‌ها
                </NavLink>
                <NavLink to="/dashboard/profile" className={navLinkClass}>
                    <i className="bi bi-person-vcard-fill fs-5"></i> اطلاعات حساب کاربری
                </NavLink>
                
                <hr className="border-light my-3" />
                
                <a href="#" onClick={handleLogout} className="d-flex align-items-center gap-3 p-3 rounded-4 text-decoration-none transition fw-bold font-14 text-danger hover-bg-danger-light">
                    <i className="bi bi-box-arrow-right fs-5"></i> خروج از حساب
                </a>
            </div>

            <style jsx="true">{`
                .hover-bg-light:hover { background-color: #f8f9fa !important; border-color: #dee2e6 !important; }
                .hover-bg-danger-light:hover { background-color: #ffe6e9 !important; }
                .border-transparent { border-color: transparent !important; }
            `}</style>
        </aside>
    );
};

export default DashboardSidebar;