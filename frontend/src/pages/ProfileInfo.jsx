import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { updateUserProfile } from '../api/authApi';

const resolveImageUrl = (url) => {
    if (!url) return "/assets/image/user/user.png";
    if (url.startsWith('http') || url.startsWith('data:')) return url;
    let baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    baseUrl = baseUrl.replace(/\/api\/?$/, '');
    return `${baseUrl}${url.startsWith('/') ? '' : '/'}${url}`;
};

const ProfileInfo = () => {
    const { user, fetchProfile } = useAuth();
    
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        email: '',
        phone_number: '',
    });

    const [avatarFile, setAvatarFile] = useState(null);
    const [avatarPreview, setAvatarPreview] = useState(null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
    const showToast = (message, type = 'success') => {
        setToast({ show: true, message, type });
        setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 4000);
    };

    useEffect(() => {
        if (user) {
            setFormData({
                first_name: user.first_name || '',
                last_name: user.last_name || '',
                email: user.email || '',
                phone_number: user.phone_number || '',
            });
            setAvatarPreview(user.avatar ? resolveImageUrl(user.avatar) : "/assets/image/user/user.png");
        }
    }, [user]);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            setAvatarFile(file);
            const reader = new FileReader();
            reader.onloadend = () => {
                setAvatarPreview(reader.result);
            };
            reader.readAsDataURL(file);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        try {
            const submitData = new FormData();
            submitData.append('first_name', formData.first_name);
            submitData.append('last_name', formData.last_name);
            
            if (formData.email) submitData.append('email', formData.email);
            if (formData.phone_number) submitData.append('phone_number', formData.phone_number);
            
            if (avatarFile) {
                submitData.append('avatar', avatarFile);
            }

            await updateUserProfile(submitData);
            await fetchProfile();
            
            showToast('بروزرسانی اطلاعات با موفقیت انجام شد.', 'success');
            
            const modalCloseBtn = document.querySelector('#editModalCloseBtn');
            if(modalCloseBtn) modalCloseBtn.click();
            
        } catch (error) {
            console.error("Profile update error", error.response?.data);
            
            let errorMsg = 'خطا در بروزرسانی اطلاعات.';
            if (error.response?.data) {
                const data = error.response.data;
                if (data.email) errorMsg = data.email[0];
                else if (data.phone_number) errorMsg = data.phone_number[0];
                else if (data.avatar) errorMsg = data.avatar[0];
                else if (typeof data === 'string') errorMsg = data;
            }
            showToast(errorMsg, 'danger');
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <div className="profile-info">
            <div className={`custom-toast ${toast.show ? 'show' : ''} bg-${toast.type} shadow-lg d-flex align-items-center gap-3`}>
                <i className={`bi ${toast.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill'} fs-3 text-white`}></i>
                <span className="font-14 fw-bold text-white lh-base">{toast.message}</span>
            </div>

            <div className="d-flex flex-wrap align-items-center justify-content-between mb-4 bg-white p-3 p-md-4 rounded-4 border border-ui shadow-sm">
                <div className="section-title-title">
                    <h2 className="fw-900 h5 m-0 text-dark d-flex align-items-center gap-2">
                        <i className="bi bi-person-vcard-fill text-danger fs-3"></i> اطلاعات <span className="text-danger">حساب کاربری</span>
                    </h2>
                </div>
                <button data-bs-toggle="modal" data-bs-target="#editModal" className="btn btn-outline-danger rounded-pill px-4 py-2 font-13 fw-bold shadow-sm hover-lift d-flex align-items-center gap-2 mt-3 mt-sm-0">
                    <i className="bi bi-pencil-square"></i> ویرایش پروفایل
                </button>
            </div>

            <div className="card shadow-sm border-ui rounded-4 overflow-hidden">
                <div className="card-body p-0">
                    <div className="table-responsive">
                        <table className="table table-borderless mb-0 align-middle">
                            <tbody>
                                <tr className="border-bottom border-light">
                                    <td className="p-4 border-end border-light w-50 hover-bg-light transition">
                                        <h6 className="fw-bold font-13 text-muted mb-2"><i className="bi bi-person me-1"></i> نام و نام خانوادگی:</h6>
                                        <p className="font-15 fw-bold text-dark mb-0 ms-4">{user?.first_name || user?.last_name ? `${user?.first_name} ${user?.last_name}` : 'ثبت نشده'}</p>
                                    </td>
                                    <td className="p-4 w-50 hover-bg-light transition">
                                        <h6 className="text-muted fw-bold font-13 mb-2"><i className="bi bi-phone me-1"></i> شماره موبایل:</h6>
                                        <p className="font-15 fw-bold text-dark mb-0 ms-4" dir="ltr">{user?.phone_number || 'ثبت نشده'}</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td className="p-4 border-end border-light w-50 hover-bg-light transition">
                                        <h6 className="fw-bold font-13 text-muted mb-2"><i className="bi bi-envelope me-1"></i> پست الکترونیک:</h6>
                                        <p className="font-15 fw-bold text-dark mb-0 ms-4 text-truncate">{user?.email || 'ثبت نشده'}</p>
                                    </td>
                                    <td className="p-4 w-50 hover-bg-light transition">
                                        <h6 className="fw-bold font-13 text-muted mb-2"><i className="bi bi-calendar2-week me-1"></i> تاریخ عضویت:</h6>
                                        <p className="font-15 fw-bold text-dark mb-0 ms-4">
                                            {user?.date_joined ? new Date(user.date_joined).toLocaleDateString('fa-IR') : '---'}
                                        </p>
                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div className="modal fade" id="editModal" tabIndex="-1" aria-labelledby="editModalLabel" aria-hidden="true">
                <div className="modal-dialog modal-dialog-centered modal-lg">
                    <div className="modal-content border-0 rounded-4 shadow-lg overflow-hidden">
                        <div className="modal-header bg-light border-bottom border-ui px-4 py-3">
                            <h5 className="modal-title fw-900 font-16 text-dark d-flex align-items-center gap-2" id="editModalLabel">
                                <i className="bi bi-pencil-square text-danger fs-4"></i> ویرایش اطلاعات
                            </h5>
                            <button type="button" className="btn-close shadow-none" data-bs-dismiss="modal" aria-label="Close" id="editModalCloseBtn"></button>
                        </div>
                        <div className="modal-body p-4 p-md-5">
                            
                            <div className="d-flex align-items-center justify-content-center mb-4 pb-4 border-bottom border-light">
                                <div className="position-relative">
                                    <img 
                                        src={avatarPreview || "/assets/image/user/user.png"} 
                                        alt="آواتار شما" 
                                        className="rounded-circle object-fit-cover border border-ui shadow-sm p-1" 
                                        width="90" 
                                        height="90" 
                                        onError={(e) => { e.target.src = '/assets/image/user/user.png'; }}
                                    />
                                    <label htmlFor="uploadAvatar" className="position-absolute bottom-0 end-0 bg-danger text-white rounded-circle d-flex align-items-center justify-content-center shadow cursor-pointer hover-lift" style={{width:'32px', height:'32px'}}>
                                        <i className="bi bi-camera-fill font-14"></i>
                                    </label>
                                    <input type="file" id="uploadAvatar" className="d-none" accept="image/*" onChange={handleFileChange} />
                                </div>
                            </div>

                            <form onSubmit={handleSubmit}>
                                <div className="row g-4">
                                    <div className="col-md-6">
                                        <label className="form-label font-13 fw-bold text-dark">نام</label>
                                        <input type="text" className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-14 focus-danger" name="first_name" placeholder="نام خود را وارد کنید" value={formData.first_name} onChange={handleChange} />
                                    </div>
                                    <div className="col-md-6">
                                        <label className="form-label font-13 fw-bold text-dark">نام خانوادگی</label>
                                        <input type="text" className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-14 focus-danger" name="last_name" placeholder="نام خانوادگی خود را وارد کنید" value={formData.last_name} onChange={handleChange} />
                                    </div>
                                    <div className="col-md-6">
                                        <label className="form-label font-13 fw-bold text-dark">آدرس ایمیل</label>
                                        <input type="email" className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-14 focus-danger text-start" name="email" placeholder="email@domain.com" value={formData.email} onChange={handleChange} dir="ltr" />
                                    </div>
                                    <div className="col-md-6">
                                        <label className="form-label font-13 fw-bold text-dark">شماره موبایل</label>
                                        <input type="text" className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-14 focus-danger text-start" name="phone_number" placeholder="09123456789" value={formData.phone_number} onChange={handleChange} dir="ltr" />
                                    </div>
                                    <div className="col-12 mt-5 text-end">
                                        <button type="button" className="btn btn-light px-4 py-2 rounded-pill fw-bold font-13 me-2" data-bs-dismiss="modal">انصراف</button>
                                        <button type="submit" disabled={isSubmitting} className="btn btn-danger px-5 py-2 rounded-pill fw-bold font-13 shadow-sm hover-lift">
                                            {isSubmitting ? <div className="spinner-border spinner-border-sm text-white"></div> : 'ذخیره تغییرات'}
                                        </button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            
            <style jsx="true">{`
                .cursor-pointer { cursor: pointer; }
                .focus-danger:focus { background-color: #fff !important; box-shadow: 0 0 0 4px rgba(239, 64, 86, 0.1) !important; border: 1px solid #ef4056 !important; outline: none; }
                .hover-bg-light:hover { background-color: #f8f9fa !important; }
                .hover-lift { transition: transform 0.2s ease, box-shadow 0.2s; }
                .hover-lift:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(239, 64, 86, 0.15) !important; }
                .custom-toast { position: fixed; bottom: 30px; left: -400px; min-width: 300px; padding: 16px 24px; border-radius: 16px; z-index: 999999; transition: left 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
                .custom-toast.show { left: 30px; }

                @media (max-width: 768px) {
                    .custom-toast { left: 50% !important; transform: translateX(-50%); bottom: -100px; width: 90%; min-width: unset; transition: bottom 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
                    .custom-toast.show { bottom: 20px !important; left: 50% !important; }
                }
            `}</style>
        </div>
    );
};

export default ProfileInfo;