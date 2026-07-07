import React, { useState, useEffect } from 'react';

const CountdownTimer = ({ endTime, variant = 'danger' }) => {
    const [timeLeft, setTimeLeft] = useState(null);

    useEffect(() => {
        if (!endTime) return;

        const targetDate = new Date(endTime).getTime();

        const updateTimer = () => {
            const now = new Date().getTime();
            const distance = targetDate - now;

            if (distance <= 0) {
                setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0 });
                return;
            }

            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);

            setTimeLeft({ days, hours, minutes, seconds });
        };

        updateTimer();
        const intervalId = setInterval(updateTimer, 1000);

        return () => clearInterval(intervalId);
    }, [endTime]);

    if (!timeLeft) return null;

    if (timeLeft.days === 0 && timeLeft.hours === 0 && timeLeft.minutes === 0 && timeLeft.seconds === 0) {
        return null;
    }

    const formatNumber = (num) => String(num).padStart(2, '0');

    const themeClass = variant === 'white' 
        ? 'bg-white text-danger border border-white shadow-sm' 
        : 'bg-danger text-white border border-danger shadow-sm';

    const labelClass = variant === 'white' ? 'text-white' : 'text-danger';

    return (
        <div className="modern-countdown d-flex align-items-center justify-content-center gap-2" dir="ltr">
            {timeLeft.days > 0 && (
                <div className="d-flex flex-column align-items-center gap-1">
                    <div className={`time-box rounded-3 fw-900 d-flex align-items-center justify-content-center ${themeClass}`}>
                        {formatNumber(timeLeft.days)}
                    </div>
                </div>
            )}
            {timeLeft.days > 0 && <span className={`separator fw-bold ${variant === 'white' ? 'text-white' : 'text-danger'}`}>:</span>}

            <div className="d-flex flex-column align-items-center gap-1">
                <div className={`time-box rounded-3 fw-900 d-flex align-items-center justify-content-center ${themeClass}`}>
                    {formatNumber(timeLeft.hours)}
                </div>
            </div>
            <span className={`separator fw-bold pb-1 ${variant === 'white' ? 'text-white' : 'text-danger'}`}>:</span>

            <div className="d-flex flex-column align-items-center gap-1">
                <div className={`time-box rounded-3 fw-900 d-flex align-items-center justify-content-center ${themeClass}`}>
                    {formatNumber(timeLeft.minutes)}
                </div>
            </div>
            <span className={`separator fw-bold pb-1 ${variant === 'white' ? 'text-white' : 'text-danger'}`}>:</span>

            <div className="d-flex flex-column align-items-center gap-1">
                <div className={`time-box rounded-3 fw-900 d-flex align-items-center justify-content-center ${themeClass}`}>
                    {formatNumber(timeLeft.seconds)}
                </div>
            </div>

            <style jsx="true">{`
                .modern-countdown .time-box {
                    width: 32px;
                    height: 32px;
                    font-size: 14px;
                    font-family: 'system-ui', -apple-system, sans-serif;
                }
                .modern-countdown .separator {
                    font-size: 18px;
                    margin-top: -2px;
                }
            `}</style>
        </div>
    );
};

export default CountdownTimer;