import React from "react";
import "./styles.css"; // Import the CSS file

const Footer: React.FC = () => {
  const year = new Date().getFullYear();
  const companyName = "emumba Enterprise GPT";

  return (
    <footer className="footer">
      <div className="footer-left">{companyName}</div>
      <div className="footer-right">
        &copy; {year} {companyName}. All Rights Reserved.
      </div>
    </footer>
  );
};

export default Footer;
