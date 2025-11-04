"""
Retrieval-Augmented Generation (RAG) Service
Provides semantic search over conversation history using ChromaDB and sentence-transformers
"""
import time
from typing import List, Optional
from datetime import datetime
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from models.conversation import Conversation
from models.rag_models import RetrievedConversation, RAGQuery, RAGSearchResult
from utils.logger import get_logger

logger = get_logger(__name__)


class RAGService:
    """
    Service for semantic search over conversation history
    Uses ChromaDB for vector storage and sentence-transformers for embeddings
    """

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize RAG service

        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        try:
            # Initialize sentence transformer for embeddings
            # Using all-MiniLM-L6-v2: lightweight, fast, 384-dimensional embeddings
            logger.info("Loading sentence transformer model...")
            self.embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            logger.info("✅ Sentence transformer loaded successfully")

            # Initialize ChromaDB client
            logger.info(f"Initializing ChromaDB at {persist_directory}...")
            self.chroma_client = chromadb.Client(Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False
            ))

            # Get or create collection for conversations
            self.collection = self.chroma_client.get_or_create_collection(
                name="conversations",
                metadata={"description": "User conversation history with AI"}
            )

            logger.info("✅ RAG service initialized successfully")
            logger.info(f"📊 Collection size: {self.collection.count()} conversations")

        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG service: {e}")
            raise

    async def embed_and_store_conversation(
        self,
        conversation: Conversation
    ) -> bool:
        """
        Embed a conversation and store it in ChromaDB

        Args:
            conversation: The conversation to embed and store

        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract user message and AI response
            user_message = ""
            ai_response = ""

            for msg in conversation.messages:
                if msg.role == "user":
                    user_message = msg.content
                elif msg.role == "assistant":
                    ai_response = msg.content

            # Skip if no messages
            if not user_message or not ai_response:
                logger.warning(f"Conversation {conversation.conversation_id} has no messages, skipping embedding")
                return False

            # Create combined text for embedding
            # Format: "User: <message> Assistant: <response>"
            combined_text = f"User: {user_message} Assistant: {ai_response}"

            # Generate embedding
            embedding = self.embedder.encode(combined_text).tolist()

            # Prepare metadata
            metadata = {
                "user_id": conversation.user_id,
                "user_message": user_message[:500],  # Limit for ChromaDB
                "ai_response": ai_response[:500],
                "created_at": conversation.created_at.isoformat(),
                "main_topic": conversation.main_topic or "Unknown"
            }

            # Store in ChromaDB
            self.collection.add(
                ids=[conversation.conversation_id],
                embeddings=[embedding],
                documents=[combined_text],
                metadatas=[metadata]
            )

            logger.info(f"✅ Embedded and stored conversation: {conversation.conversation_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Error embedding conversation: {e}")
            return False

    async def search_similar_conversations(
        self,
        query: RAGQuery
    ) -> RAGSearchResult:
        """
        Search for semantically similar conversations

        Args:
            query: RAG query with search parameters

        Returns:
            RAGSearchResult with retrieved conversations
        """
        start_time = time.time()

        try:
            # Embed the query
            query_embedding = self.embedder.encode(query.query_text).tolist()

            # Search ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=query.k,
                where={"user_id": query.user_id}  # Filter by user
            )

            # Parse results
            retrieved_conversations = []

            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    # Calculate similarity score (ChromaDB returns distances, convert to similarity)
                    # For cosine similarity: similarity = 1 - distance
                    distance = results['distances'][0][i] if 'distances' in results else 0
                    similarity_score = 1.0 - distance

                    # Skip if below threshold
                    if similarity_score < query.min_similarity:
                        continue

                    # Extract metadata
                    metadata = results['metadatas'][0][i]

                    retrieved_conv = RetrievedConversation(
                        conversation_id=results['ids'][0][i],
                        user_id=metadata['user_id'],
                        similarity_score=similarity_score,
                        user_message=metadata['user_message'],
                        ai_response=metadata['ai_response'],
                        created_at=datetime.fromisoformat(metadata['created_at']),
                        main_topic=metadata.get('main_topic')
                    )

                    retrieved_conversations.append(retrieved_conv)

            # Calculate search time
            search_time_ms = (time.time() - start_time) * 1000

            result = RAGSearchResult(
                query=query.query_text,
                retrieved_conversations=retrieved_conversations,
                total_results=len(retrieved_conversations),
                search_time_ms=search_time_ms
            )

            logger.info(f"🔍 RAG search complete: {result.total_results} results in {search_time_ms:.1f}ms")
            return result

        except Exception as e:
            logger.error(f"❌ Error in RAG search: {e}")
            # Return empty result
            search_time_ms = (time.time() - start_time) * 1000
            return RAGSearchResult(
                query=query.query_text,
                retrieved_conversations=[],
                total_results=0,
                search_time_ms=search_time_ms
            )

    def get_collection_stats(self) -> dict:
        """Get statistics about the ChromaDB collection"""
        try:
            count = self.collection.count()
            return {
                "total_conversations": count,
                "collection_name": self.collection.name,
                "status": "healthy"
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "total_conversations": 0,
                "collection_name": "unknown",
                "status": "error"
            }

    async def delete_user_conversations(self, user_id: str) -> int:
        """
        Delete all conversations for a user (for privacy/GDPR compliance)

        Args:
            user_id: User ID

        Returns:
            Number of conversations deleted
        """
        try:
            # Get all conversations for user
            results = self.collection.get(
                where={"user_id": user_id}
            )

            if results['ids']:
                # Delete them
                self.collection.delete(ids=results['ids'])
                logger.info(f"🗑️ Deleted {len(results['ids'])} conversations for user {user_id}")
                return len(results['ids'])

            return 0

        except Exception as e:
            logger.error(f"❌ Error deleting user conversations: {e}")
            return 0
