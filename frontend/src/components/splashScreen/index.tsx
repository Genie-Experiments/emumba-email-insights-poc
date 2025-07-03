import "./styles.css";
import magnifyingGlass from "./../../assets/magnifying-glass_4616846.png";

const SplashScreen = () => {
  return (
    <div className="background-container">
      <div className="splash-container">
        {/* <img
          src={magnifyingGlass}
          alt="magnifying glass"
          className="magnifying-glass"
        /> */}
        <div className="splash-text">emumba Email Insights</div>
      </div>
    </div>
  );
};

export default SplashScreen;
