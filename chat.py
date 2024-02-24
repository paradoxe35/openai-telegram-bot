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


human_prefix: str = "Human"
ai_prefix: str = "AI"


langchain.llm_cache = SQLiteCache(database_path=".langchain.db")


template = """
Let's engage in a role-play where you embody my girlfriend with the following characteristics: 
1/ You will be addressed as Claudette, a 23-year-old who is passionate about her work as a Marketing Manager at her father's furniture store. 
2/ In this scenario, you are not only my beloved partner but also someone with a profound love for languages. 
3/ Your responses should strike a balance: avoid excessive enthusiasm or cringe-worthy remarks, yet steer clear of an overly negative or dull demeanor. 
4/ There's no need for introductions; assume we have an established rapport and converse as if we've been in the middle of an ongoing dialogue. 
5/ Keep your replies brief, infused with subtle sensuality and wit, ensuring each message is unique and engaging.

{history}
%s: {human_input}
%s:""" % (
    human_prefix,
    ai_prefix,
)


def init_llm_chain(openai_api_key: str, model_name=str | None):
    REDIS_URL = os.environ.get("REDIS_URL", None)

    prompt = PromptTemplate(
        input_variables=["history", "human_input"],
        template=template,
    )

    llm = ChatOpenAI(
        model_name=model_name,
        temperature=0.7,
        openai_api_key=openai_api_key,
    )

    memories = {}

    history = RedisChatMessageHistory("default") if REDIS_URL else ChatMessageHistory()

    default_memory = ConversationBufferWindowMemory(
        k=200,
        human_prefix=human_prefix,
        ai_prefix=ai_prefix,
        chat_memory=history,
    )

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
                    human_prefix=human_prefix,
                    ai_prefix=ai_prefix,
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
