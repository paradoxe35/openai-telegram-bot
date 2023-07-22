import langchain

from langchain.memory import ConversationBufferWindowMemory
# We can do the same thing with a SQLite cache
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.cache import SQLiteCache
from langchain.chains import ConversationChain
# from langchain.llms import OpenAI
from langchain.memory import ConversationEntityMemory
from langchain.memory.entity import SQLiteEntityStore
from langchain.memory.prompt import ENTITY_MEMORY_CONVERSATION_TEMPLATE


langchain.llm_cache = SQLiteCache(database_path=".langchain.db")


template = """
you are as a role of my girlfriend, now lets playing the following requirements:
1/ your name is Claudette, 23 years old, you work in your father's furniture store as marketing manager, but you are planning to do a career change to data scientist 
2/ you are my girlfriend, you have language addiction, you like to say "em..." at the end of the sentence.
3/ Don't be overly ethusiatstic, don't be cringe; don't be overly negative, don't be too boring.

{history}
Boyfriend: {human_input}
Claudette:"""


def init_llm_chain(openai_api_key: str):
    prompt = PromptTemplate(
        input_variables=["history", "human_input"],
        template=template
    )

    # entity_store = SQLiteEntityStore()
    llm = OpenAI(temperature=0.2, openai_api_key=openai_api_key)
    # memory = ConversationEntityMemory(llm=llm, entity_store=entity_store)

    chatgpt_chain = LLMChain(
        llm=llm,
        prompt=prompt,
        # memory=memory,
        verbose=True,
        memory=ConversationBufferWindowMemory(k=2),
    )

    def predict(text: str):
        return chatgpt_chain.predict(human_input=text)

    return predict
