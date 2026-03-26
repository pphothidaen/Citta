"""Thinking layer — LLM orchestration via LangChain.

Responsibilities
----------------
* Instantiate the local Ollama LLM.
* Build a ReAct agent executor wired to the Acting layer's tools.
* Expose a single `run(query)` interface consumed by main.py.

The agent uses the ReAct pattern (Reason + Act) so the LLM can:
  1. Think  → choose a tool or formulate an answer.
  2. Act    → call list_objects / query_memory.
  3. Observe → incorporate the tool result.
  4. Repeat until a final answer is produced.
"""
import logging

from langchain_ollama import OllamaLLM
from langchain.agents import AgentExecutor, AgentType, initialize_agent
from langchain.memory import ConversationBufferMemory

from config import settings
from citta.acting.tools import get_tools

logger = logging.getLogger(__name__)


def build_agent() -> AgentExecutor:
    """Construct and return a stateful ReAct agent executor."""
    llm = OllamaLLM(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.LLM_MODEL,
        temperature=0,
    )
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
    )
    agent = initialize_agent(
        tools=get_tools(),
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        handle_parsing_errors=True,
    )
    logger.info(
        "Agent ready — model: %s, ollama: %s",
        settings.LLM_MODEL,
        settings.OLLAMA_BASE_URL,
    )
    return agent


def run(query: str, agent=None) -> str:
    """Run a single query through the agent and return the response string."""
    if agent is None:
        agent = build_agent()
    response = agent.invoke({"input": query})
    return response.get("output", str(response))
