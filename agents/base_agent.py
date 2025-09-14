from abc import ABC, abstractmethod
from typing import Dict, List, Any

class BaseAgent(ABC):
    """Base class for all text analysis agents"""
    
    def __init__(self, name: str):
        self.name = name
        
    @abstractmethod
    def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze text and return improvements"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of agent capabilities"""
        pass