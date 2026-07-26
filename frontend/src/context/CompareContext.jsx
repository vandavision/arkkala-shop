import React, { createContext, useState, useEffect } from 'react';

export const CompareContext = createContext();

export const CompareProvider = ({ children }) => {
    const [compareIds, setCompareIds] = useState([]);
    const [toast, setToast] = useState({ show: false, message: '', type: 'success' });
    const [toastTimer, setToastTimer] = useState(null);

    useEffect(() => {
        const saved = localStorage.getItem('compareIds');
        if (saved) {
            try {
                setCompareIds(JSON.parse(saved));
            } catch (e) {
                console.error("Error parsing compare ids from local storage");
            }
        }
    }, []);

    const showToast = (message, type = 'success') => {
        // اگر تایمر قبلی وجود داشت پاک می‌شود تا از تداخل پیام‌ها جلوگیری شود
        if (toastTimer) clearTimeout(toastTimer);
        
        setToast({ show: true, message, type });
        
        const timer = setTimeout(() => {
            // فقط پیام را مخفی می‌کنیم و نوع و متن را تغییر نمی‌دهیم تا تغییر رنگ ناگهانی رخ ندهد
            setToast(prev => ({ ...prev, show: false }));
        }, 3000);
        
        setToastTimer(timer);
    };

    const addToCompare = (id) => {
        if (compareIds.includes(id)) {
            showToast('این کالا از قبل در لیست مقایسه وجود دارد.', 'warning');
            return;
        }
        if (compareIds.length >= 4) {
            showToast('حداکثر ۴ کالا را می‌توانید همزمان مقایسه کنید.', 'danger');
            return;
        }
        const updated = [...compareIds, id];
        setCompareIds(updated);
        localStorage.setItem('compareIds', JSON.stringify(updated));
        showToast('کالا با موفقیت به لیست مقایسه اضافه شد.', 'success');
    };

    const removeFromCompare = (id) => {
        const updated = compareIds.filter(item => item !== id);
        setCompareIds(updated);
        localStorage.setItem('compareIds', JSON.stringify(updated));
        showToast('کالا از لیست مقایسه حذف شد.', 'success');
    };

    return (
        <CompareContext.Provider value={{ compareIds, addToCompare, removeFromCompare }}>
            {children}
            <div className={`compare-toast ${toast.show ? 'show' : ''} bg-${toast.type} shadow-lg d-flex align-items-center gap-3`}>
                <i className={`bi ${toast.type === 'success' ? 'bi-check-circle-fill' : toast.type === 'warning' ? 'bi-exclamation-triangle-fill' : 'bi-x-circle-fill'} fs-3 text-white`}></i>
                <span className="font-14 fw-bold text-white lh-base">{toast.message}</span>
            </div>
            <style jsx="true">{`
                .compare-toast { 
                    position: fixed !important; 
                    top: 30px !important; 
                    bottom: auto !important;
                    left: auto !important;
                    right: -400px !important; 
                    height: auto !important;
                    width: auto !important;
                    min-width: 300px !important;
                    max-width: 400px !important;
                    padding: 16px 24px !important; 
                    border-radius: 16px !important; 
                    z-index: 9999999 !important; 
                    transition: right 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55), top 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55) !important; 
                }
                .compare-toast.show { 
                    right: 30px !important; 
                }
                
                @media (max-width: 768px) {
                    .compare-toast { 
                        right: 16px !important; 
                        left: 16px !important; 
                        transform: none !important; 
                        top: -150px !important; 
                        bottom: auto !important; 
                        width: auto !important; 
                        min-width: unset !important; 
                        max-width: none !important;
                        transition: top 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55) !important; 
                    }
                    .compare-toast.show { 
                        top: 20px !important; 
                        left: 16px !important; 
                        right: 16px !important;
                    }
                }
            `}</style>
        </CompareContext.Provider>
    );
};