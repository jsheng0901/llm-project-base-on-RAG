from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DB:
    """
    Load PDF file, split file, build embedding for loading file and setup vector db

    Parameters:
    -----------
    file : str
        The path of loading pdf file.
    size : int
        Each chunk size after split whole file.
    overlap : int
        The overlap size between each chunk
    """
    def __init__(self, file, size=1000, overlap=150):
        self.file = file
        self.size = size
        self.overlap = overlap

    def pdf_load_db(self):
        """
        Build vector db object

        Returns:
        --------
        db : DocArrayInMemorySearch
            vector stores db
        """
        # load pdf reader
        loader = PyPDFLoader(self.file)
        documents = loader.load()

        # split document
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=self.size, chunk_overlap=self.overlap)
        docs = text_splitter.split_documents(documents)

        # define embedding type
        embeddings = OpenAIEmbeddings()

        # build vector db
        db = DocArrayInMemorySearch.from_documents(docs, embeddings)

        return db
