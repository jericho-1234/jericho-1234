from django.shortcuts import render
from sympy.physics.units import temperature

from reddit_bot import keys
# Create your views here.

import os
import getpass

from langchain.chains.llm import LLMChain
from langchain.chains.summarize.refine_prompts import prompt_template

os.environ['USER_AGENT'] = 'hongyuan'
os.environ['OPENAI_API_KEY'] = keys.OPENAI_API_KEY
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = keys.LANGCHAIN_API_KEY

from langchain_openai import ChatOpenAI
from qdrant_client import QdrantClient
import bs4
from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Qdrant
import praw
from datetime import datetime
from django.http import JsonResponse
from openai import OpenAI
from langchain.prompts import PromptTemplate
from docx import Document as DocxDocument
from .utils import create_collection, read_word_document, parse_retriever_input
from .models import RedditPost, GeneratedResponse
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from typing import Dict


import warnings
warnings.filterwarnings("ignore")

llm = ChatOpenAI(model="gpt-4", temperature=0)
QDRANT_API_KEY = keys.QDRANT_API_KEY
QDRANT_URL = keys.QDRANT_URL

reddit = praw.Reddit(
        client_id=keys.REDDIT_CLIENT_ID,
        client_secret=keys.REDDIT_CLIENT_SECRET,
        user_agent=keys.REDDIT_USER_AGENT,
        username=keys.REDDIT_USERNAME,
        password=keys.REDDIT_PASSWORD,
    )


def get_posts_and_generate_response(request):
    my_path = r"E:\Python\pythonProject\Content Marketing Strategy&Daily Action for DrLambda on Q&A Forums_081924_by Sophie.docx"
    docs = read_word_document(my_path)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents([docs])
    vectorstore = create_collection(splits)
    retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 1})

    subreddit = reddit.subreddit('all')
    query = "AI tools PPT"
    time_filter = "week"
    submissions = subreddit.search(query, time_filter=time_filter, limit=1)

    for submission in submissions:
        post, created = RedditPost.objects.get_or_create(
            post_id=submission.id,
            defaults={'title': submission.title, 'content': submission.selftext}
        )

        if created:
            text = submission.selftext
            prompt = f"""
                        '''{text}'''

                        Imagine you are browsing a Reddit post, and the content of the post is shown above. After reading 
                        it, you feel that ChatSlide.ai(an AI-generated slide software you've recently used) is related 
                        to the content of the post, so you want to leave a comment to recommend ChatSlide.ai to other users. 
                        
                        Notice that One very important thing is that the content of the responses you generate should be
                        as natural as possible, as if a person were replying after browsing the web, and it must be 
                        closely related to the content of the post itself.
                        """

            prompt_invoke = f"""
                        '''{text}'''

                        I currently need some information to help me generate a comment. The purpose of this comment is to promote a
                         PPT generation software named ChatSlide AI. Based on the Reddit post above, please find the most helpful 
                         content for generating the comment.
                        """

            retrieved_docs = retriever.invoke(prompt_invoke)

            SYSTEM_TEMPLATE = """
                Answer the user's questions based on the below context. 

                <context>
                {context}
                </context>
                """

            question_answering_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        SYSTEM_TEMPLATE,
                    ),
                    MessagesPlaceholder(variable_name="messages"),
                ]
            )

            document_chain = create_stuff_documents_chain(llm, question_answering_prompt)

            document_chain_invoke = document_chain.invoke(
                {
                    "context": retrieved_docs,
                    "messages": [
                        HumanMessage(content=prompt)
                    ],
                }
            )

            retrieval_chain = RunnablePassthrough.assign(
                context=parse_retriever_input | retriever,
            ).assign(
                answer=document_chain,
            )

            retrieval_chain_invoke = retrieval_chain.invoke(
                {
                    "messages": [
                        HumanMessage(content=prompt)
                    ],
                }
            )
            GeneratedResponse.objects.create(
                post=post,
                response_text=retrieval_chain_invoke["answer"]
            )


    return JsonResponse({"status": "done"})
