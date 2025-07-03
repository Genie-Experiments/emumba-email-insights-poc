import { Tag } from "antd";
import React, { useState } from "react";
import { EmailContribution } from "../../types/apiTypes";
import EmailModal from "./../emailModal"; // Import the new modal component
import "./styles.css";

interface EmailTagsProps {
  emails: EmailContribution[];
  response: string;
}

const EmailTags: React.FC<EmailTagsProps> = ({ emails, response }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedEmail, setSelectedEmail] = useState<
    EmailContribution | undefined
  >(undefined);

  const openModal = (email: EmailContribution) => {
    setSelectedEmail(email);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  return (
    <>
      <div className="email-tags-wrapper">
        <div className="email-tags">
          {emails.map((email, i) => (
            <Tag className="email-tag" onClick={() => openModal(email)} key={i}>
              <div className="tag-content">
                <div className="tag-subject">
                  {email.Subject || "No Subject"}
                </div>
                <div className="tag-date">
                  {new Date(email.Date).toLocaleDateString()}
                </div>
              </div>
            </Tag>
          ))}
        </div>
      </div>
      <EmailModal
        isModalOpen={isModalOpen}
        selectedEmail={selectedEmail}
        closeModal={closeModal}
        response={response}
      />
    </>
  );
};

export default EmailTags;
