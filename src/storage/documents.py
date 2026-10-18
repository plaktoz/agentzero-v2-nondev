"""
Document storage system for content management.
Handles storage, versioning, and retrieval of documents.
"""

import os
import json
import aiofiles
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class DocumentMetadata:
    """Metadata for a document."""
    id: str
    title: str
    content_type: str
    status: str  # "draft", "review", "approved", "published"
    created_at: str
    updated_at: str
    author: str
    version: int
    word_count: int
    quality_score: Optional[float] = None
    tags: Optional[List[str]] = None


class DocumentStorage:
    """Manages document storage and versioning."""
    
    def __init__(self, base_path: str = "./documents"):
        """
        Initialize document storage.
        
        Args:
            base_path: Base directory for document storage
        """
        self.base_path = Path(base_path)
        self.research_path = self.base_path / "research"
        self.drafts_path = self.base_path / "drafts"
        self.finals_path = self.base_path / "finals"
        self.metadata_path = self.base_path / "metadata"
        
        # Create directories if they don't exist
        for path in [self.research_path, self.drafts_path, 
                     self.finals_path, self.metadata_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    async def save_document(
        self,
        doc_id: str,
        content: str,
        metadata: DocumentMetadata,
        status: str = "draft"
    ) -> str:
        """
        Save document with metadata.
        
        Args:
            doc_id: Unique document identifier
            content: Document content (markdown)
            metadata: Document metadata
            status: Document status (draft, review, approved, published)
            
        Returns:
            Path to saved document
        """
        # Determine storage path based on status
        if status == "draft":
            doc_path = self.drafts_path / doc_id
        elif status in ["approved", "published"]:
            doc_path = self.finals_path / doc_id
        else:
            doc_path = self.drafts_path / doc_id
        
        doc_path.mkdir(parents=True, exist_ok=True)
        
        # Update metadata
        metadata.updated_at = datetime.utcnow().isoformat()
        metadata.status = status
        metadata.word_count = len(content.split())
        
        # Save content with version
        version = metadata.version
        content_file = doc_path / f"v{version}.md"
        
        async with aiofiles.open(content_file, "w", encoding="utf-8") as f:
            await f.write(content)
        
        # Save metadata
        metadata_file = self.metadata_path / f"{doc_id}.json"
        async with aiofiles.open(metadata_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(asdict(metadata), indent=2))
        
        return str(content_file)
    
    async def load_document(
        self,
        doc_id: str,
        version: Optional[int] = None
    ) -> tuple[str, DocumentMetadata]:
        """
        Load document and metadata.
        
        Args:
            doc_id: Document identifier
            version: Specific version to load (None for latest)
            
        Returns:
            Tuple of (content, metadata)
        """
        # Load metadata
        metadata_file = self.metadata_path / f"{doc_id}.json"
        
        if not metadata_file.exists():
            raise FileNotFoundError(f"Document not found: {doc_id}")
        
        async with aiofiles.open(metadata_file, "r", encoding="utf-8") as f:
            metadata_dict = json.loads(await f.read())
            metadata = DocumentMetadata(**metadata_dict)
        
        # Determine document path
        if metadata.status == "draft":
            doc_path = self.drafts_path / doc_id
        else:
            doc_path = self.finals_path / doc_id
        
        # Load content
        if version is None:
            version = metadata.version
        
        content_file = doc_path / f"v{version}.md"
        
        if not content_file.exists():
            raise FileNotFoundError(f"Version {version} not found for document: {doc_id}")
        
        async with aiofiles.open(content_file, "r", encoding="utf-8") as f:
            content = await f.read()
        
        return content, metadata
    
    async def list_documents(
        self,
        status: Optional[str] = None,
        content_type: Optional[str] = None
    ) -> List[DocumentMetadata]:
        """
        List documents with optional filtering.
        
        Args:
            status: Filter by status
            content_type: Filter by content type
            
        Returns:
            List of document metadata
        """
        documents = []
        
        # Iterate through metadata files
        for metadata_file in self.metadata_path.glob("*.json"):
            async with aiofiles.open(metadata_file, "r", encoding="utf-8") as f:
                metadata_dict = json.loads(await f.read())
                metadata = DocumentMetadata(**metadata_dict)
                
                # Apply filters
                if status and metadata.status != status:
                    continue
                if content_type and metadata.content_type != content_type:
                    continue
                
                documents.append(metadata)
        
        # Sort by updated_at (most recent first)
        documents.sort(key=lambda x: x.updated_at, reverse=True)
        
        return documents
    
    async def update_status(
        self,
        doc_id: str,
        new_status: str
    ) -> None:
        """
        Update document status.
        
        Args:
            doc_id: Document identifier
            new_status: New status value
        """
        content, metadata = await self.load_document(doc_id)
        
        # Move document if status changes between draft and final
        old_status = metadata.status
        if old_status == "draft" and new_status in ["approved", "published"]:
            # Move from drafts to finals
            old_path = self.drafts_path / doc_id
            new_path = self.finals_path / doc_id
            
            if old_path.exists():
                import shutil
                shutil.move(str(old_path), str(new_path))
        
        # Update metadata
        metadata.status = new_status
        metadata.updated_at = datetime.utcnow().isoformat()
        
        # Save updated metadata
        metadata_file = self.metadata_path / f"{doc_id}.json"
        async with aiofiles.open(metadata_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(asdict(metadata), indent=2))
    
    async def create_version(
        self,
        doc_id: str,
        content: str
    ) -> int:
        """
        Create new version of document.
        
        Args:
            doc_id: Document identifier
            content: New content
            
        Returns:
            New version number
        """
        _, metadata = await self.load_document(doc_id)
        
        # Increment version
        new_version = metadata.version + 1
        metadata.version = new_version
        
        # Save new version
        await self.save_document(doc_id, content, metadata, metadata.status)
        
        return new_version
    
    async def get_versions(self, doc_id: str) -> List[int]:
        """
        Get list of available versions for document.
        
        Args:
            doc_id: Document identifier
            
        Returns:
            List of version numbers
        """
        _, metadata = await self.load_document(doc_id)
        
        # Determine document path
        if metadata.status == "draft":
            doc_path = self.drafts_path / doc_id
        else:
            doc_path = self.finals_path / doc_id
        
        # Find all version files
        versions = []
        for version_file in doc_path.glob("v*.md"):
            version_num = int(version_file.stem[1:])  # Remove 'v' prefix
            versions.append(version_num)
        
        return sorted(versions)
