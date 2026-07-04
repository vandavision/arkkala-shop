// arkkala/frontend/src/components/SectionHeader.jsx
import React from 'react';
import { Link } from 'react-router-dom';

/**
 * Reusable Section Header with Title and "View All" button.
 * @param {Object} props
 * @param {string} props.title
 * @param {string} props.link
 */
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