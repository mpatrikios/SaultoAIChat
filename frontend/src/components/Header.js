import React from 'react';
import SumersaultLogo from './SumersaultLogo';

const Header = ({ title }) => {
  return (
    <div className="chat-header">
      <div className="chat-title">Sumersault Chat</div>
      <div className="logo-container">
        <SumersaultLogo height={45} />
      </div>
    </div>
  );
};

export default Header;