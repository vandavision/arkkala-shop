import React from 'react';
import { Outlet, Navigate, Link } from 'react-router-dom';
import DashboardSidebar from '../components/DashboardSidebar';
import { useAuth } from '../context/AuthContext';

const DashboardLayout = () => {
    const { user, loading } = useAuth();

    if (loading) {
        return (
            <div className="d-flex flex-column justify-content-center align-items-center min-vh-100 bg-light">
                <div className="spinner-border text-danger mb-3" style={{width: '3.5rem', height:'3.5rem', borderWidth: '0.25rem'}} role="status"></div>
                <h5 className="fw-bold text-muted font-14">در حال ورود به پنل کاربری...</h5>
            </div>
        );
    }

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    return (
        <main className="dashboard-layout bg-light min-vh-100 pb-5">
            <section className="bread-crumb py-3 mb-3 mb-lg-4 bg-white shadow-sm border-bottom border-light d-none d-lg-block">
                <div className="container-fluid container-xl">
                    <nav aria-label="breadcrumb">
                        <ol className="breadcrumb mb-0 px-2">
                            <li className="breadcrumb-item"><Link to="/" className="font-14 text-muted text-decoration-none hover-text-danger transition"><i className="bi bi-house me-1"></i>خانه</Link></li>
                            <li className="breadcrumb-item active text-danger font-14 fw-bold" aria-current="page">پنل کاربری</li>
                        </ol>
                    </nav>
                </div>
            </section>

            <section className="content pt-3 pt-lg-0">
                <div className="container-fluid container-xl">
                    <div className="row gy-3 gy-lg-4">
                        <div className="col-12 col-lg-3">
                            <DashboardSidebar />
                        </div>
                        
                        <div className="col-12 col-lg-9">
                            <div className="dashboard-content-wrapper h-100 animate-fade-in pb-4 pb-lg-0">
                                <Outlet />
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            <style jsx="true">{`
                .animate-fade-in { animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
            `}</style>
        </main>
    );
};

export default DashboardLayout;