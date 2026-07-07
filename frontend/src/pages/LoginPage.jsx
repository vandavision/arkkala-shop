import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { sendOtp, registerWithEmail } from '../api/authApi';
import { AuthContext } from '../context/AuthContext';
import { SiteContext } from '../context/SiteContext';

const LoginPage = () => {
    const navigate = useNavigate();
    const { loginEmail, loginOtp } = useContext(AuthContext);
    const { settings } = useContext(SiteContext);

    const [step, setStep] = useState('identifier');
    const [identifier, setIdentifier] = useState('');
    const [password, setPassword] = useState('');
    const [passwordConfirm, setPasswordConfirm] = useState('');
    const [otpCode, setOtpCode] = useState('');
    const [loading, setLoading] = useState(false);

    const [toast, setToast] = useState({ show: false, message: '', type: 'success' });

    const showToast = (message, type = 'danger') => {
        setToast({ show: true, message, type });
        setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 4000);
    };

    const isPhone = (val) => /^09\d{9}$/.test(val);
    const isEmail = (val) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);

    const handleIdentifierSubmit = async (e) => {
        e.preventDefault();
        const trimmed = identifier.trim();
        
        if (!trimmed) return showToast('لطفاً ایمیل یا شماره موبایل خود را وارد کنید.');

        setLoading(true);
        try {
            if (isPhone(trimmed)) {
                await sendOtp(trimmed);
                setStep('otp');
            } else if (isEmail(trimmed)) {
                setStep('password');
            } else {
                showToast('فرمت ایمیل یا شماره موبایل صحیح نیست.');
            }
        } catch (error) {
            showToast(error.response?.data?.error || 'خطا در ارتباط با سرور.');
        } finally {
            setLoading(false);
        }
    };

    const handlePasswordLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await loginEmail(identifier.trim(), password);
            navigate('/');
        } catch (error) {
            showToast(error.response?.data?.error || 'ایمیل یا رمز عبور اشتباه است.');
        } finally {
            setLoading(false);
        }
    };

    const handleOtpVerify = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await loginOtp(identifier.trim(), otpCode);
            navigate('/');
        } catch (error) {
            showToast(error.response?.data?.error || 'کد تایید اشتباه یا منقضی شده است.');
        } finally {
            setLoading(false);
        }
    };

    const handleEmailRegister = async (e) => {
        e.preventDefault();
        if (password !== passwordConfirm) return showToast('رمز عبور و تکرار آن مطابقت ندارند.');
        
        setLoading(true);
        try {
            await registerWithEmail({ email: identifier.trim(), password, password_confirm: passwordConfirm });
            showToast('ثبت نام با موفقیت انجام شد. اکنون وارد شوید.', 'success');
            setStep('password');
        } catch (error) {
            const errData = error.response?.data;
            if (errData && errData.email) showToast(errData.email[0]);
            else showToast('خطا در ثبت نام.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="auth-page bg-light min-vh-100 d-flex align-items-center justify-content-center py-5">
            <div className={`custom-toast ${toast.show ? 'show' : ''} bg-${toast.type} shadow-lg d-flex align-items-center gap-3`}>
                <i className={`bi ${toast.type === 'success' ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill'} fs-3 text-white`}></i>
                <span className="font-14 fw-bold text-white lh-base">{toast.message}</span>
            </div>

            <div className="container">
                <div className="row justify-content-center">
                    <div className="col-12 col-md-8 col-lg-5 col-xl-4">
                        <div className="bg-white p-4 p-md-5 rounded-5 shadow-sm border border-ui text-center animate-fade-in">
                            
                            <Link to="/" className="d-inline-block mb-4">
                                <img src={settings?.logo_url || "/assets/image/logo.png"} alt="Logo" style={{maxHeight: '50px'}} />
                            </Link>

                            <h4 className="fw-900 text-dark mb-4">ورود | ثبت‌نام</h4>

                            {step === 'identifier' && (
                                <form onSubmit={handleIdentifierSubmit}>
                                    <div className="text-start mb-4">
                                        <label className="font-13 fw-bold text-dark mb-2">سلام!</label>
                                        <p className="font-13 text-muted">لطفاً شماره موبایل یا ایمیل خود را وارد کنید</p>
                                        <input 
                                            type="text" 
                                            className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-14 focus-danger text-start" 
                                            placeholder="مثال: 09123456789 یا email@domain.com"
                                            value={identifier}
                                            onChange={(e) => setIdentifier(e.target.value)}
                                            dir="ltr"
                                            autoFocus
                                        />
                                    </div>
                                    <button type="submit" disabled={loading} className="btn btn-danger w-100 py-3 rounded-pill fw-bold shadow-sm hover-lift">
                                        {loading ? <div className="spinner-border spinner-border-sm text-white"></div> : 'ورود به ارک کالا'}
                                    </button>
                                    <p className="font-11 text-muted mt-4 lh-lg">
                                        با ورود و یا ثبت نام در سایت شما <Link to="/rules" className="text-danger text-decoration-none">شرایط و قوانین</Link> استفاده از سرویس های سایت و قوانین حریم خصوصی آن را می‌پذیرید.
                                    </p>
                                </form>
                            )}

                            {step === 'password' && (
                                <form onSubmit={handlePasswordLogin} className="animate-fade-in">
                                    <div className="text-start mb-4">
                                        <div className="d-flex justify-content-between align-items-center mb-3">
                                            <span className="font-13 fw-bold text-dark">رمز عبور خود را وارد کنید</span>
                                            <button type="button" onClick={() => setStep('identifier')} className="btn btn-link p-0 font-12 text-danger text-decoration-none"><i className="bi bi-pencil-square"></i> تغییر ایمیل</button>
                                        </div>
                                        <input 
                                            type="password" 
                                            className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-14 focus-danger text-start" 
                                            placeholder="رمز عبور"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            dir="ltr"
                                            autoFocus
                                        />
                                    </div>
                                    <button type="submit" disabled={loading} className="btn btn-danger w-100 py-3 rounded-pill fw-bold shadow-sm hover-lift mb-3">
                                        {loading ? <div className="spinner-border spinner-border-sm text-white"></div> : 'ورود'}
                                    </button>
                                    <button type="button" onClick={() => setStep('register')} className="btn btn-outline-danger w-100 py-3 rounded-pill fw-bold shadow-sm hover-lift">
                                        حساب کاربری ندارید؟ ثبت‌نام
                                    </button>
                                </form>
                            )}

                            {step === 'otp' && (
                                <form onSubmit={handleOtpVerify} className="animate-fade-in">
                                    <div className="text-start mb-4">
                                        <div className="d-flex justify-content-between align-items-center mb-3">
                                            <span className="font-13 fw-bold text-dark">کد تایید پیامک شده را وارد کنید</span>
                                            <button type="button" onClick={() => setStep('identifier')} className="btn btn-link p-0 font-12 text-danger text-decoration-none"><i className="bi bi-pencil-square"></i> تغییر شماره</button>
                                        </div>
                                        <p className="font-12 text-muted mb-3">کد تایید برای شماره <bdi className="text-dark fw-bold">{identifier}</bdi> ارسال شد.</p>
                                        <input 
                                            type="text" 
                                            maxLength="5"
                                            className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-20 fw-bold focus-danger text-center letter-spacing-lg" 
                                            placeholder="- - - - -"
                                            value={otpCode}
                                            onChange={(e) => setOtpCode(e.target.value)}
                                            dir="ltr"
                                            autoFocus
                                        />
                                    </div>
                                    <button type="submit" disabled={loading} className="btn btn-danger w-100 py-3 rounded-pill fw-bold shadow-sm hover-lift">
                                        {loading ? <div className="spinner-border spinner-border-sm text-white"></div> : 'تایید و ورود'}
                                    </button>
                                </form>
                            )}

                            {step === 'register' && (
                                <form onSubmit={handleEmailRegister} className="animate-fade-in">
                                    <div className="text-start mb-4">
                                        <div className="d-flex justify-content-between align-items-center mb-3">
                                            <span className="font-13 fw-bold text-dark">ثبت‌نام با ایمیل</span>
                                            <button type="button" onClick={() => setStep('identifier')} className="btn btn-link p-0 font-12 text-danger text-decoration-none">بازگشت</button>
                                        </div>
                                        <input 
                                            type="password" 
                                            className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-14 focus-danger text-start mb-3" 
                                            placeholder="رمز عبور"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            dir="ltr"
                                            required
                                            autoFocus
                                        />
                                        <input 
                                            type="password" 
                                            className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-14 focus-danger text-start" 
                                            placeholder="تکرار رمز عبور"
                                            value={passwordConfirm}
                                            onChange={(e) => setPasswordConfirm(e.target.value)}
                                            dir="ltr"
                                            required
                                        />
                                    </div>
                                    <button type="submit" disabled={loading} className="btn btn-danger w-100 py-3 rounded-pill fw-bold shadow-sm hover-lift">
                                        {loading ? <div className="spinner-border spinner-border-sm text-white"></div> : 'ثبت نام'}
                                    </button>
                                </form>
                            )}

                        </div>
                    </div>
                </div>
            </div>

            <style jsx="true">{`
                .focus-danger:focus { background-color: #fff !important; box-shadow: 0 0 0 4px rgba(239, 64, 86, 0.1) !important; border: 1px solid #ef4056 !important; outline: none; }
                .letter-spacing-lg { letter-spacing: 15px; }
                .hover-lift { transition: transform 0.2s ease, box-shadow 0.2s; }
                .hover-lift:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(239, 64, 86, 0.15) !important; }
                .animate-fade-in { animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
                
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

export default LoginPage;