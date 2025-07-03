from openai import OpenAI
import re
from email_ingestion.config.Config import config

llm_url = config.LLM_URL
llm_model = config.LLM_MODEL


def generate_meddpicc_tags_for_chunks(text):

    tags = [
        "metrics",
        "economic-buyer",
        "decision-criteria",
        "decision-process",
        "paper-process",
        "identified-pain",
        "champion",
        "competition",
    ]

    tags_string = "[" + ",".join(tags) + "]"

    client = OpenAI(base_url=llm_url, api_key=config.API_KEY)
    template = f"""You are an experienced sales representative for emumba. You will receive relevant snippets from conversations between emumba and their client, where emumba is trying to sell their product. 
    
    Here are typical challenges emumba attempts to solve for its clients:

    Challenges Addressed by emumba
        1. Complexity of Multi-Cloud Networking: emumba simplifies the management of networking across multiple cloud platforms, reducing integration challenges.
        2. Lack of Visibility and Control: The platform provides comprehensive visibility and control over network operations, addressing the "black box" issue in cloud environments.
        3. Inefficient Cost Structures: emumba helps organizations optimize cloud networking expenses by offering insights into data transfer costs and resource management.
        4. Security and Compliance Risks: It enhances security by implementing dynamic policies across cloud environments, ensuring compliance and protection against threats.
        5.Operational Silos: The solution integrates with existing tools, facilitating collaboration and breaking down operational silos within organizations.
        6. Integration with Existing Toolsets: emumba allows for seamless integration with established workflows, enabling teams to leverage current investments alongside new capabilities.
        7.Performance and Latency Issues: The platform optimizes network performance by strategically placing applications closer to users, improving response times.
        8. Dynamic Network Policies: emumba enables consistent management of dynamic network policies across multiple cloud platforms, allowing for agile business responses.
        9. Limited Granularity in Data Management: It restores granularity in data flows, providing detailed insights and control over data management in cloud environments.
        10. Management of Diverse Cloud Providers: emumba offers a unified approach to managing networking across various cloud providers, simplifying operations and enhancing efficiency.

    Some of these emails are from the initial phase when the company began engaging with the client, and some from later stages after the client is using the company's services. Your job is to assign one or more tags to the email snippet you receive based on what you think it represents. You MUST ONLY assign tags from the MEDDPICC sales strategy, which are: {tags_string}. It is essential to follow the MEDDPICC framework when tagging the snippets. 
    Here are examples of what each tag represents:
    - **metrics**: Quantifiable goals that customer aims to achieve
    - **economic-buyer**: The person with the authority to make purchasing decisions and approve budgets.
    - **decision-criteria**: The standards the client uses to make their decision
    - **decision-process**: Steps the client follows to make a purchase decision
    - **paper-process**: Formal steps required to complete the transaction including contracts or legal review
    - **identified-pain**: Specific business problems or challenges the client is facing
    - **champion**: References to an internal advocate for the product within the client's organization
    - **competition**: Mentions of competitors or alternative solutions
    - **other**: If the snippet doesn't match any of the given tags, assign 'other' to it. 

    You MUST assign at least one tag to the email snippet. Assign the tag only from the list of tags provided. Also give a reason for assigning each tag. Follow the yaml format for the final answer. For example the format for returning the tag should be like the following:
    tag: ['tag1', 'tag2']
    
    Perform this task for the following email snippet: {text}
    """

    completion = client.chat.completions.create(
        model=llm_model,
        messages=[{"role": "user", "content": template}],
        temperature=0.1,
        top_p=0.1,
    )

    text = completion.choices[0].message.content.strip()

    match = re.search(r"\[(.*?)\]", text)

    if match:
        text = match.group(1)
        tags = [tag.strip().strip("'") for tag in text.split(",")]

        return tags

    else:
        return []
