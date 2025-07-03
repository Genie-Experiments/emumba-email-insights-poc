export interface SubQuestion {
  question: string;
  tags: string[];
}

export interface GenerateRequestBody {
  query: string;
  company: string;
  sub_questions: SubQuestion[];
  db_table: string;
}

export interface GenerateResponse {
  success: boolean;
  data: GptResponse;
}

export interface FormattedEmail {
  EmailID: string;
  From: string;
  To: string[];
  BCC: string[];
  CC: string[];
  Date: string;
  Body: string;
  Subject: string;
  Attachments: string[];
}

export interface EmailContribution {
  email_id: string;
  Subject: string;
  From: string;
  Date: string;
  To: string[];
  CC: string[];
  BCC: string[];
  highlighted_text: string;
  contribution_score: number;
}

export interface EmailContributionAttachments {
  attachment_text: string;
  s3_link: string;
  contribution_score: number;
  attachment_name: string;
}

export interface GptResponse {
  formatted_emails: FormattedEmail[];
  response: string;
  s3_attachment_links: string[];
  email_contributions: EmailContribution[];
  email_contributions_attachments: EmailContributionAttachments[];
}

export interface CompanyName {
  id: number;
  company_name: string;
}
