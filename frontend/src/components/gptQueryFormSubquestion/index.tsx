import React from "react";
import { Form, Input, Select, Button } from "antd";
import { MinusCircleOutlined } from "@ant-design/icons";

interface GptQueryFormSubquestionProps {
  index: number;
  availableTags: { value: string; label: string }[];
  onTagChange: (tags: string[], index: number) => void;
  onSubquestionChange: (value: string, index: number) => void;
  subquestionValue: string;
  tagsValue: string[];
  onRemove: () => void;
}

const GptQueryFormSubquestion: React.FC<GptQueryFormSubquestionProps> = ({
  index,
  availableTags,
  onTagChange,
  onSubquestionChange,
  subquestionValue,
  tagsValue,
  onRemove,
}) => {
  return (
    <Form.Item label={`Subquestion ${index + 1}`} className="subquestion-item">
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <Input
          placeholder="Type your subquestion here"
          value={subquestionValue}
          onChange={(e) => onSubquestionChange(e.target.value, index)}
          style={{ width: "60%" }}
        />
        <Select
          mode="multiple"
          placeholder="Select tags"
          value={tagsValue}
          onChange={(tags) => onTagChange(tags, index)}
          style={{ width: "30%" }}
        >
          {availableTags.map((tag) => (
            <Select.Option key={tag.value} value={tag.value}>
              {tag.label}
            </Select.Option>
          ))}
        </Select>
        {index > 0 && (
          <Button
            type="link"
            onClick={onRemove}
            icon={<MinusCircleOutlined />}
            danger
          />
        )}
      </div>
    </Form.Item>
  );
};

export default GptQueryFormSubquestion;
