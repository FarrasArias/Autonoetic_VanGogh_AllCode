import os
import faiss
import pickle
import pandas as pd
import numpy as np

from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS

from colorama import init, Fore

init()

class EmbedderOpenAI:
    """Encodes text into embeddings using OpenAI and allows embedding search."""

    def __init__(self, encoder_name, series, index_name, api_key):
        """Initializes the EmbedderOpenAI.

        Args:
            api_key: Your OpenAI API key.
            index_name: The name for the embedding index.
        """
        self._embeddings = OpenAIEmbeddings(model=encoder_name, openai_api_key=api_key)
        self._series = series
        self._index = None
        self._index_w_chat = None
        self._index_name = index_name
        self._index_dir = f"{index_name}_openai_index"
        self._load_index()
        
    def _convert_strings_to_docs(self, text_list):
        documents = [Document(page_content=text) for text in text_list]
        return documents

    def create_embeddings(self, series, force=False):
        """Creates embeddings for the given text data.

        Args:
            series:  The filepath to a text file containing text data.
            force: If True, forces re-creation of embeddings even if an index exists.
        """
        if self._index is None or force:
            vectors = self._encode(series)
            self._index = self._create_vector_space(vectors)
            #self._index_w_chat = self._create_vector_space(vectors) ###
            ## for now, we must stop and re-run.
            self._save_index()
            self._load_index()

    def _encode(self, series):
        """Encodes text data into embeddings using OpenAI.

        Args:
            series: A list of text chunks, the filepath to a text file, 
                    or a Pandas Series.

        Returns:
            A Faiss index of embeddings.
        """
        if isinstance(series, str):  # Check if series is a filepath
            loader = TextLoader(series, encoding='utf8')
            documents = loader.load()
        elif isinstance(series, pd.Series): 
            documents = self._convert_strings_to_docs(series.tolist())
        else:  # Assume series is already a list of text chunks
            documents = self._convert_strings_to_docs(series)

        self._index = FAISS.from_documents(documents, self._embeddings)
        return self._index

    def _create_vector_space(self, vectors):
        """Creates a Faiss index for embedding search.

        Args:
            vectors: A Faiss index of embeddings.

        Returns:
            A Faiss index.
        """
        return vectors  # In this case, FAISS.from_documents already does this

    def similarity_search(self, query, k=5, return_indexes=False, from_chat = False):
        """Performs a similarity search and returns the most similar text.

        Args:
            query: The query text.
            k: The number of top results to return.
            return_indexes: If True, returns raw indexes. Otherwise, returns text.

        Returns:
            A tuple of distances and the most similar items (texts or indexes).
        """
        assert type(query) is str, "query must be a str"
        docs_scores = []
        if not from_chat:
            docs_scores = self._index.similarity_search_with_score(query)
        docs_scores_chat = self._index_w_chat.similarity_search_with_score(query)
        final_docs_scores = docs_scores + docs_scores_chat
        #print("SCORES")
        #print(docs_scores)
        #print(docs_scores_chat)
        docs = []
        scores = []
        #for item in docs_scores:
        for item in final_docs_scores:
            docs.append(item[0].page_content)
            scores.append(item[1])

        if return_indexes:
            matches = np.array(docs).isin(self._series)  # Efficient check for membership
            matching_indexes = matches.index[matches].tolist()
            return np.array(scores), np.array(matching_indexes)
        else:
            return np.array(scores), np.array(docs)
        
    def add_history(self, query, response):
        """Adds a query and response pair to the embedding space."""
        new_doc = Document(page_content=f"chathistory: {query}\n{response}")  # Combine query and response
        #new_embedding = self._embeddings.embed_documents([new_doc])[0]
        #new_embedding = self._embeddings.embed_query(f"chathistory: {query}\n{response}")
        #new_embedding = self._embeddings.embed_query(f"chathistory: {query}")
        db2 = FAISS.from_documents([new_doc], self._embeddings)
        self._index_w_chat.merge_from(db2)
        #self._index.merge_from(db2)
        #self._index.add_with_ids(new_embedding, [self._index.ntotal])  # Add to Faiss Index
        
        #self._save_index()  # Update the saved index 

    def _save_index(self):
        """Saves the embedding index to disk."""
        self._index.save_local(f"{self._index_dir}")

    def _load_index(self):
        """Loads the embedding index from disk (if it exists)."""
        faiss_path = os.path.join(self._index_dir, "index.faiss")
        pkl_path = os.path.join(self._index_dir, "index.pkl")

        if os.path.isdir(self._index_dir):
            # Load the vectors from the pickle file
            db = FAISS.load_local(f"{self._index_dir}", self._embeddings, allow_dangerous_deserialization=True)
            db_chat = FAISS.load_local(f"{self._index_dir}", self._embeddings, allow_dangerous_deserialization=True)
            self._index = db
            self._index_w_chat = db_chat
            print("Index loaded from existing files.")
            
        else:
            print(f"No embedding folder with name {self._index_dir} found. Creating...")
            self.create_embeddings(self._series)

        

