"""
APIResponse data model for consistent API responses.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
from models.schedule import Schedule


@dataclass
class APIResponse:
    """
    Standard API response format for all endpoints.
    
    Attributes:
        success: Whether the request was successful
        data: Optional list of schedules (None on error)
        errors: List of error messages (empty on success)
        timestamp: Response generation timestamp
    """
    success: bool
    data: Optional[List[Schedule]]
    errors: List[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert APIResponse to dictionary for JSON serialization.
        
        Returns:
            Dictionary representation of the response
        """
        return {
            'success': self.success,
            'data': [schedule.to_dict() for schedule in self.data] if self.data else None,
            'errors': self.errors,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def success_response(cls, schedules: List[Schedule]) -> 'APIResponse':
        """
        Create a successful response with schedule data.
        
        Args:
            schedules: List of schedules to include in response
            
        Returns:
            APIResponse with success=True
        """
        return cls(
            success=True,
            data=schedules,
            errors=[],
            timestamp=datetime.utcnow()
        )
    
    @classmethod
    def error_response(cls, errors: List[str], partial_data: Optional[List[Schedule]] = None) -> 'APIResponse':
        """
        Create an error response with optional partial data.
        
        Args:
            errors: List of error messages
            partial_data: Optional partial schedule data if some providers succeeded
            
        Returns:
            APIResponse with success=False
        """
        return cls(
            success=False,
            data=partial_data,
            errors=errors,
            timestamp=datetime.utcnow()
        )
