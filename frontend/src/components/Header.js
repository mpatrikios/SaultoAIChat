import React from 'react';
import SumersaultLogo from './SumersaultLogo';

const Header = ({ title }) => {
  return (
    <div className="chat-header">
      <div className="chat-title">{title}</div>
      <SumersaultLogo height={28} />
    </div>
  );
};

export default Header;