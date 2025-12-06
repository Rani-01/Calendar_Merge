"""
ViewType enum for calendar view periods.
"""
from enum import Enum


class ViewType(Enum):
    """
    Enum representing different calendar view time periods.
    
    Values:
        DAILY: Current day only
        WEEKLY: Current week (7 consecutive days starting from today)
        MONTHLY: Current month
    """
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    
    @classmethod
    def from_string(cls, value: str) -> 'ViewType':
        """
        Create ViewType from string value.
        
        Args:
            value: String representation of view type
            
        Returns:
            ViewType enum value
            
        Raises:
            ValueError: If value is not a valid view type
        """
        try:
            return cls(value.lower())
        except ValueError:
            valid_values = [v.value for v in cls]
            raise ValueError(
                f"Invalid view type: {value}. Must be one of {valid_values}"
            )
