#!/usr/bin/env python3
"""
Semantic Text Chunker using Max-Min Algorithm

Implements semantic chunking for text documents using:
1. Sentence tokenization (NLTK)
2. BGE-M3 embeddings for semantic similarity
3. Greedy max-min algorithm for coherent chunk creation
4. Target chunk size of 500-700 tokens
"""

import nltk
import numpy as np
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import hashlib
import logging
from pathlib import Path

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

class SemanticTextChunker:
    """
    Semantic text chunker using greedy max-min algorithm for coherent chunk creation.
    """
    
    def __init__(self, 
                 model_name: str = "BAAI/bge-m3",
                 target_tokens: int = 600,
                 min_tokens: int = 500,
                 max_tokens: int = 700,
                 device: str = "auto"):
        """
        Initialize the semantic text chunker.
        
        Args:
            model_name: Sentence transformer model name (BGE-M3)
            target_tokens: Target number of tokens per chunk
            min_tokens: Minimum tokens per chunk
            max_tokens: Maximum tokens per chunk
            device: Device to run the model on ("auto", "cpu", "cuda")
        """
        self.model_name = model_name
        self.target_tokens = target_tokens
        self.min_tokens = min_tokens
        self.max_tokens = max_tokens
        
        # Handle device selection
        if device == "auto":
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Initialize the embedding model
        print(f"Loading embedding model: {model_name} on device: {device}")
        self.model = SentenceTransformer(model_name, device=device)
        
        # Initialize tokenizer for token counting
        self.tokenizer = self.model.tokenizer
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def tokenize_sentences(self, text: str) -> List[str]:
        """
        Tokenize text into sentences using NLTK.
        
        Args:
            text: Input text to tokenize
            
        Returns:
            List of sentences
        """
        # Clean and normalize text
        text = text.strip()
        if not text:
            return []
        
        # Use NLTK sentence tokenizer
        sentences = nltk.sent_tokenize(text)
        
        # Filter out very short sentences and clean whitespace
        sentences = [s.strip() for s in sentences if len(s.strip()) > 10]
        
        return sentences
    
    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text using the model's tokenizer.
        
        Args:
            text: Input text
            
        Returns:
            Number of tokens
        """
        return len(self.tokenizer.encode(text))
    
    def compute_embeddings(self, sentences: List[str]) -> np.ndarray:
        """
        Compute embeddings for a list of sentences.
        
        Args:
            sentences: List of sentences
            
        Returns:
            Array of embeddings
        """
        if not sentences:
            return np.array([])
        
        embeddings = self.model.encode(sentences, convert_to_numpy=True)
        return embeddings
    
    def max_min_chunking(self, sentences: List[str], embeddings: np.ndarray) -> List[List[int]]:
        """
        Apply greedy max-min algorithm for semantic chunking.
        
        The algorithm:
        1. Start with the first sentence
        2. Iteratively add the sentence whose minimum cosine similarity 
           to the current chunk is maximal
        3. Stop when token limit is reached or no more sentences
        
        Args:
            sentences: List of sentences
            embeddings: Sentence embeddings
            
        Returns:
            List of chunks, where each chunk is a list of sentence indices
        """
        if len(sentences) == 0:
            return []
        
        chunks = []
        remaining_indices = set(range(len(sentences)))
        
        while remaining_indices:
            # Start new chunk with first remaining sentence
            current_chunk = [min(remaining_indices)]
            remaining_indices.remove(current_chunk[0])
            
            # Build chunk text for token counting
            chunk_text = sentences[current_chunk[0]]
            chunk_tokens = self.count_tokens(chunk_text)
            
            # Greedy max-min selection
            while remaining_indices and chunk_tokens < self.max_tokens:
                best_sentence_idx = None
                best_min_similarity = -1
                
                # For each remaining sentence, compute its minimum similarity to current chunk
                for candidate_idx in remaining_indices:
                    candidate_embedding = embeddings[candidate_idx].reshape(1, -1)
                    chunk_embeddings = embeddings[current_chunk]
                    
                    # Compute similarities to all sentences in current chunk
                    similarities = cosine_similarity(candidate_embedding, chunk_embeddings)[0]
                    min_similarity = np.min(similarities)
                    
                    # Check if adding this sentence would exceed token limit
                    test_text = chunk_text + " " + sentences[candidate_idx]
                    test_tokens = self.count_tokens(test_text)
                    
                    # Select sentence with maximum minimum similarity that fits
                    if (min_similarity > best_min_similarity and 
                        test_tokens <= self.max_tokens):
                        best_min_similarity = min_similarity
                        best_sentence_idx = candidate_idx
                
                # Add best sentence if found and meets minimum token requirement
                if best_sentence_idx is not None:
                    current_chunk.append(best_sentence_idx)
                    remaining_indices.remove(best_sentence_idx)
                    chunk_text += " " + sentences[best_sentence_idx]
                    chunk_tokens = self.count_tokens(chunk_text)
                else:
                    # No suitable sentence found, break if we have minimum tokens
                    if chunk_tokens >= self.min_tokens:
                        break
                    # Otherwise, add any remaining sentence to meet minimum
                    elif remaining_indices:
                        fallback_idx = next(iter(remaining_indices))
                        current_chunk.append(fallback_idx)
                        remaining_indices.remove(fallback_idx)
                        chunk_text += " " + sentences[fallback_idx]
                        chunk_tokens = self.count_tokens(chunk_text)
                        break
            
            chunks.append(current_chunk)
        
        return chunks
    
    def create_chunk_metadata(self, 
                            sentences: List[str], 
                            chunk_indices: List[int], 
                            source_id: str, 
                            chunk_id: int) -> Dict:
        """
        Create metadata for a chunk.
        
        Args:
            sentences: Original sentences
            chunk_indices: Indices of sentences in this chunk
            source_id: Source document identifier
            chunk_id: Chunk number
            
        Returns:
            Chunk metadata dictionary
        """
        chunk_text = " ".join(sentences[i] for i in chunk_indices)
        token_count = self.count_tokens(chunk_text)
        
        metadata = {
            "chunk_id": f"{source_id}_semantic_{chunk_id}",
            "text": chunk_text,
            "source": source_id,
            "chunk_index": chunk_id,
            "sentence_count": len(chunk_indices),
            "sentence_indices": chunk_indices, 
            "token_count": token_count,
            "char_count": len(chunk_text),
            "chunking_method": "max_min_semantic",
            "model_used": self.model_name,
            "hash": hashlib.md5(chunk_text.encode()).hexdigest()
        }
        
        return metadata
    
    def chunk_text(self, text: str, source_id: str) -> List[Dict]:
        """
        Main method to chunk text using semantic max-min algorithm.
        
        Args:
            text: Input text to chunk
            source_id: Identifier for the source document
            
        Returns:
            List of chunk dictionaries with metadata
        """
        self.logger.info(f"Starting semantic chunking for source: {source_id}")
        
        # Step 1: Tokenize into sentences
        sentences = self.tokenize_sentences(text)
        if not sentences:
            self.logger.warning(f"No sentences found in {source_id}")
            return []
        
        self.logger.info(f"Found {len(sentences)} sentences")
        
        # Step 2: Compute embeddings
        self.logger.info("Computing sentence embeddings...")
        embeddings = self.compute_embeddings(sentences)
        
        # Step 3: Apply max-min chunking
        self.logger.info("Applying max-min semantic chunking...")
        chunk_indices_list = self.max_min_chunking(sentences, embeddings)
        
        # Step 4: Create chunk metadata
        chunks = []
        for i, chunk_indices in enumerate(chunk_indices_list):
            chunk_metadata = self.create_chunk_metadata(
                sentences, chunk_indices, source_id, i
            )
            chunks.append(chunk_metadata)
        
        self.logger.info(f"Created {len(chunks)} semantic chunks")
        
        # Log statistics
        token_counts = [c["token_count"] for c in chunks]
        self.logger.info(f"Token count stats - Min: {min(token_counts)}, "
                        f"Max: {max(token_counts)}, "
                        f"Mean: {np.mean(token_counts):.1f}")
        
        return chunks


def main():
    """Example usage of SemanticTextChunker"""
    
    # Sample text for testing
    sample_text = """
    Robotics is a field that combines engineering, computer science, and artificial intelligence. 
    Industrial robots are widely used in manufacturing processes. They can perform tasks with high 
    precision and consistency. The Meca500 is a compact 6-axis industrial robot arm designed for 
    precision tasks in confined spaces.
    
    Programming industrial robots requires understanding of coordinate frames and motion planning. 
    The robot's end effector moves through 3D space following programmed paths. Safety considerations 
    are paramount when working with industrial robots. Emergency stops and safety zones must be 
    properly configured.
    
    Modern robots use advanced sensors for feedback and control. Vision systems enable robots to 
    adapt to variations in their environment. Force sensing allows for delicate manipulation tasks. 
    The integration of these technologies makes robots increasingly versatile and capable.
    """
    
    # Initialize chunker
    chunker = SemanticTextChunker(target_tokens=200, min_tokens=150, max_tokens=250)
    
    # Chunk the text
    chunks = chunker.chunk_text(sample_text, "sample_robot_text")
    
    # Display results
    print(f"\nCreated {len(chunks)} chunks:")
    for i, chunk in enumerate(chunks):
        print(f"\nChunk {i + 1}:")
        print(f"  Tokens: {chunk['token_count']}")
        print(f"  Sentences: {chunk['sentence_count']}")
        print(f"  Text: {chunk['text'][:100]}...")


if __name__ == "__main__":
    main()