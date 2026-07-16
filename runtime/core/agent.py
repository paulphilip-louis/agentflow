import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import (BaseMessage, HumanMessage, AIMessage, SystemMessage)
from langchain.agents import create_agent
from langchain_core.callbacks import BaseCallbackHandler
from runtime.core.app import Calendar, DocumentStore

load_dotenv()

MODEL_NAME = "gpt-4o-mini"
SYSTEM_PROMPT = """You are an assistant that processes documents.
                Use the available tools to complete the user's request.
                All document names are self-explanatory.
                Always start by listing them to identify the exact names to retrieve
                Always retrieve all necessary documents before performing any action.
                NB: Emails are stored as documents.
                """

def create_env_agent(env):
    print("Loading model")
    llm = ChatOpenAI(model=MODEL_NAME, temperature=0, api_key=os.getenv("OPENAI_API_KEY"))
    tools = env.tools
    
    return create_agent(llm, tools, system_prompt=SYSTEM_PROMPT)