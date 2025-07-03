import React, { useState } from "react";
import { Form, Select, Button, ConfigProvider } from "antd";
import { PlusOutlined } from "@ant-design/icons";
import { questions, options, subquestionTags } from "../../data/questions";
import { FormValues } from "../../types/formTypes";
import { generateResponse } from "../../api/generate";
import GptQueryFormSubquestion from "../gptQueryFormSubquestion";

import "./styles.css";

const GptQueryForm: React.FC = () => {
  const [form] = Form.useForm();
  const [subquestions, setSubquestions] = useState<
    { subquestion: string; tags: string[] }[]
  >([{ subquestion: "", tags: [] }]);

  const addSubquestion = () => {
    if (subquestions.length < 5) {
      setSubquestions([...subquestions, { subquestion: "", tags: [] }]);
    }
  };

  const removeSubquestion = (index: number) => {
    if (subquestions.length > 1) {
      const newSubquestions = [...subquestions];
      newSubquestions.splice(index, 1);
      setSubquestions(newSubquestions);
    }
  };

  const handleSubquestionChange = (value: string, index: number) => {
    const newSubquestions = [...subquestions];
    newSubquestions[index].subquestion = value;
    setSubquestions(newSubquestions);
  };

  const handleTagChange = (tags: string[], index: number) => {
    const newSubquestions = [...subquestions];
    newSubquestions[index].tags = tags;
    setSubquestions(newSubquestions);
  };

  const onFinish = async (values: FormValues) => {
    console.log("Form values:", values);
    console.log("Subquestions:", subquestions);

    const payload = {
      query: values.question,
      company: values.option,
      db_table: "pwc_json_meddpicc",
    };

    try {
      const response = await generateResponse(payload.query, payload.company);
      console.log("Response from API:", response);
    } catch (error) {
      console.error("Error submitting form:", error);
    }
  };

  return (
    <Form
      form={form}
      name="gpt_query_form"
      layout="vertical"
      onFinish={onFinish}
      autoComplete="off"
      className="gptQueryForm"
    >
      {/* Question Dropdown */}
      <Form.Item
        name="question"
        label="Choose a question"
        rules={[{ required: true, message: "Please select a question!" }]}
      >
        <Select className="gptQueryFormSelect" placeholder="Select a question">
          {questions.map((q) => (
            <Select.Option key={q.value} value={q.value}>
              {q.label}
            </Select.Option>
          ))}
        </Select>
      </Form.Item>

      {/* Option Dropdown */}
      <Form.Item
        name="option"
        label="Choose an option"
        rules={[{ required: true, message: "Please select an option!" }]}
      >
        <Select placeholder="Select an option" className="gptQueryFormSelect">
          {options.map((opt) => (
            <Select.Option key={opt.value} value={opt.value}>
              {opt.label}
            </Select.Option>
          ))}
        </Select>
      </Form.Item>

      {/* Subquestions Section */}
      {subquestions.map((sub, index) => (
        <GptQueryFormSubquestion
          key={index}
          index={index}
          availableTags={Object.values(subquestionTags).map((tag) => ({
            value: tag,
            label: tag,
          }))}
          onTagChange={handleTagChange}
          onSubquestionChange={handleSubquestionChange}
          subquestionValue={sub.subquestion}
          tagsValue={sub.tags}
          onRemove={() => removeSubquestion(index)}
        />
      ))}

      {/* Add Subquestion Button */}
      <Form.Item>
        <Button
          type="dashed"
          onClick={addSubquestion}
          icon={<PlusOutlined />}
          block
          disabled={subquestions.length >= 5}
        >
          Add Subquestion
        </Button>
      </Form.Item>

      {/* Submit Button */}
      <Form.Item>
        <Button
          type="primary"
          htmlType="submit"
          block
          style={{ fontSize: "16px", height: "36px" }}
        >
          Generate Response
        </Button>
      </Form.Item>
    </Form>
  );
};

export default GptQueryForm;
