import re
from typing import Optional

class RAGEngine:
    """Rule-based RAG system for answering system monitoring questions."""
    
    def __init__(self):
        self.context_data = ""
    
    def set_context(self, context: str):
        """Update the context data."""
        self.context_data = context
    
    def generate(self, prompt: str, context: str = "") -> str:
        """
        Generate answer using template matching on context data.
        Falls back to generic response if no match found.
        """
        if context:
            self.context_data = context
        
        query = prompt.lower()
        
        # Disk/Storage queries
        if any(word in query for word in ['space', 'storage', 'disk', 'folder', 'directory', 'largest']):
            return self._answer_disk_query(query)
        
        # Memory queries
        if any(word in query for word in ['memory', 'ram', 'consuming']):
            return self._answer_memory_query(query)
        
        # CPU queries
        if any(word in query for word in ['cpu', 'processor', 'process']):
            return self._answer_cpu_query(query)
        
        # Process termination
        if any(word in query for word in ['kill', 'terminate', 'stop', 'close']):
            return self._answer_termination_query()
        
        # Health/Status queries
        if any(word in query for word in ['health', 'status', 'problem', 'issue']):
            return self._answer_health_query()
        
        # Generic fallback
        return self._generic_response(query)
    
    def _answer_disk_query(self, query: str) -> str:
        """Answer disk-related questions."""
        # Extract disk info from context
        if "LARGEST DIRECTORIES" in self.context_data:
            match = re.search(r'LARGEST DIRECTORIES.*?\n(.*?)(?=\n\n|\Z)', self.context_data, re.DOTALL)
            if match:
                dirs = match.group(1).strip()
                return f"Based on the disk scan, here are the largest directories:\n\n{dirs}\n\nThese folders are consuming the most storage space on your system."
        
        # Fallback to disk usage summary
        if "DISK STORAGE SUMMARY" in self.context_data:
            match = re.search(r'DISK STORAGE SUMMARY.*?\n(.*?)(?=LARGEST|$)', self.context_data, re.DOTALL)
            if match:
                summary = match.group(1).strip()
                return f"Disk Storage Overview:\n\n{summary}"
        
        return "Please run a disk scan on the Dashboard to see which folders are using the most space."
    
    def _answer_memory_query(self, query: str) -> str:
        """Answer memory-related questions."""
        # 1. Check for specific process usage from "TOP MEMORY CONSUMERS" section
        if "TOP MEMORY CONSUMERS" in self.context_data:
             # Extract the top list
             match = re.search(r'TOP MEMORY CONSUMERS:\n(.*?)(?=\n\n|\Z)', self.context_data, re.DOTALL)
             if match and ("top" in query or "most" in query or "process" in query or "app" in query):
                 top_list = match.group(1).strip()
                 return f"Here are the top memory consumers:\n\n{top_list}"

        # Check for process-specific memory questions
        if "app" in query or "program" in query or "application" in query:
            # Try to extract process info from process-specific context
            if "PROCESS DETAILS" in self.context_data:
                match = re.search(r'Name:\s*(\S+).*?Memory:\s*(\d+\.?\d*)\s*MB', self.context_data, re.DOTALL)
                if match:
                    name, mem = match.groups()
                    return f"**{name}** is currently using **{mem} MB** of RAM."
            
            # If no specific process context, give general answer
            return "To see specific memory usage, check the 'TOP MEMORY CONSUMERS' list above or go to the Performance tab."
        
        # System-wide memory questions
        if "Memory:" in self.context_data:
            match = re.search(r'Memory:\s*\n\s*-\s*Current:\s*(\d+\.?\d*)%.*?Average:\s*(\d+\.?\d*)%.*?Peak:\s*(\d+\.?\d*)%', self.context_data, re.DOTALL)
            if match:
                current, avg, peak = match.groups()
                response = f"**System Memory Usage:**\n• Current: **{current}%**\n• Average: **{avg}%**\n• Peak: **{peak}%**"
                
                # Check for high usage
                if float(current) > 85:
                    response += "\n\n⚠️ **Memory usage is high!** Consider closing unnecessary applications."
                
                return response
        
        return "Memory information is available in the Dashboard. Check the real-time metrics there."
    
    def _answer_cpu_query(self, query: str) -> str:
        """Answer CPU-related questions."""
        if "CPU:" in self.context_data:
            match = re.search(r'CPU:\s*\n\s*-\s*Current:\s*(\d+\.?\d*)%.*?Average:\s*(\d+\.?\d*)%.*?Peak:\s*(\d+\.?\d*)%.*?High Usage Events.*?:\s*(\d+)', self.context_data, re.DOTALL)
            if match:
                current, avg, peak, events = match.groups()
                response = f"CPU Status:\n• Current usage: {current}%\n• Average: {avg}%\n• Peak: {peak}%\n• High usage spikes: {events} times"
                
                if float(current) > 80:
                    response += "\n\n⚠️ CPU usage is high! Check the Performance tab to see which processes are consuming resources."
                
                return response
        
        return "CPU information is available in the Dashboard. Check real-time metrics there."
    
    def _answer_termination_query(self) -> str:
        """Answer process termination questions."""
        return "To terminate a process:\n1. Go to the Performance tab\n2. Find the process in the list\n3. Click the ⋮ (three dots) menu\n4. Select 'Terminate process'\n5. Confirm the action\n\n⚠️ Be careful when terminating processes - it may cause data loss."
    
    def _answer_health_query(self) -> str:
        """Answer system health questions."""
        # Look for health data in context
        if "System Health" in self.context_data or "SYSTEM NORMAL" in self.context_data:
            return "Your system health appears to be normal based on current metrics. The health indicator on the Dashboard shows the overall status."
        
        return "System health is monitored continuously. Check the badge on the Dashboard for current status."
    
    def _generic_response(self, query: str) -> str:
        """Generic fallback response."""
        return f"I understand you're asking about: '{query}'\n\nI can help with:\n• Disk storage analysis\n• Memory usage questions\n• CPU performance\n• Process management\n• System health status\n\nPlease ask a more specific question, or check the Dashboard for real-time metrics."
