#!/usr/bin/env python3
"""
MCP (Model Context Protocol) Integration with Weave
Advanced context management and protocol handling
"""

import weave
from typing import Dict, List, Any, Optional, AsyncGenerator
import json
import time
import asyncio
from dataclasses import dataclass, asdict
from enum import Enum

class MessageType(Enum):
    """MCP message types"""
    REQUEST = "request"
    RESPONSE = "response" 
    NOTIFICATION = "notification"
    ERROR = "error"

@dataclass
class MCPMessage:
    """MCP protocol message"""
    id: str
    type: MessageType
    method: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

@weave.op()
class WeaveProtocol:
    """MCP protocol implementation with Weave tracing"""
    
    def __init__(self, agent_id: str = "weave-agent"):
        self.agent_id = agent_id
        self.message_id_counter = 0
        self.active_sessions = {}
        self.message_history = []
        self.context_store = {}
        
    @weave.op()
    def generate_message_id(self) -> str:
        """Generate unique message ID"""
        self.message_id_counter += 1
        return f"{self.agent_id}-{self.message_id_counter}-{int(time.time())}"
    
    @weave.op()
    def create_request(self, method: str, params: Dict[str, Any]) -> MCPMessage:
        """Create MCP request message"""
        message = MCPMessage(
            id=self.generate_message_id(),
            type=MessageType.REQUEST,
            method=method,
            params=params
        )
        self.message_history.append(message)
        return message
    
    @weave.op()
    def create_response(self, request_id: str, result: Any) -> MCPMessage:
        """Create MCP response message"""
        message = MCPMessage(
            id=request_id,
            type=MessageType.RESPONSE,
            result=result
        )
        self.message_history.append(message)
        return message
    
    @weave.op()
    def create_error(self, request_id: str, error_code: int, error_message: str) -> MCPMessage:
        """Create MCP error message"""
        message = MCPMessage(
            id=request_id,
            type=MessageType.ERROR,
            error={
                "code": error_code,
                "message": error_message
            }
        )
        self.message_history.append(message)
        return message
    
    @weave.op()
    def store_context(self, key: str, context: Dict[str, Any]):
        """Store context information"""
        self.context_store[key] = {
            "data": context,
            "timestamp": time.time(),
            "agent_id": self.agent_id
        }
    
    @weave.op()
    def get_context(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve context information"""
        return self.context_store.get(key)
    
    @weave.op()
    def list_contexts(self) -> List[str]:
        """List all stored context keys"""
        return list(self.context_store.keys())
    
    @weave.op()
    def process_agent_request(self, query: str, context_keys: List[str] = None) -> MCPMessage:
        """Process agent request with context"""
        # Gather relevant context
        context = {}
        if context_keys:
            for key in context_keys:
                ctx = self.get_context(key)
                if ctx:
                    context[key] = ctx
        
        # Create request
        request = self.create_request(
            method="agent.process",
            params={
                "query": query,
                "context": context,
                "agent_id": self.agent_id,
                "timestamp": time.time()
            }
        )
        
        return request
    
    @weave.op()
    def process_tool_request(self, tool_name: str, tool_params: Dict[str, Any]) -> MCPMessage:
        """Process tool execution request"""
        request = self.create_request(
            method="tool.execute",
            params={
                "tool_name": tool_name,
                "parameters": tool_params,
                "agent_id": self.agent_id,
                "timestamp": time.time()
            }
        )
        
        return request
    
    @weave.op()
    def get_message_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent message history"""
        recent_messages = self.message_history[-limit:] if limit > 0 else self.message_history
        return [asdict(msg) for msg in recent_messages]
    
    @weave.op()
    def get_protocol_stats(self) -> Dict[str, Any]:
        """Get protocol statistics"""
        message_types = {}
        for msg in self.message_history:
            msg_type = msg.type.value
            message_types[msg_type] = message_types.get(msg_type, 0) + 1
        
        return {
            "agent_id": self.agent_id,
            "total_messages": len(self.message_history),
            "message_types": message_types,
            "active_sessions": len(self.active_sessions),
            "stored_contexts": len(self.context_store),
            "last_activity": self.message_history[-1].timestamp if self.message_history else None
        }

@weave.op()
class MCPContextManager:
    """Advanced context management for MCP"""
    
    def __init__(self, protocol: WeaveProtocol):
        self.protocol = protocol
        self.context_templates = {}
        self.context_relationships = {}
    
    @weave.op()
    def create_context_template(self, template_name: str, schema: Dict[str, Any]):
        """Create a context template"""
        self.context_templates[template_name] = {
            "schema": schema,
            "created_at": time.time(),
            "usage_count": 0
        }
    
    @weave.op()
    def create_context_from_template(self, template_name: str, data: Dict[str, Any]) -> str:
        """Create context instance from template"""
        if template_name not in self.context_templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.context_templates[template_name]
        template["usage_count"] += 1
        
        # Generate context key
        context_key = f"{template_name}-{int(time.time())}"
        
        # Store context
        context_data = {
            "template": template_name,
            "data": data,
            "schema": template["schema"],
            "created_at": time.time()
        }
        
        self.protocol.store_context(context_key, context_data)
        return context_key
    
    @weave.op()
    def link_contexts(self, parent_key: str, child_key: str, relationship_type: str = "contains"):
        """Create relationship between contexts"""
        if parent_key not in self.context_relationships:
            self.context_relationships[parent_key] = []
        
        self.context_relationships[parent_key].append({
            "child": child_key,
            "type": relationship_type,
            "created_at": time.time()
        })
    
    @weave.op()
    def get_related_contexts(self, context_key: str) -> List[str]:
        """Get all related context keys"""
        related = []
        
        # Direct children
        if context_key in self.context_relationships:
            related.extend([rel["child"] for rel in self.context_relationships[context_key]])
        
        # Parents (reverse lookup)
        for parent, children in self.context_relationships.items():
            if any(child["child"] == context_key for child in children):
                related.append(parent)
        
        return related
    
    @weave.op()
    def get_context_manager_stats(self) -> Dict[str, Any]:
        """Get context manager statistics"""
        return {
            "templates_count": len(self.context_templates),
            "relationships_count": sum(len(rels) for rels in self.context_relationships.values()),
            "most_used_template": max(
                self.context_templates.items(),
                key=lambda x: x[1]["usage_count"],
                default=(None, {"usage_count": 0})
            )[0] if self.context_templates else None
        }