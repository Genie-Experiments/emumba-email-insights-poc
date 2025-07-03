import { Modal, Tag, Popover } from "antd";
import React from "react";
import { EmailContribution } from "../../types/apiTypes";
// @ts-ignore
import { Markup } from "react-render-markup";

import "./styles.css";

import ResponseMessageContent from "../responseMessageContent";

interface EmailModalProps {
  isModalOpen: boolean;
  selectedEmail: EmailContribution | undefined;
  closeModal: () => void;
  response: string;
}

const EmailModal: React.FC<EmailModalProps> = ({
  isModalOpen,
  selectedEmail,
  closeModal,
  response,
}) => {
  const formatHighlightedText = (text: string) => {
    try {
      let formattedText = text.replace(/\n/g, "<br />");
      formattedText = formattedText.replace(
        /(<br \/>\s*){2,}/g,
        "<br /><br />"
      );
      return formattedText;
    } catch (error) {
      return text;
    }
  };

  // Function to render email chips
  const renderEmailChips = (emails: string[]) => {
    const maxVisibleChips = 3;

    if (emails.length <= maxVisibleChips) {
      return emails.map((email, index) => (
        <Tag key={index} className="to-email-tag">
          {email}
        </Tag>
      ));
    }

    // Show only the first 3, and then a "remaining" chip
    const visibleEmails = emails.slice(0, maxVisibleChips);
    const remainingEmails = emails.slice(maxVisibleChips);

    return (
      <>
        {visibleEmails.map((email, index) => (
          <Tag key={index} className="to-email-tag">
            {email}
          </Tag>
        ))}
        <Popover
          placement="bottom"
          content={remainingEmails.map((email, index) => (
            <p key={index} className="remaining-email">
              {email}
            </p>
          ))}
        >
          <Tag className="to-email-more-tag">
            +{remainingEmails.length} more
          </Tag>
        </Popover>
      </>
    );
  };

  return (
    <Modal
      open={isModalOpen}
      onCancel={closeModal}
      footer={null}
      className="email-modal"
      title="Email Details"
    >
      <div style={{ display: "flex", gap: "20px" }}>
        <div style={{ flex: 2 }}>
          {selectedEmail && (
            <div className="email-modal-content">
              {selectedEmail.Subject && (
                <>
                  <p className="email-keys">Subject:</p>
                  <p className="subject">{selectedEmail.Subject}</p>
                </>
              )}
              <p className="email-keys">From:</p>
              <p>
                {
                  <Tag className="to-email-tag">
                    {String(selectedEmail.From)}
                  </Tag>
                }
              </p>
              {selectedEmail.To.length > 0 && (
                <>
                  <p className="email-keys">To:</p>
                  <div className="email-to-container">
                    {renderEmailChips(selectedEmail.To)}
                  </div>
                </>
              )}
              {selectedEmail.CC[0] !== "No CC Addresses" &&
                selectedEmail.CC.length > 0 && (
                  <>
                    <p className="email-keys">CC:</p>
                    <div className="email-to-container">
                      {renderEmailChips(selectedEmail.CC)}
                    </div>
                    {/* <p>{selectedEmail.CC}</p> */}
                  </>
                )}
              {selectedEmail.BCC[0] !== "No BCC Addresses" &&
                selectedEmail.BCC.length > 0 && (
                  <>
                    <p className="email-keys">BCC:</p>
                    <div className="email-to-container">
                      {renderEmailChips(selectedEmail.BCC)}
                    </div>
                    {/* <p>{selectedEmail.BCC}</p> */}
                  </>
                )}
              <p className="email-keys">Received DateTime: </p>
              <p className="email-date">
                {new Date(selectedEmail.Date).toLocaleString()}
              </p>
              <div
                className="email-body-text-container"
                dangerouslySetInnerHTML={{
                  __html: formatHighlightedText(
                    selectedEmail.highlighted_text || ""
                  ),
                }}
              >
                {/* <Markup
                  markup={formatHighlightedText(
                    selectedEmail?.highlighted_text || ""
                  )}
                /> */}
              </div>
            </div>
          )}
        </div>
        <div style={{ flex: 1.5 }}>
          {<ResponseMessageContent response={response} isHeightFull />}
        </div>
      </div>
    </Modal>
  );
};

export default EmailModal;
