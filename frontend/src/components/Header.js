import React from 'react';
import SumersaultLogo from './SumersaultLogo';

const Header = ({ title, toggleSidebar, isSidebarOpen }) => {
  return (
    <div className="chat-header">
      <div className="header-left">
        <button className="navbar-toggle-btn" onClick={toggleSidebar}>
          {isSidebarOpen ? <i className="fas fa-times"></i> : <i className="fas fa-bars"></i>}
        </button>
        <div className="chat-title">Sumersault Chat</div>
      </div>
      <div className="logo-container">
        <SumersaultLogo height={28} />
      </div>
    </div>
  );
};

export default Header;