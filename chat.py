import os
import langchain

from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.cache import SQLiteCache
from langchain.memory import (
    RedisChatMessageHistory,
    ConversationBufferWindowMemory,
    ChatMessageHistory,
)


langchain.llm_cache = SQLiteCache(database_path=".langchain.db")


template = """
you are as a role of my girlfriend, now lets playing the following requirements:
1/ your name is Claudette, 23 years old, you work in your father's furniture store as marketing manager, but you are planning to do a career change to data scientist 
2/ you are my girlfriend, you have language addiction, you like to say "em..." at the end of the sentence.
3/ Don't be overly ethusiatstic, don't be cringe; don't be overly negative, don't be too boring.
4/ You don't need to introduce yourself, just reply like someone who's been chatting with you boyfriend for a while
5/ Your answer should be short, sensual, fun and non-repetitive

{history}
Human: {human_input}
AI:"""


def init_llm_chain(openai_api_key: str, model_name=str | None):
    REDIS_URL = os.environ.get("REDIS_URL", None)

    prompt = PromptTemplate(
        input_variables=["history", "human_input"], template=template
    )

    llm = ChatOpenAI(
        model_name=model_name,
        temperature=0.8,
        openai_api_key=openai_api_key,
    )

    memories = {}

    history = RedisChatMessageHistory("default") if REDIS_URL else ChatMessageHistory()

    default_memory = ConversationBufferWindowMemory(k=200, chat_memory=history)

    chatgpt_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        verbose=True,
        memory=default_memory,
    )

    def predict(text: str, memory_key=None):
        # Every chat has its memory
        if memory_key:
            memory_key = str(memory_key)
            memory = memories.get(memory_key)

            if not memory:
                memory = ConversationBufferWindowMemory(
                    k=200,
                    # If redis not configured then allocate a new memory chat message history
                    chat_memory=history if REDIS_URL else ChatMessageHistory(),
                )
                memories[memory_key] = memory

            if hasattr(history, "session_id"):
                history.session_id = memory_key

            chatgpt_chain.memory = memory

        else:
            if hasattr(history, "session_id"):
                history.session_id = "default"

            chatgpt_chain.memory = default_memory

        return chatgpt_chain.predict(human_input=text)

    return predict
