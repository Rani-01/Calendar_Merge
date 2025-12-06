"""
Schedule aggregation service.
"""
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple
from models.schedule import Schedule
from models.view_type import ViewType
from providers.base_provider import CalendarProvider


class ScheduleAggregator:
    """
    Aggregates calendar schedules from multiple providers.
    
    Handles retrieval from multiple calendar providers, consolidation,
    and filtering based on time periods.
    """
    
    def __init__(self, providers: List[CalendarProvider]):
        """
        Initialize aggregator with calendar providers.
        
        Args:
            providers: List of calendar provider instances
        """
        self.providers = providers
    
    def get_schedules(self, view_type: ViewType) -> Tuple[List[Schedule], List[str]]:
        """
        Get schedules for the specified view type.
        
        Retrieves events from all configured providers, consolidates them,
        and filters based on the view type (daily/weekly/monthly).
        
        Args:
            view_type: Type of view (DAILY, WEEKLY, or MONTHLY)
            
        Returns:
            Tuple of (schedules list, errors list)
        """
        # Calculate date range based on view type
        start_date, end_date = self._get_date_range(view_type)
        
        # Retrieve from all providers
        all_schedules = []
        errors = []
        
        for provider in self.providers:
            try:
                # Check if provider is available
                if not provider.is_available():
                    errors.append(f"{provider.get_provider_name()} provider: Not available or not configured")
                    continue
                
                # Get events from provider
                schedules = provider.get_events(start_date, end_date)
                all_schedules.extend(schedules)
                
            except Exception as e:
                # Collect error but continue with other providers
                errors.append(f"{provider.get_provider_name()} provider: {str(e)}")
        
        # Filter schedules by date range (handles overlapping events)
        filtered_schedules = self._filter_by_date_range(all_schedules, start_date, end_date)
        
        return filtered_schedules, errors
    
    def _get_date_range(self, view_type: ViewType) -> Tuple[datetime, datetime]:
        """
        Calculate date range for the specified view type.
        
        Args:
            view_type: Type of view
            
        Returns:
            Tuple of (start_date, end_date) - both timezone-aware
        """
        # Use timezone-aware datetime to match Google Calendar API
        now = datetime.now(timezone.utc)
        
        if view_type == ViewType.DAILY:
            # Current day: midnight to 23:59:59
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = now.replace(hour=23, minute=59, second=59, microsecond=999999)
            
        elif view_type == ViewType.WEEKLY:
            # Next 7 days starting from today
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=7)
            
        elif view_type == ViewType.MONTHLY:
            # Current month: first day to last day
            start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            # Calculate last day of month
            if now.month == 12:
                next_month = now.replace(year=now.year + 1, month=1, day=1)
            else:
                next_month = now.replace(month=now.month + 1, day=1)
            
            end_date = next_month - timedelta(microseconds=1)
        
        else:
            raise ValueError(f"Invalid view type: {view_type}")
        
        return start_date, end_date
    
    def _filter_by_date_range(
        self,
        schedules: List[Schedule],
        start_date: datetime,
        end_date: datetime
    ) -> List[Schedule]:
        """
        Filter schedules to include only those that overlap with the date range.
        
        An event overlaps if:
        - It starts before the range ends AND
        - It ends after the range starts
        
        Args:
            schedules: List of schedules to filter
            start_date: Start of date range
            end_date: End of date range
            
        Returns:
            Filtered list of schedules
        """
        filtered = []
        
        for schedule in schedules:
            # Check if event overlaps with the requested period
            # Event overlaps if: event_start < range_end AND event_end > range_start
            if schedule.start_time < end_date and schedule.end_time > start_date:
                filtered.append(schedule)
        
        return filtered
    
    def get_provider_count(self) -> int:
        """
        Get the number of configured providers.
        
        Returns:
            Number of providers
        """
        return len(self.providers)
    
    def get_provider_names(self) -> List[str]:
        """
        Get names of all configured providers.
        
        Returns:
            List of provider names
        """
        return [provider.get_provider_name() for provider in self.providers]
