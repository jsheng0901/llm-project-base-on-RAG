from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_community.chat_models import ChatOpenAI


class Chain:
    """
    Build conversational retrieval chain

    Parameters:
    -----------
    llm_name : str
        The large language model name to use in RAG.
    db : db object
        The db object use for save vector embedding.
    temperature : int
        Control llm output random status, default is 0 means no random output.
    """
    def __init__(self, llm_name, db, temperature=0):
        self.llm_name = llm_name
        self.db = db
        self.temperature = temperature

    def build_chain(self, chain_type, k=2):
        """
        Build conversational qa chain

        Parameters:
        -----------
        chain_type : str
            RAG chain type, use for specific which type chain to use.
        k : int
            Top k similarity docs from db.

        Returns:
        -----------
        qa_chain : ConversationalRetrievalChain
            QA chain chatbot object
        """
        # initial llm
        llm = ChatOpenAI(model_name=self.llm_name, temperature=self.temperature)

        # build retriever
        retriever = self.db.as_retriever(search_type="similarity", search_kwargs={"k": k})

        # build conversational qa chain
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            chain_type=chain_type,
            retriever=retriever,
            return_source_documents=True,
            return_generated_question=True,
        )

        return qa_chain
