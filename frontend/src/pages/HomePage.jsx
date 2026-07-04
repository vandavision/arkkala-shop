import React from 'react';
import { Link } from 'react-router-dom';

const HomePage = () => {
    return (
        <main className="container" style={{ marginTop: '50px', textAlign: 'center' }}>
            <h1>به فروشگاه ارک کالا خوش آمدید</h1>
            <p style={{ marginTop: '20px', color: '#6c757d' }}>
                صفحه اصلی در حال توسعه است...
            </p>
            
            {/* یک لینک تستی برای اینکه بتوانید صفحه محصول را ببینید */}
            <div style={{ marginTop: '40px' }}>
                <Link to="/product/1" className="btn btn-primary" style={{ textDecoration: 'none' }}>
                    مشاهده یک محصول تستی
                </Link>
            </div>
        </main>
    );
};

export default HomePage;