import React, { useEffect } from "react";
import "./styles.css";
import ResponseMessageContent from "../responseMessageContent";
import ResponseMessageContentLoader from "../responseMessageContentLoader";
import EmailTags from "../emailTags";
import EmailAttachments from "../emailAttachments";
import { Collapse, notification } from "antd";
import { GptResponse } from "../../types/apiTypes";
import response_container_svg from "./../../assets/Vector.svg";

interface ResponseContainerProps {
  loading: boolean;
  response?: GptResponse;
  error: string | undefined;
}

const ResponseContainer: React.FC<ResponseContainerProps> = ({
  loading,
  response,
  error,
}) => {
  useEffect(() => {
    if (error) {
      notification.error({
        message: "Error",
        description: error,
        placement: "bottomRight",
        duration: 5,
      });
    }
  }, [error]);

  return (
    <>
      <div className="response-card-container">
        <div className="card-header">
          <img src={response_container_svg} alt="response container" />
          <h4>Results</h4>
        </div>
        <div className="card-content">
          <div className="response-container">
            {!response ? (
              <ResponseMessageContentLoader loading={loading} />
            ) : (
              <>
                <ResponseMessageContent response={response.response} />
                {response.email_contributions.length > 0 && (
                  <Collapse
                    className="email-tags-collapse"
                    size="large"
                    items={[
                      {
                        key: "1",
                        label: `Context Emails (${response.email_contributions.length})`,
                        children: (
                          <EmailTags
                            emails={response.email_contributions}
                            response={response.response}
                          />
                        ),
                      },
                    ]}
                  />
                )}
                {response.email_contributions_attachments.length > 0 && (
                  <Collapse
                    className="attachment-tag-collapse"
                    size="large"
                    items={[
                      {
                        key: "2",
                        label: `Context Attachments (${response.email_contributions_attachments.length})`,
                        children: (
                          <EmailAttachments
                            attachments={
                              response.email_contributions_attachments
                            }
                          />
                        ),
                      },
                    ]}
                  />
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default ResponseContainer;