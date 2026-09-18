import React from 'react';
import DemoBadge from '../common/DemoBadge';

export const SummaryCard = ({
  title,
  value,
  subtitle,
  icon: Icon,
  badgeType = 'demo',
  variant = 'default',
}) => {
  return (
    <div className={`soc-summary-card ${variant ? `variant-${variant}` : ''}`}>
      <div className="soc-summary-header">
        <span className="soc-summary-title">{title}</span>
        <div className="soc-summary-icon-wrap">
          {Icon && <Icon size={18} />}
        </div>
      </div>

      <div className="soc-summary-body">
        <div className="soc-summary-val-row">
          <span className="soc-summary-value">{value}</span>
          <DemoBadge type={badgeType} size="small" />
        </div>
        {subtitle && <span className="soc-summary-sub">{subtitle}</span>}
      </div>
    </div>
  );
};

export default SummaryCard;

