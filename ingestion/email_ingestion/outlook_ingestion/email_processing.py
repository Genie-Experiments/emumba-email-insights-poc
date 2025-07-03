import re
import html2text
import requests

def process_email(email):
    email_id = email.get('id', 'No Email ID')
    subject = email.get('subject', '')
    from_address = email.get('from', {}).get('emailAddress', {}).get('address', '')
    received_date_time = email.get('receivedDateTime', '')
    sent_date_time = email.get('sentDateTime', '')  
    conversation_id = email.get('conversationId', '')
    receiver_recipient = email.get('toRecipients', [])
    cc_recipients = email.get('ccRecipients', [])
    bcc_recipients = email.get('bccRecipients', [])

    cc_addresses = ', '.join([recipient.get('emailAddress', {}).get('address', '') for recipient in cc_recipients])
    bcc_addresses = ', '.join([recipient.get('emailAddress', {}).get('address', '') for recipient in bcc_recipients])
    
    body = email.get('body', {})
    body_content = body.get('content', '')
    content_type = body.get('contentType', 'text')

    if content_type == 'html':
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_images = True
        h.ignore_tables = True
        h.ignore_emphasis = True
        h.single_line_break = True
        h.body_width = 0
        text = h.handle(body_content)
        body_content = text.strip()


    email_content = (
        f"EmailID: {email_id}\n\n"
        f"ConversationId: {conversation_id}\n\n"
        f"Subject: {subject}\n"
        f"From: {from_address}\n"
        f"To: {receiver_recipient}\n"
        f"CC: {cc_addresses if cc_addresses else ''}\n"
        f"BCC: {bcc_addresses if bcc_addresses else ''}\n"
        f"Received DateTime: {received_date_time}\n"
        f"Sent DateTime: {sent_date_time}\n" 
        f"Body Text:\n{body_content}\n"
        f"\nThreads Content:\n\n" 
    )

    email_dict = {
        "EmailID": email_id,
        "ConversationId": conversation_id,
        "Subject": subject,
        "From": from_address,
        "To": receiver_recipient,
        "CC": cc_addresses if cc_addresses else "",
        "BCC": bcc_addresses if bcc_addresses else "",
        "Received DateTime": received_date_time,
        "Sent DateTime": sent_date_time,
        "Body Text": "",
        "AttachmentNames": []
    }

    return email_content, received_date_time, conversation_id, body_content, email_dict

def process_threads(conversation_id, user_id, headers):
    threads_endpoint = f"https://graph.microsoft.com/v1.0/users/{user_id}/messages?$filter=conversationId eq '{conversation_id}'"
    threads_response = requests.get(threads_endpoint, headers=headers)
    
    if threads_response.status_code == 400:
        print(f"Bad request for URL: {threads_endpoint}")
        print(f"Response: {threads_response.json()}")
        return [], None, {}, []

    threads_response.raise_for_status()
    threads_data = threads_response.json()

    thread_contents = []
    attachment_names_all = []
    received_date_time = None
    last_json = {}

    for thread in threads_data.get('value', []):
        thread_subject = thread.get('subject', '')
        thread_from_address = thread.get('from', {}).get('emailAddress', {}).get('address', '')
        thread_body = thread.get('body', {}).get('content', '')
        thread_content_type = thread.get('body', {}).get('contentType', 'text')
        received_date_time = thread.get('receivedDateTime', '')
        thread_id = thread.get('id', 'No ID')
        cc_recipients = thread.get('ccRecipients', [])
        bcc_recipients = thread.get('bccRecipients', [])

        if not thread_body.strip():
            continue

        cc_addresses = ', '.join([recipient.get('emailAddress', {}).get('address', '') for recipient in cc_recipients])
        bcc_addresses = ', '.join([recipient.get('emailAddress', {}).get('address', '') for recipient in bcc_recipients])
        
        if thread_content_type == 'html':
            h = html2text.HTML2Text()
            h.ignore_links = True
            h.ignore_images = True
            h.ignore_tables = True
            h.ignore_emphasis = True
            h.single_line_break = True
            h.body_width = 0
            text = h.handle(thread_body)
            thread_body = text.strip()
        
        formatted_thread_content = {
            "EmailId": thread_id,
            "ConversationId": conversation_id,
            "Subject": thread_subject,
            "From": thread_from_address,
            "CC": cc_addresses if cc_addresses else '',
            "BCC": bcc_addresses if bcc_addresses else '',
            "ReceivedDateTime": received_date_time,
            "AttachmentNames": "",
            "Body": thread_body
        }

        last_json = formatted_thread_content
        thread_contents.append(formatted_thread_content)

    return thread_contents, received_date_time, last_json, attachment_names_all


def save_email_to_html(emails, output_file):
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("<html><body>\n")
        for email in emails:
            subject = email.get('subject', '')
            from_address = email.get('from', {}).get('emailAddress', {}).get('address', '')
            body = email.get('body', {}).get('content', '')
            received_date = email.get('receivedDateTime', '')
            conversation_id = email.get('conversationId', '')

            f.write(f"<h3>Conversation ID: {conversation_id}</h3>\n")
            f.write(f"<h3>Subject: {subject}</h3>\n")
            f.write(f"<p>From: {from_address}</p>\n")
            f.write(f"<p>Received Date: {received_date}</p>\n")
            f.write(body)
            f.write("<hr>\n")

        f.write("</body></html>\n")

def extract_main_email_body(body_text):

    from_pattern = re.compile(r'\n+From: ', re.MULTILINE)
    from_pattern_2nd = re.compile(r'From: ', re.MULTILINE)
    reply_pattern = re.compile(r'(?:On .+? wrote:|From: .+? Sent: .+? To: .+? Subject: .+? Body Text:)', re.DOTALL)
    footer_pattern = re.compile(r'--\s*\n$', re.MULTILINE)
    from_start_pattern = re.compile(r'^From: ', re.MULTILINE)

    from_match = from_pattern.search(body_text)
    from_pattern_2nd_match = from_pattern_2nd.search(body_text)
    reply_match = reply_pattern.search(body_text)
    footer_match = footer_pattern.search(body_text)
    from_start_match = from_start_pattern.search(body_text)

    earliest_match = None

    if from_match:
        earliest_match = from_match
    if from_pattern_2nd_match and (earliest_match is None or from_pattern_2nd_match.start() < earliest_match.start()):
        earliest_match = from_pattern_2nd_match
    if reply_match and (earliest_match is None or reply_match.start() < earliest_match.start()):
        earliest_match = reply_match
    if footer_match and (earliest_match is None or footer_match.start() < earliest_match.start()):
        earliest_match = footer_match
    if from_start_match and (earliest_match is None or from_start_match.start() < earliest_match.start()):
        earliest_match = from_start_match

    if earliest_match:
        main_email_body = body_text[:earliest_match.start()].strip()
    else:
        main_email_body = body_text.strip()

    main_email_body = re.sub(r'\n+From:.*$', '', main_email_body, flags=re.DOTALL).strip()
    main_email_body = re.sub(r'(?:--|Sent:|From:|On .+? wrote:).*$', '', main_email_body, flags=re.DOTALL).strip()

    return main_email_body