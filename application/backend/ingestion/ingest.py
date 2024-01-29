from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_community.document_loaders import OneDriveLoader
from unstructured.cleaners.core import clean_extra_whitespace
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from langchain_community.vectorstores import Weaviate
import tiktoken
import os

os.environ['O365_CLIENT_ID']
os.environ['O365_CLIENT_SECRET']
os.environ["OPENAI_API_KEY"]

tokenizer = tiktoken.get_encoding('cl100k_base')
def tiktoken_len(text):
    tokens = tokenizer.encode(
          text,
          disallowed_special=()
    )
    return len(tokens)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=20,
    length_function=tiktoken_len,
    separators=["\n\n", "\n", " ", ""]
)

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

#check parent folder modified_date every 24h

loader = OneDriveLoader(drive_id="", folder_path="", auth_with_token=True)
fetched_docs = loader.load()

# Check how many docs + Check if loading works for pdf, word, ppt

documents = []

for doc in fetched_docs:
        doc_loader = UnstructuredFileLoader(doc, mode="elements", post_processors=[clean_extra_whitespace])
        docs = doc_loader.load()
        metadata = docs.metadata

        chunks = text_splitter.split_text(docs.page_content)

        for i, chunk in enumerate(chunks):
            documents.append(Document(
                page_content=chunk,
                metadata={
                    "filename": metadata["filename"] + "_" + str(i),
                    "file_directory": metadata["file_directory"],
                    "language": metadata['languages']
                }
            ))

#for ppt, chunks only per page
#pdfs => check how tables are handled

vectorstore = Weaviate.from_documents(
    documents, embeddings, weaviate_url=""
)
