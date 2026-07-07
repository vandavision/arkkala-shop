import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { sendOtp, registerWithEmail, requestPasswordReset, confirmPasswordReset } from '../api/authApi';
import { AuthContext } from '../context/AuthContext';
import { SiteContext } from '../context/SiteContext';

const LoginPage = () => {
    const navigate = useNavigate();
    const { authMode, loginEmail, loginOtp } = useContext(AuthContext);
    const { settings } = useContext(SiteContext);

    // Modes
    const isEmailMode = authMode === 'EMAIL';

    // Steps: 'identifier' | 'password' | 'otp' | 'register' | 'forgot_request' | 'forgot_verify'
    const [step, setStep] = useState('identifier');
    
    // Form States
    const [identifier, setIdentifier] = useState(''); // phone or email
    const [password, setPassword] = useState('');
    const [passwordConfirm, setPasswordConfirm] = useState('');
    const [otpCode, setOtpCode] = useState('');
    const [loading, setLoading] = useState(false);

    // Toast
    const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
    const showToast = (message, type = 'danger') => {
        setToast({ show: true, message, type });
        setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 4000);
    };

    const isPhone = (val) => /^09\d{9}$/.test(val);
    const isEmail = (val) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val);

    // =============================================
    // HANDLERS
    // =============================================
    
    const handleIdentifierSubmit = async (e) => {
        e.preventDefault();
        const trimmed = identifier.trim();
        
        if (!trimmed) return showToast(isEmailMode ? 'لطفاً ایمیل خود را وارد کنید.' : 'لطفاً شماره موبایل خود را وارد کنید.');

        setLoading(true);
        try {
            if (isEmailMode) {
                if (!isEmail(trimmed)) return showToast('فرمت ایمیل نامعتبر است.');
                setStep('password');
            } else {
                if (!isPhone(trimmed)) return showToast('شماره موبایل نامعتبر است. (مثال: 09123456789)');
                await sendOtp(trimmed);
                setStep('otp');
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
        if (otpCode.length < 5) return showToast('کد تایید را کامل وارد کنید.');
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

    const handleForgotRequest = async (e) => {
        e.preventDefault();
        if (!isEmail(identifier.trim())) return showToast('لطفا ایمیل معتبری وارد کنید.');
        
        setLoading(true);
        try {
            await requestPasswordReset(identifier.trim());
            showToast('کد تایید به ایمیل شما ارسال شد.', 'success');
            setStep('forgot_verify');
        } catch (error) {
            showToast(error.response?.data?.error || 'خطا در ارسال کد.');
        } finally {
            setLoading(false);
        }
    };

    const handleForgotVerify = async (e) => {
        e.preventDefault();
        if (password !== passwordConfirm) return showToast('رمز عبور جدید و تکرار آن مطابقت ندارند.');
        if (otpCode.length < 6) return showToast('کد تایید ۶ رقمی ایمیل شده را وارد کنید.');

        setLoading(true);
        try {
            await confirmPasswordReset({
                email: identifier.trim(),
                code: otpCode,
                new_password: password,
                new_password_confirm: passwordConfirm
            });
            showToast('رمز عبور شما با موفقیت تغییر کرد. وارد شوید.', 'success');
            setStep('password');
            setPassword('');
            setPasswordConfirm('');
            setOtpCode('');
        } catch (error) {
            showToast(error.response?.data?.error || 'کد وارد شده اشتباه است.');
        } finally {
            setLoading(false);
        }
    };

    // =============================================
    // RENDERERS
    // =============================================

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
                                        <p className="font-13 text-muted">
                                            {isEmailMode ? 'لطفاً آدرس ایمیل خود را وارد کنید.' : 'لطفاً شماره موبایل خود را وارد کنید.'}
                                        </p>
                                        <input 
                                            type="text" 
                                            className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-14 focus-danger text-start" 
                                            placeholder={isEmailMode ? "email@domain.com" : "09123456789"}
                                            value={identifier}
                                            onChange={(e) => setIdentifier(e.target.value)}
                                            dir="ltr"
                                            autoFocus
                                            required
                                        />
                                    </div>
                                    <button type="submit" disabled={loading} className="btn btn-danger w-100 py-3 rounded-pill fw-bold shadow-sm hover-lift">
                                        {loading ? <div className="spinner-border spinner-border-sm text-white"></div> : 'ادامه'}
                                    </button>
                                    
                                    {isEmailMode && (
                                        <button type="button" onClick={() => { setStep('register'); setIdentifier(''); }} className="btn btn-outline-danger w-100 py-3 mt-3 rounded-pill fw-bold shadow-sm hover-lift">
                                            حساب کاربری ندارید؟ ثبت‌نام
                                        </button>
                                    )}

                                    <p className="font-11 text-muted mt-4 lh-lg">
                                        با ورود و یا ثبت نام در سایت شما <Link to="/rules" className="text-danger text-decoration-none">شرایط و قوانین</Link> استفاده از سرویس های سایت و قوانین حریم خصوصی آن را می‌پذیرید.
                                    </p>
                                </form>
                            )}

                            {step === 'otp' && !isEmailMode && (
                                <form onSubmit={handleOtpVerify} className="animate-fade-in">
                                    <div className="text-start mb-4">
                                        <div className="d-flex justify-content-between align-items-center mb-3">
                                            <span className="font-13 fw-bold text-dark">کد تایید پیامک شده را وارد کنید</span>
                                            <button type="button" onClick={() => setStep('identifier')} className="btn btn-link p-0 font-12 text-danger text-decoration-none"><i className="bi bi-pencil-square"></i> تغییر شماره</button>
                                        </div>
                                        <p className="font-12 text-muted mb-3">کد ۵ رقمی تایید برای <bdi className="text-dark fw-bold">{identifier}</bdi> ارسال شد.</p>
                                        <input 
                                            type="text" 
                                            maxLength="5"
                                            className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-20 fw-bold focus-danger text-center letter-spacing-lg" 
                                            placeholder="- - - - -"
                                            value={otpCode}
                                            onChange={(e) => setOtpCode(e.target.value.replace(/[^0-9]/g, ''))}
                                            dir="ltr"
                                            autoFocus
                                            required
                                        />
                                    </div>
                                    <button type="submit" disabled={loading} className="btn btn-danger w-100 py-3 rounded-pill fw-bold shadow-sm hover-lift">
                                        {loading ? <div className="spinner-border spinner-border-sm text-white"></div> : 'تایید و ورود'}
                                    </button>
                                </form>
                            )}

                            {step === 'password' && isEmailMode && (
                                <form onSubmit={handlePasswordLogin} className="animate-fade-in">
                                    <div className="text-start mb-4">
                                        <div className="d-flex justify-content-between align-items-center mb-3">
                                            <span className="font-13 fw-bold text-dark">رمز عبور حساب کاربری</span>
                                            <button type="button" onClick={() => setStep('identifier')} className="btn btn-link p-0 font-12 text-danger text-decoration-none"><i className="bi bi-pencil-square"></i> تغییر ایمیل</button>
                                        </div>
                                        <input 
                                            type="password" 
                                            className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-14 focus-danger text-start mb-3" 
                                            placeholder="رمز عبور"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            dir="ltr"
                                            autoFocus
                                            required
                                        />
                                        <div className="text-end">
                                            <button type="button" onClick={() => setStep('forgot_request')} className="btn btn-link p-0 font-12 text-muted text-decoration-none hover-text-danger">
                                                رمز عبور را فراموش کرده‌اید؟
                                            </button>
                                        </div>
                                    </div>
                                    <button type="submit" disabled={loading} className="btn btn-danger w-100 py-3 rounded-pill fw-bold shadow-sm hover-lift">
                                        {loading ? <div className="spinner-border spinner-border-sm text-white"></div> : 'ورود به حساب'}
                                    </button>
                                </form>
                            )}

                            {step === 'register' && isEmailMode && (
                                <form onSubmit={handleEmailRegister} className="animate-fade-in">
                                    <div className="text-start mb-4">
                                        <div className="d-flex justify-content-between align-items-center mb-3">
                                            <span className="font-13 fw-bold text-dark">ایجاد حساب کاربری جدید</span>
                                            <button type="button" onClick={() => setStep('identifier')} className="btn btn-link p-0 font-12 text-danger text-decoration-none">بازگشت</button>
                                        </div>
                                        <input 
                                            type="email" 
                                            className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-14 focus-danger text-start mb-3" 
                                            placeholder="آدرس ایمیل شما"
                                            value={identifier}
                                            onChange={(e) => setIdentifier(e.target.value)}
                                            dir="ltr"
                                            autoFocus
                                            required
                                        />
                                        <input 
                                            type="password" 
                                            className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-14 focus-danger text-start mb-3" 
                                            placeholder="رمز عبور قوی"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            dir="ltr"
                                            required
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

                            {step === 'forgot_request' && isEmailMode && (
                                <form onSubmit={handleForgotRequest} className="animate-fade-in">
                                    <div className="text-start mb-4">
                                        <div className="d-flex justify-content-between align-items-center mb-3">
                                            <span className="font-13 fw-bold text-dark">بازیابی رمز عبور</span>
                                            <button type="button" onClick={() => setStep('password')} className="btn btn-link p-0 font-12 text-danger text-decoration-none">بازگشت</button>
                                        </div>
                                        <p className="font-12 text-muted mb-3">ایمیل خود را وارد کنید تا کد بازیابی برای شما ارسال شود.</p>
                                        <input 
                                            type="email" 
                                            className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-14 focus-danger text-start" 
                                            placeholder="email@domain.com"
                                            value={identifier}
                                            onChange={(e) => setIdentifier(e.target.value)}
                                            dir="ltr"
                                            autoFocus
                                            required
                                        />
                                    </div>
                                    <button type="submit" disabled={loading} className="btn btn-danger w-100 py-3 rounded-pill fw-bold shadow-sm hover-lift">
                                        {loading ? <div className="spinner-border spinner-border-sm text-white"></div> : 'ارسال کد بازیابی'}
                                    </button>
                                </form>
                            )}

                            {step === 'forgot_verify' && isEmailMode && (
                                <form onSubmit={handleForgotVerify} className="animate-fade-in">
                                    <div className="text-start mb-4">
                                        <div className="d-flex justify-content-between align-items-center mb-3">
                                            <span className="font-13 fw-bold text-dark">تغییر رمز عبور</span>
                                            <button type="button" onClick={() => setStep('forgot_request')} className="btn btn-link p-0 font-12 text-danger text-decoration-none">تغییر ایمیل</button>
                                        </div>
                                        <p className="font-12 text-muted mb-3">کد ۶ رقمی ارسال شده به ایمیل را به همراه رمز عبور جدید وارد کنید.</p>
                                        
                                        <input 
                                            type="text" 
                                            maxLength="6"
                                            className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-16 fw-bold focus-danger text-center letter-spacing-lg mb-3" 
                                            placeholder="- - - - - -"
                                            value={otpCode}
                                            onChange={(e) => setOtpCode(e.target.value.replace(/[^0-9]/g, ''))}
                                            dir="ltr"
                                            autoFocus
                                            required
                                        />
                                        <input 
                                            type="password" 
                                            className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-14 focus-danger text-start mb-3" 
                                            placeholder="رمز عبور جدید"
                                            value={password}
                                            onChange={(e) => setPassword(e.target.value)}
                                            dir="ltr"
                                            required
                                        />
                                        <input 
                                            type="password" 
                                            className="form-control py-3 px-4 bg-light border-0 shadow-sm rounded-4 font-14 focus-danger text-start" 
                                            placeholder="تکرار رمز عبور جدید"
                                            value={passwordConfirm}
                                            onChange={(e) => setPasswordConfirm(e.target.value)}
                                            dir="ltr"
                                            required
                                        />
                                    </div>
                                    <button type="submit" disabled={loading} className="btn btn-danger w-100 py-3 rounded-pill fw-bold shadow-sm hover-lift">
                                        {loading ? <div className="spinner-border spinner-border-sm text-white"></div> : 'ذخیره و ورود'}
                                    </button>
                                </form>
                            )}

                        </div>
                    </div>
                </div>
            </div>

            <style jsx="true">{`
                .focus-danger:focus { background-color: #fff !important; box-shadow: 0 0 0 4px rgba(239, 64, 86, 0.1) !important; border: 1px solid #ef4056 !important; outline: none; }
                .letter-spacing-lg { letter-spacing: 12px; }
                .hover-lift { transition: transform 0.2s ease, box-shadow 0.2s; }
                .hover-lift:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(239, 64, 86, 0.15) !important; }
                .animate-fade-in { animation: fadeIn 0.4s cubic-bezier(0.16, 1, 0.3, 1); }
                @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
                
                .hover-text-danger:hover { color: #ef4056 !important;}
                
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