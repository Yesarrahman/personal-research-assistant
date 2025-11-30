"""
Session Manager - Research Assistant System

Manages conversation state and memory across research sessions.
Implements in-memory session storage for context retention.

This demonstrates the "Sessions & Memory" requirement from the capstone.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages research sessions and maintains conversation context.
    Implements in-memory storage for session data.
    """
    
    def __init__(self):
        """Initialize session manager with empty storage."""
        self.sessions: Dict[str, dict] = {}
        logger.info("Session Manager initialized")
    
    def create_session(self) -> str:
        """
        Create a new research session.
        
        Returns:
            str: Unique session ID
        """
        session_id = str(uuid.uuid4())
        
        self.sessions[session_id] = {
            'id': session_id,
            'created_at': datetime.now().isoformat(),
            'queries': [],
            'context': {},
            'history': []
        }
        
        logger.info(f"Created new session: {session_id}")
        return session_id
    
    def store(self, session_id: str, data: dict) -> bool:
        """
        Store research data in a session.
        
        Args:
            session_id: Session identifier
            data: Research data to store
            
        Returns:
            bool: Success status
        """
        if session_id not in self.sessions:
            logger.warning(f"Session not found: {session_id}")
            # Create session if it doesn't exist
            self.sessions[session_id] = {
                'id': session_id,
                'created_at': datetime.now().isoformat(),
                'queries': [],
                'context': {},
                'history': []
            }
        
        session = self.sessions[session_id]
        
        # Store query if present
        if 'query' in data:
            session['queries'].append({
                'query': data['query'],
                'timestamp': datetime.now().isoformat()
            })
        
        # Update context
        session['context'].update(data)
        
        # Add to history
        session['history'].append({
            'timestamp': datetime.now().isoformat(),
            'data': data
        })
        
        # Update last accessed time
        session['last_accessed'] = datetime.now().isoformat()
        
        logger.info(f"Stored data in session: {session_id}")
        return True
    
    def retrieve(self, session_id: str) -> Optional[dict]:
        """
        Retrieve session data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            dict: Session context or None if not found
        """
        if session_id not in self.sessions:
            logger.warning(f"Session not found: {session_id}")
            return None
        
        session = self.sessions[session_id]
        session['last_accessed'] = datetime.now().isoformat()
        
        logger.info(f"Retrieved session: {session_id}")
        return session['context']
    
    def get_history(self, session_id: str, limit: int = 10) -> list:
        """
        Get session history.
        
        Args:
            session_id: Session identifier
            limit: Maximum number of history items
            
        Returns:
            list: Recent history items
        """
        if session_id not in self.sessions:
            return []
        
        history = self.sessions[session_id]['history']
        return history[-limit:]  # Return most recent items
    
    def get_queries(self, session_id: str) -> list:
        """
        Get all queries from a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            list: Query history
        """
        if session_id not in self.sessions:
            return []
        
        return self.sessions[session_id]['queries']
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session and all its data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: Success status
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        
        logger.warning(f"Cannot delete, session not found: {session_id}")
        return False
    
    def list_sessions(self) -> list:
        """
        List all active sessions.
        
        Returns:
            list: Session metadata
        """
        sessions = []
        
        for session_id, session in self.sessions.items():
            sessions.append({
                'id': session_id,
                'created_at': session['created_at'],
                'last_accessed': session.get('last_accessed'),
                'num_queries': len(session['queries'])
            })
        
        return sessions