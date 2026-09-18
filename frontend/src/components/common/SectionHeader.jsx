import React from 'react';

/**
 * Standardized Section Header with title, subtitle, and action slots
 */
export const SectionHeader = ({ title, subtitle, badge, action }) => {
  return (
    <div className="section-header-wrap">
      <div className="section-header-text">
        <div className="section-header-title-row">
          <h2 className="section-heading">{title}</h2>
          {badge && <div className="section-header-badge">{badge}</div>}
        </div>
        {subtitle && <p className="section-subheading">{subtitle}</p>}
      </div>
      {action && <div className="section-header-action">{action}</div>}
    </div>
  );
};

export default SectionHeader;

