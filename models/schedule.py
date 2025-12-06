"""
Schedule data model representing a calendar event.
"""
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class Schedule:
    """
    Represents a calendar event from any provider.
    
    Attributes:
        id: Unique identifier for the event
        title: Event title/summary
        description: Optional detailed description
        start_time: Event start datetime
        end_time: Event end datetime
        provider: Source provider (e.g., 'gmail', 'outlook')
        location: Optional event location
        attendees: List of attendee email addresses
    """
    id: str
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    provider: str
    location: Optional[str]
    attendees: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Schedule to dictionary with ISO format datetimes.
        
        Returns:
            Dictionary representation of the schedule
        """
        data = asdict(self)
        data['start_time'] = self.start_time.isoformat()
        data['end_time'] = self.end_time.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schedule':
        """
        Create Schedule from dictionary with ISO format datetimes.
        
        Args:
            data: Dictionary containing schedule data
            
        Returns:
            Schedule instance
        """
        data_copy = data.copy()
        if isinstance(data_copy['start_time'], str):
            data_copy['start_time'] = datetime.fromisoformat(data_copy['start_time'])
        if isinstance(data_copy['end_time'], str):
            data_copy['end_time'] = datetime.fromisoformat(data_copy['end_time'])
        return cls(**data_copy)
