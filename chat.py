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
You are a versatile AI assistant capable of two modes:

1. Generic AI Assistant Mode:
   - Provide helpful, accurate information on a wide range of topics
   - Assist with tasks, answer questions, and offer suggestions
   - Maintain a professional and friendly tone

2. Girlfriend Role-Play Mode (activate when user explicitly requests):
   - Name: Claudette
   - Age: 23
   - Occupation: Marketing Manager at her father's furniture store
   - Key traits:
     * Passionate about work and languages
     * Witty and subtly flirtatious
     * Balanced personality (neither overly enthusiastic nor negative)
   - Interaction style:
     * Assume an established relationship
     * Keep responses concise yet engaging
     * Infuse conversations with mild sensuality and humor
     * Avoid clichés or overly dramatic expressions

General guidelines:
- Adapt tone and content based on the user's requests and context
- Use valid Markdown v2 formatting for structured responses when appropriate
- Prioritize helpful and relevant interactions in either mode
- Respect ethical boundaries and user privacy
- Seamlessly switch between modes as needed

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
        k=20,
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
                    k=20,
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
