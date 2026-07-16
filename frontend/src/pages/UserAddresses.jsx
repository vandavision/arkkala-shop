import React, { useState, useEffect } from 'react';
import { getUserAddresses, addUserAddress, deleteUserAddress, setDefaultAddress } from '../api/authApi';

const UserAddresses = () => {
    const [addresses, setAddresses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isSubmitting, setIsSubmitting] = useState(false);
    
    const [formData, setFormData] = useState({
        title: '', recipient_first_name: '', recipient_last_name: '', recipient_phone: '',
        province: '', city: '', postal_address: '', postal_code: '', plaque: '', building_unit: ''
    });

    const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
    const showToast = (message, type = 'success') => {
        setToast({ show: true, message, type });
        setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 4000);
    };

    const fetchAddresses = async () => {
        try {
            const data = await getUserAddresses();
            setAddresses(data.results || data || []);
        } catch (error) {
            console.error(error);
            showToast("خطا در دریافت لیست آدرس‌ها", "danger");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAddresses();
    // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const handleChange = (e) => setFormData({ ...formData, [e.target.name]: e.target.value });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsSubmitting(true);
        try {
            await addUserAddress(formData);
            showToast("آدرس جدید با موفقیت ثبت شد.", "success");
            setFormData({ title: '', recipient_first_name: '', recipient_last_name: '', recipient_phone: '', province: '', city: '', postal_address: '', postal_code: '', plaque: '', building_unit: '' });
            document.querySelector('#addAddressModal .btn-close').click();
            fetchAddresses();
        } catch (error) {
            showToast("خطا در ثبت آدرس. لطفا فیلدها را بررسی کنید.", "danger");
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm("آیا از حذف این آدرس اطمینان دارید؟")) {
            try {
                await deleteUserAddress(id);
                showToast("آدرس با موفقیت حذف شد.", "success");
                fetchAddresses();
            } catch (error) {
                showToast("خطا در حذف آدرس.", "danger");
            }
        }
    };

    const handleSetDefault = async (id) => {
        try {
            await setDefaultAddress(id);
            showToast("آدرس پیش‌فرض با موفقیت تغییر کرد.", "success");
            fetchAddresses();
        } catch (error) {
            showToast("خطا در تغییر آدرس پیش‌فرض.", "danger");
        }
    };

    if (loading) {
        return (
            <div className="text-center py-5 d-flex flex-column align-items-center justify-content-center bg-white rounded-4 shadow-sm border border-ui min-vh-50">
                <div className="spinner-border text-danger mb-3" style={{width: '3rem', height:'3rem'}}></div>
                <h6 className="font-14 fw-bold text-muted">در حال دریافت آدرس‌ها...</h6>
            </div>
        );
    }

    return (
        <div className="user-addresses position-relative">
            <div className={`custom-toast ${toast.show ? 'show' : ''} bg-${toast.type} shadow-lg d-flex align-items-center gap-3`} style={{zIndex: 99999}}>
                <i className={`bi ${toast.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill'} fs-3 text-white`}></i>
                <span className="font-14 fw-bold text-white lh-base">{toast.message}</span>
            </div>

            <div className="bg-white p-3 p-md-4 rounded-4 border border-ui shadow-sm mb-4 d-flex align-items-center justify-content-between flex-wrap gap-3">
                <div className="d-flex align-items-center gap-3">
                    <div className="bg-primary bg-opacity-10 p-3 rounded-circle d-flex align-items-center justify-content-center">
                        <i className="bi bi-geo-alt-fill text-primary fs-3"></i>
                    </div>
                    <div>
                        <h2 className="fw-900 h5 m-0 text-dark mb-1">دفترچه <span className="text-danger">آدرس‌ها</span></h2>
                        <span className="text-muted font-12">مدیریت آدرس‌های ارسال کالا</span>
                    </div>
                </div>
                <button className="btn btn-danger rounded-pill px-4 py-2 font-13 fw-bold shadow-sm hover-lift" data-bs-toggle="modal" data-bs-target="#addAddressModal">
                    <i className="bi bi-plus-circle me-1"></i> ثبت آدرس جدید
                </button>
            </div>

            <div className="row gy-4">
                {addresses.length === 0 ? (
                    <div className="col-12">
                        <div className="text-center py-5 my-3 bg-white rounded-4 shadow-sm border border-ui min-h-300 d-flex flex-column align-items-center justify-content-center">
                            <i className="bi bi-map text-muted opacity-25 d-block mb-3" style={{ fontSize: '5rem' }}></i>
                            <h5 className="fw-bold text-dark mb-2 font-16">هیچ آدرسی ثبت نکرده‌اید!</h5>
                            <p className="text-muted font-13 mb-4">برای تسریع در روند خرید، آدرس‌های خود را اینجا ثبت کنید.</p>
                        </div>
                    </div>
                ) : (
                    addresses.map(addr => (
                        <div className="col-md-6 col-lg-6 col-xl-6" key={addr.uuid}>
                            <div className="bg-white rounded-4 shadow-sm border border-ui p-4 h-100 position-relative hover-shadow transition">
                                <div className="d-flex align-items-center justify-content-between mb-3 pb-3 border-bottom border-light">
                                    <div className="d-flex align-items-center gap-2">
                                        <i className="bi bi-geo-alt text-danger fs-5"></i>
                                        <h5 className="fw-bold font-15 text-dark m-0">{addr.title}</h5>
                                    </div>
                                    {addr.is_default && <span className="badge bg-success font-11 rounded-pill px-2 py-1"><i className="bi bi-check-circle me-1"></i>پیش‌فرض</span>}
                                </div>
                                <p className="font-13 text-muted lh-lg mb-4 text-justify min-h-50">{addr.province}، {addr.city}، {addr.postal_address} {addr.plaque ? `، پلاک ${addr.plaque}` : ''} {addr.building_unit ? `، واحد ${addr.building_unit}` : ''}</p>
                                
                                <div className="bg-light rounded-3 p-3 mb-4 border border-light">
                                    <div className="d-flex align-items-center gap-2 mb-2">
                                        <i className="bi bi-person text-secondary"></i>
                                        <span className="font-13 text-dark fw-bold">{addr.recipient_first_name} {addr.recipient_last_name}</span>
                                    </div>
                                    <div className="d-flex align-items-center gap-2 mb-2">
                                        <i className="bi bi-telephone text-secondary"></i>
                                        <span className="font-13 text-dark" dir="ltr">{addr.recipient_phone}</span>
                                    </div>
                                    <div className="d-flex align-items-center gap-2">
                                        <i className="bi bi-envelope-paper text-secondary"></i>
                                        <span className="font-13 text-dark">کد پستی: <span dir="ltr">{addr.postal_code}</span></span>
                                    </div>
                                </div>

                                <div className="d-flex align-items-center justify-content-between mt-auto">
                                    {!addr.is_default ? (
                                        <button onClick={() => handleSetDefault(addr.uuid)} className="btn btn-sm btn-outline-primary rounded-pill px-3 font-12 fw-bold hover-lift transition">تنظیم به عنوان پیش‌فرض</button>
                                    ) : <div></div>}
                                    <button onClick={() => handleDelete(addr.uuid)} className="btn btn-sm text-danger hover-text-dark font-20 p-0" title="حذف آدرس"><i className="bi bi-trash3-fill"></i></button>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Add Address Modal */}
            <div className="modal fade" id="addAddressModal" tabIndex="-1" aria-hidden="true">
                <div className="modal-dialog modal-lg modal-dialog-centered">
                    <div className="modal-content rounded-4 border-0 shadow-lg">
                        <div className="modal-header bg-light border-bottom border-light px-4 py-3">
                            <h5 className="modal-title fw-900 font-16 text-dark d-flex align-items-center gap-2"><i className="bi bi-map text-danger fs-4"></i> ثبت آدرس جدید</h5>
                            <button type="button" className="btn-close shadow-none" data-bs-dismiss="modal" aria-label="بستن"></button>
                        </div>
                        <div className="modal-body p-4 p-md-5">
                            <form onSubmit={handleSubmit}>
                                <div className="row gy-4">
                                    <div className="col-md-12">
                                        <label className="fw-bold font-13 text-dark mb-2">عنوان آدرس <span className="text-danger">*</span></label>
                                        <input type="text" name="title" value={formData.title} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light" placeholder="مثال: خانه، محل کار" required />
                                    </div>
                                    <div className="col-md-6">
                                        <label className="fw-bold font-13 text-dark mb-2">نام تحویل گیرنده <span className="text-danger">*</span></label>
                                        <input type="text" name="recipient_first_name" value={formData.recipient_first_name} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light" required />
                                    </div>
                                    <div className="col-md-6">
                                        <label className="fw-bold font-13 text-dark mb-2">نام خانوادگی تحویل گیرنده <span className="text-danger">*</span></label>
                                        <input type="text" name="recipient_last_name" value={formData.recipient_last_name} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light" required />
                                    </div>
                                    <div className="col-md-6">
                                        <label className="fw-bold font-13 text-dark mb-2">شماره تماس <span className="text-danger">*</span></label>
                                        <input type="text" name="recipient_phone" value={formData.recipient_phone} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light text-start" dir="ltr" placeholder="09123456789" required />
                                    </div>
                                    <div className="col-md-6">
                                        <label className="fw-bold font-13 text-dark mb-2">استان <span className="text-danger">*</span></label>
                                        <input type="text" name="province" value={formData.province} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light" required />
                                    </div>
                                    <div className="col-md-6">
                                        <label className="fw-bold font-13 text-dark mb-2">شهر <span className="text-danger">*</span></label>
                                        <input type="text" name="city" value={formData.city} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light" required />
                                    </div>
                                    <div className="col-md-6">
                                        <label className="fw-bold font-13 text-dark mb-2">کد پستی <span className="text-danger">*</span></label>
                                        <input type="text" name="postal_code" value={formData.postal_code} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light text-start" dir="ltr" required />
                                    </div>
                                    <div className="col-12">
                                        <label className="fw-bold font-13 text-dark mb-2">آدرس پستی دقیق <span className="text-danger">*</span></label>
                                        <textarea name="postal_address" value={formData.postal_address} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-4 shadow-sm bg-light lh-lg" rows="2" required></textarea>
                                    </div>
                                    <div className="col-md-6">
                                        <label className="fw-bold font-13 text-dark mb-2">پلاک <span className="text-danger">*</span></label>
                                        <input type="text" name="plaque" value={formData.plaque} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light" required />
                                    </div>
                                    <div className="col-md-6">
                                        <label className="fw-bold font-13 text-dark mb-2">واحد</label>
                                        <input type="text" name="building_unit" value={formData.building_unit} onChange={handleChange} className="form-control border-ui py-3 font-13 rounded-3 shadow-sm bg-light" placeholder="اختیاری" />
                                    </div>
                                    <div className="col-12 text-end mt-4">
                                        <button type="button" className="btn btn-light px-4 py-2 rounded-pill fw-bold font-13 me-2" data-bs-dismiss="modal">انصراف</button>
                                        <button type="submit" disabled={isSubmitting} className="btn btn-danger px-5 py-2 rounded-pill fw-bold font-13 shadow-sm hover-lift">
                                            {isSubmitting ? <div className="spinner-border spinner-border-sm text-white"></div> : 'ثبت آدرس'}
                                        </button>
                                    </div>
                                </div>
                            </form>
                        </div>
                    </div>
                </div>
            </div>
            
            <style jsx="true">{`
                .hover-lift { transition: transform 0.2s ease, box-shadow 0.2s; }
                .hover-lift:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,0,0,0.08) !important; }
                .hover-shadow:hover { box-shadow: 0 15px 30px rgba(0,0,0,0.06) !important; border-color: #dee2e6 !important;}
                .transition { transition: all 0.3s ease; }
                .min-h-300 { min-height: 300px; }
                .min-h-50 { min-height: 50px; }
                .custom-toast { position: fixed; bottom: 30px; left: -400px; min-width: 300px; padding: 16px 24px; border-radius: 16px; z-index: 999999; transition: left 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
                .custom-toast.show { left: 30px; }
            `}</style>
        </div>
    );
};

export default UserAddresses;