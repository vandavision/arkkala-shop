import React from 'react';
import { Link } from 'react-router-dom';

const SectionHeader = ({ title, link = "#" }) => {
    return (
        <div className="section-header">
            <div className="header-title-wrapper">
                <span className="title-icon">∷</span>
                <h3 className="section-title">{title}</h3>
            </div>
            <Link to={link} className="view-all-btn">
                مشاهده همه
            </Link>
        </div>
    );
};

export default SectionHeader;