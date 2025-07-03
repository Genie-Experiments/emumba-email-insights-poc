from openai import OpenAI
from config.Config import config
from config.LoggingConfig import logger
import tiktoken


def count_tokens(text: str) -> int:
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def get_final_answer(all_text, main_question, company):
    logger.info(f"Main Question: {main_question}")
    client = OpenAI(base_url=config.LLM_URL, api_key=config.API_KEY, timeout=900)

    template = f"""You have been provided with a set of email conversation between emumba and {company}. Your task is to generate a thorough and accurate answer to the main question based strictly on the provided information.

    Instructions:
    1. Only include relevant information from the provided text. Do not add any additional content or personal interpretations.
    2. The response should be directly related to the main question and must include all pertinent details from the provided text.
    3. Maintain a consistent and clear format in your response.
    4. Avoid introducing any randomness or deviation in your answer.
    5. Do not include the question in the final answer.
    6. Add as much detail as possible. Make the response well formatted using bullet points. Make the headings text bold without any additional formatting to the text.
    7. Do not infer anything from your own understanding. Keep the context relevant to the information that is being provided to you.
    8. Make sure all the technical details are shared in the final response. Make sure the technical jargons are kept in final response along with all the relevant contextual information.
    9. Make sure the response includes context relevant to {company} only. If there's mention of any other company and its relevant to the main question make sure you add reference to why it is relevant to {company}.
    10. Make the final response as detailed as possible.
    Main Question: {main_question}.
    Information: {all_text}.
    Generate the answer strictly following the instructions above."""

    messages = [{"role": "user", "content": template}]

    logger.info(f"Final response template: {template}")
    logger.info(f"Context length {count_tokens(template)}")

    completion = client.chat.completions.create(
        model=config.LLM_MODEL, messages=messages, temperature=0.1, top_p=0.1
    )
    return completion.choices[0].message.content.strip()
