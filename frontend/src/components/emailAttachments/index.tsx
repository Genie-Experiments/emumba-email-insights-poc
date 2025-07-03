import React, { useState } from "react";
import "./styles.css";
import { EmailContributionAttachments } from "../../types/apiTypes";
import { Tag } from "antd";
import AttachmentModal from "../attachmentModal";

interface EmailAttachmentsProps {
  attachments: EmailContributionAttachments[];
}

const EmailAttachments: React.FC<EmailAttachmentsProps> = ({ attachments }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedAttachment, setSelectedAttachment] = useState<
    EmailContributionAttachments | undefined
  >(undefined);

  const openModal = (attachment: EmailContributionAttachments) => {
    setSelectedAttachment(attachment);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };
  return (
    <>
      <div className="attachment-tags-wrapper">
        <div className="attachment-tags">
          {attachments.map((attachment, i) => (
            <Tag
              className="attachment-tag"
              onClick={() => openModal(attachment)}
              key={i}
            >
              <div className="tag-content">
                <div className="tag-subject">{attachment.attachment_name}</div>
              </div>
            </Tag>
          ))}
        </div>
      </div>

      <AttachmentModal
        closeModal={closeModal}
        isModalOpen={isModalOpen}
        selectedAttachment={selectedAttachment}
      />
    </>
  );
};

export default EmailAttachments;
