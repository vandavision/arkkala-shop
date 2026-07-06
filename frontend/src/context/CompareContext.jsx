import React, { createContext, useState, useEffect } from 'react';

export const CompareContext = createContext();

export const CompareProvider = ({ children }) => {
    const [compareIds, setCompareIds] = useState([]);
    const [toast, setToast] = useState({ show: false, message: '', type: 'success' });

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
        setToast({ show: true, message, type });
        setTimeout(() => setToast({ show: false, message: '', type: 'success' }), 3000);
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
            <div className={`custom-toast ${toast.show ? 'show' : ''} bg-${toast.type} shadow-lg d-flex align-items-center gap-3`} style={{zIndex: 9999999}}>
                <i className={`bi ${toast.type === 'success' ? 'bi-check-circle-fill' : toast.type === 'warning' ? 'bi-exclamation-triangle-fill' : 'bi-x-circle-fill'} fs-3 text-white`}></i>
                <span className="font-14 fw-bold text-white lh-base">{toast.message}</span>
            </div>
            <style jsx="true">{`
                .custom-toast { position: fixed; bottom: 30px; left: -400px; min-width: 300px; padding: 16px 24px; border-radius: 16px; transition: left 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
                .custom-toast.show { left: 30px; }
                @media (max-width: 768px) {
                    .custom-toast { left: 50% !important; transform: translateX(-50%); bottom: -100px; width: 90%; min-width: unset; transition: bottom 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55); }
                    .custom-toast.show { bottom: 20px !important; left: 50% !important; }
                }
            `}</style>
        </CompareContext.Provider>
    );
};