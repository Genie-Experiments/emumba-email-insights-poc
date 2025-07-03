import { Modal } from "antd";
import React from "react";
// @ts-ignore
import { Markup } from "react-render-markup";
import { LinkOutlined } from "@ant-design/icons";

import "./styles.css";
import { EmailContributionAttachments } from "../../types/apiTypes";

interface AttachmentModalProps {
  isModalOpen: boolean;
  selectedAttachment: EmailContributionAttachments | undefined;
  closeModal: () => void;
}

const AttachmentModal: React.FC<AttachmentModalProps> = ({
  isModalOpen,
  selectedAttachment,
  closeModal,
}) => {
  return (
    <Modal
      open={isModalOpen}
      onCancel={closeModal}
      footer={null}
      className="attachment-modal"
      title="Attachment Details"
    >
      {selectedAttachment && (
        <div className="attachment-modal-content">
          <p className="attachment-keys">Title:</p>
          <p className="subject">{selectedAttachment.attachment_name}</p>
          <div className="attachment-body-text-container">
            <Markup markup={selectedAttachment.attachment_text} />
          </div>
          <div className="attachment-download-link">
            <LinkOutlined />
            <a href={selectedAttachment.s3_link}>
              {selectedAttachment.attachment_name}
            </a>
          </div>
        </div>
      )}
    </Modal>
  );
};

export default AttachmentModal;
