import os
import sys
import pinecone
from pinecone import Pinecone, ServerlessSpec
from langchain.llms import Replicate
from langchain.vectorstores import Pinecone
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import PyPDFLoader
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.chains import ConversationalRetrievalChain

# Replicate API token
REPLICATE_API_TOKEN = 'r8_DuJ1PJxoCp37iVhMKkbXNVcAdPBNmUP0rcosH'

# Initialize Pinecone
pc = Pinecone(api_key = '36982985-b107-446b-9c2e-1ca654b64efd')
pc.create_index(
    name="quickstart",
    dimension=768,
    metric="euclidean",
    spec=ServerlessSpec(
        cloud='aws', 
        region='us-west-2'
    ) 
) 

# load and preprocess the PDF document
loader = PyPDFLoader('air_quality_index_prediction_paper_3.pdf')

documents = loader.load()

# Split the documents into smaller chunks for processing
text_splitter = CharacterTextSplitter(chunk_size = 1000, chunk_overlap = 0)
texts = text_splitter.split_documents(documents)

# use huggingface embeddings for transforming text inot numerical vectors
embeddings = HuggingFaceEmbeddings()

# setting up the pinecone vector database
# index_name = "resumeanalyzer"
# index = pc.Index(index_name)
index = pc.Index("quickstart")
vectordb = pc.from_documents(texts, embeddings, index_name = 'quickstart')

# Initialize Replicate Llama2 Model
llm = Replicate(
    model="a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5",
    input={"temperature": 0.75, "max_length": 3000}
)

# set up the conversational retrieval chain
qa_chain = ConversationalRetrievalChain.from_llm(llm, vectordb.as_retriever(search_kwargs = {'k' : 2}),return_source_documents = True)

# main code
chat_history = []
while True:
    query = input("Prompt: ")
    if query.lower() in ['exit', 'quit', 'q']:
        print('Exciting')
        sys.exit()
    result = qa_chain({'question': query, 'chat_history': chat_history})
    print('Answer: ' + result['answer'] + '\n')
    chat_history.append((query, result['answer']))