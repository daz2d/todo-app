"""
Memory and Learning System

Provides persistent memory across sessions with learning from mistakes.
Implements episodic, semantic, procedural, and error memory types.
"""

import os
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib


@dataclass
class MemoryEntry:
    """Represents a memory entry in the database."""
    id: Optional[int]
    memory_type: str  # 'episodic', 'semantic', 'procedural', 'error'
    content: str
    context: str
    tags: List[str]
    success: bool
    created_at: str
    embedding_hash: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class MemorySystem:
    """
    Persistent memory system with learning capabilities.
    
    Features:
    - Episodic memory: Complete conversation histories and decision trails
    - Semantic memory: Extracted patterns, best practices, anti-patterns
    - Procedural memory: Successful workflows and solution templates
    - Error memory: Failed approaches with root causes and fixes
    - Context retrieval: Pull relevant past experiences for current tasks
    - Learning: Analyzes patterns to improve future performance
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize memory system.
        
        Args:
            db_path: Path to SQLite database. Defaults to MEMORY_DB_PATH env var.
        """
        self.enabled = os.getenv('LEARNING_ENABLED', 'true').lower() == 'true'
        
        if not self.enabled:
            self.db_path = None
            self.conn = None
            return
        
        self.db_path = db_path or os.getenv('MEMORY_DB_PATH', './memory.db')
        self.retrieval_limit = int(os.getenv('MEMORY_RETRIEVAL_LIMIT', '5'))
        self.similarity_threshold = float(os.getenv('MEMORY_SIMILARITY_THRESHOLD', '0.7'))
        self.auto_learn = os.getenv('AUTO_LEARN_FROM_FAILURES', 'true').lower() == 'true'
        self.store_success = os.getenv('STORE_SUCCESS_PATTERNS', 'true').lower() == 'true'
        
        # Initialize database
        self._init_db()
    
    def _init_db(self):
        """Create database tables if they don't exist."""
        if not self.enabled:
            return
        
        # Ensure directory exists
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Connect and create tables
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        
        # Main memory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_type TEXT NOT NULL,
                content TEXT NOT NULL,
                context TEXT,
                tags TEXT,
                success BOOLEAN,
                created_at TEXT NOT NULL,
                embedding_hash TEXT
            )
        ''')
        
        # Index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_memory_type 
            ON memories(memory_type)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_tags 
            ON memories(tags)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_success 
            ON memories(success)
        ''')
        
        # Statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                context TEXT,
                recorded_at TEXT NOT NULL
            )
        ''')
        
        self.conn.commit()
    
    def store(
        self,
        memory_type: str,
        content: str,
        context: str = "",
        tags: Optional[List[str]] = None,
        success: bool = True
    ) -> int:
        """
        Store a memory entry.
        
        Args:
            memory_type: Type of memory ('episodic', 'semantic', 'procedural', 'error').
            content: Main content of the memory.
            context: Additional context information.
            tags: List of tags for categorization and retrieval.
            success: Whether this represents a successful approach.
        
        Returns:
            ID of stored memory entry.
        
        Examples:
            >>> memory = MemorySystem()
            >>> memory.store(
            ...     memory_type='error',
            ...     content='JSON file corruption caused data loss',
            ...     context='TODO app file storage',
            ...     tags=['json', 'persistence', 'error-handling'],
            ...     success=False
            ... )
        """
        if not self.enabled:
            return -1
        
        tags = tags or []
        tags_json = json.dumps(tags)
        
        # Create content hash for similarity detection
        embedding_hash = hashlib.md5(content.encode()).hexdigest()
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO memories (memory_type, content, context, tags, success, created_at, embedding_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (memory_type, content, context, tags_json, success, datetime.now().isoformat(), embedding_hash))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def retrieve(
        self,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        success_only: bool = False,
        limit: Optional[int] = None
    ) -> List[MemoryEntry]:
        """
        Retrieve relevant memories.
        
        Args:
            query: Text query for semantic search (basic keyword matching).
            memory_type: Filter by memory type.
            tags: Filter by tags (matches if ANY tag present).
            success_only: Only return successful approaches.
            limit: Maximum number of results (defaults to MEMORY_RETRIEVAL_LIMIT).
        
        Returns:
            List of matching memory entries, ordered by relevance/recency.
        
        Examples:
            >>> # Find past JSON persistence solutions
            >>> memories = memory.retrieve(
            ...     query='json file storage',
            ...     memory_type='procedural',
            ...     success_only=True
            ... )
        """
        if not self.enabled:
            return []
        
        limit = limit or self.retrieval_limit
        
        cursor = self.conn.cursor()
        
        # Build query
        conditions = []
        params = []
        
        if query:
            conditions.append("(content LIKE ? OR context LIKE ?)")
            query_pattern = f"%{query}%"
            params.extend([query_pattern, query_pattern])
        
        if memory_type:
            conditions.append("memory_type = ?")
            params.append(memory_type)
        
        if tags:
            tag_conditions = " OR ".join(["tags LIKE ?" for _ in tags])
            conditions.append(f"({tag_conditions})")
            params.extend([f"%{tag}%" for tag in tags])
        
        if success_only:
            conditions.append("success = 1")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        cursor.execute(f'''
            SELECT * FROM memories
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ?
        ''', params + [limit])
        
        rows = cursor.fetchall()
        
        # Convert to MemoryEntry objects
        entries = []
        for row in rows:
            entries.append(MemoryEntry(
                id=row['id'],
                memory_type=row['memory_type'],
                content=row['content'],
                context=row['context'],
                tags=json.loads(row['tags']),
                success=bool(row['success']),
                created_at=row['created_at'],
                embedding_hash=row['embedding_hash']
            ))
        
        return entries
    
    def learn_from_failure(
        self,
        failure_description: str,
        root_cause: str,
        solution: str,
        context: str = "",
        tags: Optional[List[str]] = None
    ) -> int:
        """
        Store a lesson learned from failure.
        
        Args:
            failure_description: What went wrong.
            root_cause: Why it went wrong.
            solution: How it was fixed.
            context: Additional context.
            tags: Categorization tags.
        
        Returns:
            ID of stored memory entry.
        
        Examples:
            >>> memory.learn_from_failure(
            ...     failure_description='App crashed on startup',
            ...     root_cause='Uncaught exception when JSON file missing',
            ...     solution='Added try/except with default empty list return',
            ...     context='TODO app initialization',
            ...     tags=['error-handling', 'json', 'startup']
            ... )
        """
        if not self.enabled or not self.auto_learn:
            return -1
        
        content = f"""
FAILURE: {failure_description}

ROOT CAUSE: {root_cause}

SOLUTION: {solution}

LESSON: Always handle missing file cases. Check file existence before reading. Provide sensible defaults.
"""
        
        return self.store(
            memory_type='error',
            content=content.strip(),
            context=context,
            tags=tags or [],
            success=False
        )
    
    def store_success_pattern(
        self,
        pattern_name: str,
        description: str,
        implementation: str,
        context: str = "",
        tags: Optional[List[str]] = None
    ) -> int:
        """
        Store a successful approach/pattern for reuse.
        
        Args:
            pattern_name: Name of the pattern.
            description: What problem it solves.
            implementation: How to implement it.
            context: Where it was used.
            tags: Categorization tags.
        
        Returns:
            ID of stored memory entry.
        
        Examples:
            >>> memory.store_success_pattern(
            ...     pattern_name='Atomic File Write',
            ...     description='Prevent file corruption during write',
            ...     implementation='Write to temp file, then rename atomically',
            ...     context='TODO app persistence',
            ...     tags=['file-io', 'reliability', 'pattern']
            ... )
        """
        if not self.enabled or not self.store_success:
            return -1
        
        content = f"""
PATTERN: {pattern_name}

PROBLEM: {description}

SOLUTION: {implementation}

APPLICABILITY: {context or 'General use'}
"""
        
        return self.store(
            memory_type='procedural',
            content=content.strip(),
            context=context,
            tags=tags or [],
            success=True
        )
    
    def store_conversation(
        self,
        role: str,
        turn: int,
        notes: str,
        context: str = ""
    ) -> int:
        """
        Store conversation history (episodic memory).
        
        Args:
            role: Agent role (pm, backend, frontend, reviewer).
            turn: Turn number.
            notes: Agent's notes/output.
            context: Additional context.
        
        Returns:
            ID of stored memory entry.
        """
        if not self.enabled:
            return -1
        
        return self.store(
            memory_type='episodic',
            content=notes,
            context=f"Turn {turn} - {role}: {context}",
            tags=[role, f'turn-{turn}'],
            success=True
        )
    
    def record_statistic(
        self,
        metric_name: str,
        metric_value: float,
        context: str = ""
    ):
        """
        Record a performance statistic.
        
        Args:
            metric_name: Name of metric (e.g., 'approval_rate', 'turns_to_approval').
            metric_value: Numeric value.
            context: Additional context.
        
        Examples:
            >>> memory.record_statistic('turns_to_approval', 7, 'TODO app project')
            >>> memory.record_statistic('test_coverage', 0.92, 'Backend tests')
        """
        if not self.enabled:
            return
        
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO statistics (metric_name, metric_value, context, recorded_at)
            VALUES (?, ?, ?, ?)
        ''', (metric_name, metric_value, context, datetime.now().isoformat()))
        
        self.conn.commit()
    
    def get_statistics(
        self,
        metric_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recorded statistics.
        
        Args:
            metric_name: Filter by specific metric name.
            limit: Maximum number of results.
        
        Returns:
            List of statistic records.
        """
        if not self.enabled:
            return []
        
        cursor = self.conn.cursor()
        
        if metric_name:
            cursor.execute('''
                SELECT * FROM statistics
                WHERE metric_name = ?
                ORDER BY recorded_at DESC
                LIMIT ?
            ''', (metric_name, limit))
        else:
            cursor.execute('''
                SELECT * FROM statistics
                ORDER BY recorded_at DESC
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of memory system state.
        
        Returns:
            Dictionary with memory counts, statistics, and insights.
        """
        if not self.enabled:
            return {'enabled': False}
        
        cursor = self.conn.cursor()
        
        # Count memories by type
        cursor.execute('''
            SELECT memory_type, COUNT(*) as count
            FROM memories
            GROUP BY memory_type
        ''')
        type_counts = {row['memory_type']: row['count'] for row in cursor.fetchall()}
        
        # Count successes vs failures
        cursor.execute('SELECT COUNT(*) as count FROM memories WHERE success = 1')
        success_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM memories WHERE success = 0')
        failure_count = cursor.fetchone()['count']
        
        # Recent statistics
        recent_stats = self.get_statistics(limit=10)
        
        return {
            'enabled': True,
            'db_path': self.db_path,
            'total_memories': sum(type_counts.values()),
            'by_type': type_counts,
            'success_count': success_count,
            'failure_count': failure_count,
            'success_rate': success_count / (success_count + failure_count) if (success_count + failure_count) > 0 else 0,
            'recent_statistics': recent_stats[:5]
        }
    
    def close(self):
        """Close database connection."""
        if self.enabled and self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Convenience function for quick memory operations
def get_memory_system() -> MemorySystem:
    """
    Get the global memory system instance.
    
    Returns:
        Configured MemorySystem instance.
    """
    return MemorySystem()


# Extensibility: The memory system can be extended with:
# 1. Vector embeddings for semantic similarity search (integrate sentence-transformers)
# 2. Memory consolidation (merge similar memories, archive old ones)
# 3. Export/import capabilities for knowledge transfer
# 4. Multi-agent memory sharing with access control
# 5. Memory decay (reduce weight of old memories over time)
# 6. Conflict resolution (handling contradictory memories)
