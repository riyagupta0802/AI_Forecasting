import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import Sidebar from './Sidebar';
import { useLanguage } from '../../hooks/useLanguage';

export const MobileDrawer = ({ isOpen, onClose, activePage, onNavigate }) => {
  const { t } = useLanguage();

  // Prevent background scroll when mobile drawer is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="mobile-drawer-overlay" onClick={onClose} role="dialog" aria-modal="true">
      <div
        className="mobile-drawer-content"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          type="button"
          className="mobile-drawer-close"
          onClick={onClose}
          aria-label={t('header.closeMenu')}
        >
          <X size={20} />
        </button>
        <Sidebar
          activePage={activePage}
          onNavigate={onNavigate}
          isMobile={true}
          onCloseMobile={onClose}
        />
      </div>
    </div>
  );
};

export default MobileDrawer;

