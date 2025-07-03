import { MinusCircleOutlined, PlusOutlined } from "@ant-design/icons";
import { Button, Form, Input, Select } from "antd";
import React, { useEffect, useState } from "react";
import { QUESTIONS, SUBQUESTION_TAGS } from "./../../data/questions";
import lightning_bolt from "./../../assets/Vector 12.svg";
import "./styles.css";
import { generateResponse } from "../../api/generate";
import { MenuFoldOutlined, MenuUnfoldOutlined } from "@ant-design/icons";
import { CompanyName } from "../../types/apiTypes";

interface GptQueryForm2Props {
  loading: boolean;
  onSetError: (value: string | undefined) => void;
  onSetLoading: (value: boolean) => void;
  onSetResponse: (value: any) => void;
  toggleCollapse: () => void;
  isCollapsed: boolean;
  companyNames: CompanyName[];
}

const GptQueryForm2: React.FC<GptQueryForm2Props> = ({
  loading,
  onSetError,
  onSetLoading,
  onSetResponse,
  toggleCollapse,
  isCollapsed,
  companyNames,
}) => {
  const [form] = Form.useForm();
  const [selectedCompany, setSelectedCompany] = useState<string | null>(null);
  const [oldSelectedCompany, setOldSelectedCompany] = useState<string | null>(
    null
  );
  const [updatedQUESTIONS, setUpdatedQUESTIONS] = useState<any[]>([]);
  const [selectedSubQuestions, setSelectedSubQuestions] = useState<any[]>([]);

  useEffect(() => {
    if (selectedCompany) {
      console.log("Selected Company:", selectedCompany);
      const updatesQuestions = QUESTIONS.map((q) => {
        if (q.subQuestions) {
          return {
            ...q,
            subQuestions: q.subQuestions.map((sub) => {
              const companyRegex = new RegExp(
                `${oldSelectedCompany || "pwc"}`,
                "gi"
              );
              return {
                ...sub,
                label: sub.label.replace(companyRegex, selectedCompany),
              };
            }),
          };
        }
        setOldSelectedCompany(selectedCompany);
        return q;
      });
      setUpdatedQUESTIONS(updatesQuestions);
    }
  }, [selectedCompany]);

  const onFinish = async (values: any) => {
    console.log("Received values of form:", values);
    onSetError(undefined);
    onSetLoading(true);
    onSetResponse(undefined);
    try {
      const response = await generateResponse(values);
      console.log(response);
      onSetResponse(response);
      onSetLoading(false);
    } catch (error) {
      onSetLoading(false);
      onSetError("Error generating response. Please try again.");
      console.error("Error generating response:", error);
    }
  };

  // Handle company change and update subquestions
  const handleCompanyChange = (company: string) => {
    setSelectedCompany(company);

    form.setFieldsValue({ query: undefined, sub_questions: [] });
    setSelectedSubQuestions([]);
  };

  const handleQuestionChange = (questionValue: string) => {
    const selectedQuestion = updatedQUESTIONS.find(
      (q) => q.label === questionValue
    );

    if (selectedQuestion?.subQuestions) {
      const initialSubQuestions = selectedQuestion.subQuestions.map(
        (sub: any) => ({
          question: sub.label.replace("PWC", selectedCompany || "PWC"), // Default to "PWC" or the selected company
          tags: sub.tags.map((tag: any) => tag.value),
        })
      );
      setSelectedSubQuestions(initialSubQuestions);
      form.setFieldsValue({ sub_questions: initialSubQuestions });
    } else {
      setSelectedSubQuestions([]);
      form.setFieldsValue({ sub_questions: [] });
    }
  };

  return (
    <>
      <div className="card-container">
        <div className="card-header">
          <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
            <img src={lightning_bolt} alt="lightning bolt" />
            <h4>Inputs</h4>
          </div>
          <div className="header-toggler">
            {isCollapsed ? (
              <MenuUnfoldOutlined onClick={toggleCollapse} />
            ) : (
              <MenuFoldOutlined onClick={toggleCollapse} />
            )}
          </div>
        </div>
        <div className="card-content">
          <Form
            disabled={companyNames.length === 0}
            form={form}
            name="dynamic_form_nest_item"
            onFinish={onFinish}
            autoComplete="off"
            layout="vertical"
            className="gptQueryForm"
          >
            {/* Select Company */}
            <Form.Item
              name="company"
              label="Choose a client"
              rules={[{ required: true, message: "Please select a company!" }]}
            >
              <Select
                placeholder="Select a company"
                className="gptQueryFormSelect"
                onChange={handleCompanyChange}
                showSearch
                loading={companyNames.length === 0}
                disabled={companyNames.length === 0}
              >
                {companyNames.map((opt) => (
                  <Select.Option key={opt.id} value={opt.company_name}>
                    {opt.company_name}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>

            {/* Select Question */}
            <Form.Item
              name="query"
              label="Choose a question"
              rules={[{ required: true, message: "Please select a question!" }]}
            >
              <Select
                className="gptQueryFormSelect"
                placeholder="Select a question"
                onChange={handleQuestionChange}
              >
                {updatedQUESTIONS.map((q) => (
                  <Select.Option key={q.value} value={q.label}>
                    {q.label}
                  </Select.Option>
                ))}
              </Select>
            </Form.Item>

            {/* Subquestions */}
            {!isCollapsed && (
              <div className="form-list-container">
                <h5>Sub Questions</h5>
                <Form.List
                  name="sub_questions"
                  rules={[
                    {
                      validator: async (_, sub_questions) => {
                        if (!sub_questions || sub_questions.length === 0) {
                          return Promise.reject(
                            new Error("Please add at least one subquestion")
                          );
                        }
                      },
                    },
                  ]}
                  initialValue={selectedSubQuestions}
                >
                  {(fields, { add, remove }, { errors }) => (
                    <>
                      {fields.map(({ key, name, ...restField }, i) => (
                        <div key={key} className="form-item-wrapper">
                          {/* Subquestion Input */}
                          <Form.Item
                            {...restField}
                            name={[name, "question"]}
                            label={`Subquestion ${i + 1}`}
                            rules={[
                              {
                                required: true,
                                message: "Missing Subquestion",
                              },
                            ]}
                            className="subquestion-item-name"
                          >
                            <Input
                              placeholder="Enter subquestion"
                              className="gptQueryFormInput"
                            />
                          </Form.Item>

                          {/* Tags Display in Select */}
                          <Form.Item
                            {...restField}
                            name={[name, "tags"]}
                            label="Tags"
                            rules={[
                              {
                                required: true,
                                message: "Please select at least one tag",
                              },
                              {
                                validator: (_, tags) => {
                                  if (!tags || tags.length === 0) {
                                    return Promise.reject(new Error(""));
                                  }
                                  return Promise.resolve();
                                },
                              },
                            ]}
                            className="subquestion-item-tags"
                          >
                            <Select
                              className="gptQueryFormSelect"
                              mode="multiple"
                              placeholder="Select tags"
                              options={SUBQUESTION_TAGS}
                              value={form.getFieldValue([
                                "sub_questions",
                                name,
                                "tags",
                              ])}
                              onChange={(value) =>
                                form.setFieldsValue({
                                  sub_questions: form
                                    .getFieldValue("sub_questions")
                                    .map((subq: any, idx: number) =>
                                      idx === name
                                        ? { ...subq, tags: value }
                                        : subq
                                    ),
                                })
                              }
                              maxTagCount={1}
                              maxTagPlaceholder={(omittedValues) =>
                                `+${omittedValues.length}`
                              }
                            />
                          </Form.Item>

                          <MinusCircleOutlined onClick={() => remove(name)} />
                        </div>
                      ))}
                      <Form.Item>
                        <Button
                          type="dashed"
                          onClick={() => add()}
                          block
                          icon={<PlusOutlined />}
                          disabled={
                            fields.length >= 5 ||
                            loading ||
                            companyNames.length === 0 ||
                            !selectedCompany ||
                            !form.isFieldTouched("query")
                          }
                        >
                          Add Subquestion
                        </Button>
                        <Form.ErrorList errors={errors} />
                      </Form.Item>
                    </>
                  )}
                </Form.List>
              </div>
            )}

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                className="cta"
                loading={loading}
                disabled={
                  isCollapsed ||
                  companyNames.length === 0 ||
                  !form.isFieldTouched("company") ||
                  !form.isFieldTouched("query") ||
                  !!form.getFieldsError().filter(({ errors }) => errors.length)
                    .length
                }
              >
                Generate Response
              </Button>
            </Form.Item>
          </Form>
        </div>
      </div>
    </>
  );
};

export default GptQueryForm2;
