import React from "react";
import "./styles.css";
import Markdown from "react-markdown";

interface ResponseMessageContentProps {
  response?: string;
  isHeightFull?: boolean;
}

const ResponseMessageContent: React.FC<ResponseMessageContentProps> = ({
  response,
  isHeightFull,
}) => {
  return (
    <div
      className="response-message-content"
      style={isHeightFull ? { maxHeight: "75vh" } : undefined}
    >
      <div className="response-content">
        <Markdown>{response}</Markdown>
      </div>
    </div>
  );
};

export default ResponseMessageContent;
