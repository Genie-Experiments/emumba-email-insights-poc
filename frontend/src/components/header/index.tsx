import logo from "./../../assets/image 1.svg";
import navtag from "./../../assets/Frame 2609009.svg";
import "./styles.css";

const Navbar = () => {
  return (
    <nav className="navbar">
      <img src={logo} alt="Logo" className="navbar-logo" />
      <img src={navtag} alt="Powered by AI" className="navtag" />
    </nav>
  );
};

export default Navbar;
