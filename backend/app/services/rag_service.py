import nltk
import asyncio

from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.embeddings.text_embeddings_inference import TextEmbeddingsInference

from services.rag_final_answer import get_final_answer
from utils.s3_utils import (
    get_attachments_from_s3,
    get_email_references,
    get_email_text_by_id,
)
from utils.query_utils import filter_nodes, get_db_table

# configs
from config.VectorStore import VectorStoreSingleton
from config.LoggingConfig import logger
from config.Config import config
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

nltk.download("punkt")


class RAGService:

    IGNORE_SENTENCES = [
        "For security purposes and other lawful business purposes, PwC monitors outgoing and incoming emails and may monitor other telecommunications on its email and telecommunications systems.PricewaterhouseCoopers IT Services (US) LLC is a Delaware limited liability company.",
        "If you received this in error, please contact the sender and delete the material from any computer and destroy any copies.If the content of this email includes tax advice, the advice is limited to the matters specifically addressed herein and is not intended to address other potential tax consequences or the potential application of tax penalties.PwC refers to one or more US member firms of the PwC network.",
        "For security purposes and other lawful business purposes, PwC monitors outgoing and incoming emails and may monitor other telecommunications on its email and telecommunications systems.----------------------------------------------------------------Visit our website http://www.pwc.com/uk and see our privacy statement for details of why and how we use personal data and your rights (including your right to object and to stop receiving direct marketing from us).----------------------------------------------------------------",
        "In the event the content of this email includes Tax advice, the content of this email is limited to the matters specifically addressed herein and is not intended to address other potential tax consequences or the potential application of tax penalties to this or any other matter.PricewaterhouseCoopers LLP is a Delaware limited liability partnership.",
        "In the event the content of this email includes Tax advice, the content of this email is limited to the matters specifically addressed herein and is not intended to address other potential tax consequences or the potential application of tax penalties to this or any other matter.PricewaterhouseCoopers LLP is a Delaware limited liability partnership.",
    ]

    CONTRIBUTION_THRESHOLD = 0.20




    def __init__(self):
        # Initialize embedding model and LLM
        self.embed_model = OpenAIEmbedding(api_key=config.API_KEY, model_name=config.EMBEDDING_MODEL)
        Settings.embed_model = self.embed_model
        Settings.llm = OpenAI(
            base_url=config.LLM_URL,
            model=config.LLM_MODEL,
            api_key=config.API_KEY
        )

    async def generate_answer(self, question, db_table, filters, top_k):
        # Use async methods for any external calls (like VectorStoreIndex)
        vector_store = VectorStoreSingleton.get_instance(db_table)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
        query_engine = index.as_retriever(similarity_top_k=top_k)

        response = query_engine.retrieve(question)
        filtered_nodes = filter_nodes(response, filter_tags=filters)

        return filtered_nodes

    async def generate_answer_attachments(self, question, filters, table_name):
        vector_store = VectorStoreSingleton.get_instance(table_name)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
        query_engine = index.as_retriever(similarity_top_k=5)

        response = query_engine.retrieve(question)
        filtered_nodes = filter_nodes(response, filter_tags=filters)

        return filtered_nodes

    async def get_response(
        self, main_question, company, sub_questions_from_request, db
    ):
        email_table, attachment_table, s3_prefix = get_db_table(company=company, db=db)
        logger.info(
            f"Processing company: {company}, Email Table: {email_table}, Attachments Table: {attachment_table}."
        )
        logger.info(f"Processing subquestions....")
        all_filtered_nodes, all_filtered_nodes_attachments = (
            await self.process_sub_questions(
                sub_questions_from_request, email_table, attachment_table
            )
        )

        unique_nodes, unique_attachment_nodes, email_ids, unique_attachment_names = (
            self.deduplicate_nodes(all_filtered_nodes, all_filtered_nodes_attachments)
        )
        logger.info(f"Filtered Email Nodes: {len(unique_nodes)}")
        logger.info(f"Filtered Attachment Nodes: {len(unique_attachment_nodes)}")

        all_text = self.concat_node_text(unique_nodes, unique_attachment_nodes)
        final_response = get_final_answer(all_text, main_question, company)
        logger.info(f"Received response from LLM.... Getting context references....")
        formatted_emails = await get_email_references(email_ids, company=s3_prefix)
        email_contributions = await self.get_email_contributions(
            unique_nodes, final_response, formatted_emails, company, db
        )

        email_contributions_attachments = await self.get_attachment_contributions(
            unique_attachment_nodes,
            final_response,
            company,
            unique_attachment_names,
            db=db,
        )
        return (
            final_response,
            email_contributions,
            email_contributions_attachments,
        )

    async def process_sub_questions(self, sub_questions, email_table, attachment_table):
        tasks = []
        attachment_tasks = []
        unique_tags = {}

        for idx, sub_question in enumerate(sub_questions, start=1):
            logger.info(f"Sub-Question: {sub_question.question}")
            question, tags = sub_question.question, [
                tag.value for tag in sub_question.tags
            ]
            unique_tags[question] = set(tags)
            tasks.append(
                self.generate_answer(
                    question, db_table=email_table, top_k=15, filters=tags
                )
            )
            attachment_tasks.append(
                self.generate_answer_attachments(
                    question, tags, table_name=attachment_table
                )
            )

        filtered_nodes = await asyncio.gather(*tasks)
        filtered_attachments = await asyncio.gather(*attachment_tasks)

        all_filtered_nodes = [node for sublist in filtered_nodes for node in sublist]
        all_filtered_nodes_attachments = [
            node for sublist in filtered_attachments for node in sublist
        ]

        return all_filtered_nodes, all_filtered_nodes_attachments

    def deduplicate_nodes(self, all_filtered_nodes, all_filtered_nodes_attachments):
        unique_nodes = {}
        unique_attachment_nodes = {}
        email_ids = []
        unique_attachment_names = set()
        logger.info(f"Filtering nodes....")
        # Deduplication for emails
        for node_with_score in all_filtered_nodes:
            node_id = node_with_score.node.node_id
            if node_id not in unique_nodes:
                unique_nodes[node_id] = node_with_score
            email_id = node_with_score.node.metadata.get("EmailID")
            if email_id:
                email_ids.append(email_id)

        # Deduplication for attachments
        for node_with_score in all_filtered_nodes_attachments:
            node_id = node_with_score.node.node_id
            logger.info(f"Filtering Attachments for Node ID: {node_id}")
            if node_id not in unique_attachment_nodes:
                unique_attachment_nodes[node_id] = node_with_score
            attachment_name = node_with_score.node.metadata.get("AttachmentName")
            logger.info(f"Node metadata: {node_with_score.node.metadata}")
            logger.info(f"Attachment Name: {attachment_name}")
            if attachment_name:
                unique_attachment_names.add(attachment_name)

        return unique_nodes, unique_attachment_nodes, email_ids, unique_attachment_names

    def concat_node_text(self, unique_nodes, unique_attachment_nodes):
        return (
            "\n".join(node.node.text for node in unique_nodes.values())
            + "\n"
            + "\n".join(node.node.text for node in unique_attachment_nodes.values())
        )

    async def get_email_contributions(
        self, unique_nodes, final_response, formatted_emails, company, db
    ):
        tasks = []
        email_ids_seen = set()
        logger.info(f"Getting email references contribution scores....")
        for node in unique_nodes.values():
            tasks.append(
                self.process_email_node(
                    node, final_response, company, email_ids_seen, formatted_emails, db
                )
            )

        email_contributions = await asyncio.gather(*tasks)
        return list(filter(None, email_contributions))

    async def process_email_node(
        self, node, final_response, company, email_ids_seen, formatted_emails, db
    ):
        email_id = node.node.metadata.get("EmailID")

        filtered_email = next(
            (email for email in formatted_emails if email["EmailID"] == email_id), None
        )
        body_text = await get_email_text_by_id(email_id, company, db)
        if not body_text or email_id in email_ids_seen:
            return None

        sentences = self.filter_sentences(body_text)
        top_sentences = self.get_top_similar_sentences(final_response, sentences)
        if top_sentences:
            email_ids_seen.add(email_id)
            return {
                "email_id": filtered_email.get("EmailID"),
                "Subject": filtered_email.get("Subject"),
                "From": filtered_email.get("From"),
                "Date": filtered_email.get("Date"),
                "To": filtered_email.get("To"),
                "highlighted_text": self.highlight_text(body_text, top_sentences),
                "CC": (
                    node.node.metadata.get("CC", "").split(",")
                    if node.node.metadata.get("CC")
                    else []
                ),
                "BCC": (
                    node.node.metadata.get("BCC", "").split(",")
                    if node.node.metadata.get("BCC")
                    else []
                ),
                "contribution_score": max(
                    self.similarity_scores(final_response, sentences)
                ),
            }

    async def get_attachment_contributions(
        self,
        unique_attachment_nodes,
        final_response,
        company,
        unique_attachment_names,
        db,
    ):
        tasks = []
        logger.info(f"Getting attachments from s3 for {unique_attachment_names}")
        s3_links = await get_attachments_from_s3(
            unique_attachment_names, company, db=db
        )
        logger.info(f"Retrieved {len(s3_links)} reference attachments")
        logger.info(f"S3 Links: {s3_links}")

        for node in unique_attachment_nodes.values():
            tasks.append(self.process_attachment_node(node, final_response, s3_links))

        return list(filter(None, await asyncio.gather(*tasks)))

    async def process_attachment_node(self, node, final_response, s3_links):
        attachment_name = node.node.metadata.get("AttachmentName")
        attachment_text = node.node.text
        sentences = self.filter_sentences(attachment_text)

        top_sentences = self.get_top_similar_sentences(final_response, sentences)
        if top_sentences:
            s3_link = next(
                (url for name, url in s3_links if name == attachment_name), None
            )
            return {
                "attachment_name": attachment_name,
                "attachment_text": attachment_text,
                "s3_link": s3_link,
                "contribution_score": max(
                    self.similarity_scores(final_response, sentences)
                ),
            }

    def filter_sentences(self, text):
        sentences = sent_tokenize(text)
        return [
            sentence for sentence in sentences if sentence not in self.IGNORE_SENTENCES
        ]

    def get_top_similar_sentences(self, reference_text, sentences):
        vectorizer = TfidfVectorizer().fit_transform([reference_text] + sentences)
        vectors = vectorizer.toarray()
        final_vector = vectors[0]
        similarities = cosine_similarity([final_vector], vectors[1:])[0]
        top_indices = similarities.argsort()[-5:][::-1]
        return [
            sentences[idx]
            for idx in top_indices
            if similarities[idx] >= self.CONTRIBUTION_THRESHOLD
        ]

    def similarity_scores(self, reference_text, sentences):
        vectorizer = TfidfVectorizer().fit_transform([reference_text] + sentences)
        vectors = vectorizer.toarray()
        final_vector = vectors[0]
        return cosine_similarity([final_vector], vectors[1:])[0]

    def highlight_text(self, text, sentences_to_highlight):
        for sentence in sentences_to_highlight:
            text = text.replace(sentence, f"<mark>{sentence}</mark>")
        return text
