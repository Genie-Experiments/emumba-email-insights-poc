import React, { useEffect, useState } from "react";
import "./styles.css";
import GptQueryForm2 from "../../components/gptQueryForm2";
import ResponseContainer from "../../components/responseContainer";
import { CompanyName, GptResponse } from "../../types/apiTypes";
import Navbar from "../../components/header";
import { fetchCompanyNames } from "../../api/fetchCompanyNames";

const Homepage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<GptResponse | undefined>(undefined);
  const [error, setError] = useState<string | undefined>(undefined);
  const [isCollapsed, setIsCollapsed] = useState(false); // State to handle collapse/expand
  const [companyNames, setCompanyNames] = useState<CompanyName[]>([]);

  useEffect(() => {
    const getCompanyNames = async () => {
      try {
        const response = await fetchCompanyNames();
        setCompanyNames(response);
      } catch (error) {
        console.error("Error fetching company names:", error);
        setError("Something went wrong. Please try again later.");
      }
    };

    getCompanyNames();
  }, []);

  const onSetResponse = (value: GptResponse) => {
    setResponse(value);
  };

  const onSetLoading = (value: boolean) => {
    setLoading(value);
  };

  const onSetError = (value: string | undefined) => {
    setError(value);
  };

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <div className="homepage">
      <Navbar />
      <div className="container">
        <h1>emumba Email Insights</h1>
        <p>
          Unlock valuable insights from your team's email conversations with
          AI-powered retrieval and analysis.
        </p>
        <div className="form-and-response">
          <div className={`leftside ${isCollapsed ? "collapsed" : ""}`}>
            <GptQueryForm2
              companyNames={companyNames}
              toggleCollapse={toggleCollapse}
              onSetError={onSetError}
              onSetResponse={onSetResponse}
              loading={loading}
              onSetLoading={onSetLoading}
              isCollapsed={isCollapsed}
            />
          </div>
          <div className="rightside">
            <ResponseContainer
              response={response}
              loading={loading}
              error={error}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Homepage;
