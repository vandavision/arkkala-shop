import React from 'react';
import { Link } from 'react-router-dom';

const SectionHeader = ({ title, highlight, link = "#", linkText = "مشاهده همه" }) => {
    return (
        <div className="d-flex flex-wrap align-items-center justify-content-between border-bottom border-light pb-3 mb-4">
            <div className="d-flex align-items-center gap-2">
                <div className="bg-danger rounded-pill" style={{width: '6px', height: '24px'}}></div>
                <h2 className="fw-900 h5 m-0 text-dark d-flex align-items-center gap-2">
                    <span>{title}</span> 
                    {highlight && <span className="text-danger">{highlight}</span>}
                </h2>
            </div>
            {link && link !== "#" && (
                <Link to={link} className="btn btn-outline-danger rounded-pill px-3 py-1 font-13 fw-bold shadow-sm hover-lift d-flex align-items-center gap-1 transition">
                    {linkText} <i className="bi bi-chevron-left font-12"></i>
                </Link>
            )}
        </div>
    );
};

export default SectionHeader;