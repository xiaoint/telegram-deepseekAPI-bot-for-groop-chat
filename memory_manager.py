import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path
import asyncio
import aiofiles

class MemoryManager:
    def __init__(self, memory_dir: str = "./memory", max_messages: int = 30):
        self.memory_dir = Path(memory_dir)
        self.max_messages = max_messages
        self.memory_dir.mkdir(exist_ok=True)
        self._locks = {}
    
    def _get_lock(self, group_id: str):
        """Get or create a lock for a specific group."""
        if group_id not in self._locks:
            self._locks[group_id] = asyncio.Lock()
        return self._locks[group_id]
    
    def _get_file_path(self, group_id: str) -> Path:
        """Get the file path for a group's memory."""
        return self.memory_dir / f"{group_id}.json"
    
    async def load_memory(self, group_id: str) -> List[Dict[str, Any]]:
        """Load chat history for a group."""
        file_path = self._get_file_path(group_id)
        
        if not file_path.exists():
            return []
        
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content) if content else []
        except Exception as e:
            print(f"Error loading memory for group {group_id}: {e}")
            return []
    
    async def save_message(self, group_id: str, message_data: Dict[str, Any]):
        """Save a new message to the group's memory."""
        async with self._get_lock(group_id):
            # Load existing messages
            messages = await self.load_memory(group_id)
            
            # Add new message
            messages.append(message_data)
            
            # Keep only the latest messages (use default max_messages)
            if len(messages) > self.max_messages:
                messages = messages[-self.max_messages:]
            
            # Save to file
            file_path = self._get_file_path(group_id)
            try:
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(messages, ensure_ascii=False, indent=2))
            except Exception as e:
                print(f"Error saving memory for group {group_id}: {e}")
    
    async def get_context(self, group_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get the context for a group with an optional message limit."""
        messages = await self.load_memory(group_id)
        
        if limit is not None and limit > 0:
            # Return only the last 'limit' messages
            return messages[-limit:] if len(messages) > limit else messages
        
        return messages
    
    async def find_message_by_id(self, group_id: str, message_id: int) -> Optional[Dict[str, Any]]:
        """Find a specific message by ID in the group's memory."""
        messages = await self.load_memory(group_id)
        for msg in messages:
            if msg.get('message_id') == message_id:
                return msg
        return None
    
    async def clear_memory(self, group_id: str):
        """Clear all memory for a group (useful when switching modes)."""
        async with self._get_lock(group_id):
            file_path = self._get_file_path(group_id)
            try:
                if file_path.exists():
                    async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                        await f.write(json.dumps([], ensure_ascii=False, indent=2))
            except Exception as e:
                print(f"Error clearing memory for group {group_id}: {e}")
    
    async def get_memory_stats(self, group_id: str) -> Dict[str, Any]:
        """Get statistics about a group's memory."""
        messages = await self.load_memory(group_id)
        return {
            "total_messages": len(messages),
            "max_capacity": self.max_messages,
            "memory_usage_percent": round((len(messages) / self.max_messages) * 100, 2) if self.max_messages > 0 else 0
        }