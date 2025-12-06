"""
Property-based tests for ScheduleAggregator.

Feature: calendar-aggregator, Properties 1-5: Aggregation properties
Validates: Requirements 1.1, 1.2, 1.3, 1.5
"""
import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings
from unittest.mock import Mock, MagicMock
from typing import List

from services.schedule_aggregator import ScheduleAggregator
from models.schedule import Schedule
from models.view_type import ViewType
from providers.base_provider import CalendarProvider


@st.composite
def schedule_strategy(draw, provider_name='test'):
    """Generate random schedules."""
    # Use today's date to ensure schedules are in the DAILY view range
    base_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    hours_offset = draw(st.integers(min_value=0, max_value=8))
    
    start_time = base_time + timedelta(hours=hours_offset)
    end_time = start_time + timedelta(hours=draw(st.integers(min_value=1, max_value=2)))
    
    return Schedule(
        id=draw(st.text(min_size=5, max_size=20, alphabet='abcdefghijklmnopqrstuvwxyz0123456789')),
        title=draw(st.text(min_size=1, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ')),
        description=draw(st.one_of(st.none(), st.text(max_size=100))),
        start_time=start_time,
        end_time=end_time,
        provider=provider_name,
        location=draw(st.one_of(st.none(), st.text(max_size=50))),
        attendees=draw(st.lists(st.text(min_size=5, max_size=30), max_size=3))
    )


def create_mock_provider(name: str, schedules: List[Schedule], should_fail: bool = False):
    """Create a mock calendar provider."""
    provider = Mock(spec=CalendarProvider)
    provider.get_provider_name.return_value = name
    provider.is_available.return_value = not should_fail
    
    if should_fail:
        provider.get_events.side_effect = Exception(f"{name} provider: Test error")
    else:
        provider.get_events.return_value = schedules
    
    return provider


class TestMultiProviderRetrievalCompleteness:
    """
    Property-based tests for multi-provider retrieval completeness.
    
    Feature: calendar-aggregator, Property 1: Multi-provider retrieval completeness
    """
    
    @given(
        num_providers=st.integers(min_value=1, max_value=5),
        schedules_per_provider=st.integers(min_value=0, max_value=5)
    )
    @settings(max_examples=100)
    def test_aggregator_attempts_retrieval_from_all_providers(self, num_providers, schedules_per_provider):
        """
        Property: For any set of configured calendar providers, when the system
        receives a schedule request, it should attempt to retrieve events from
        every configured provider.
        
        Feature: calendar-aggregator, Property 1: Multi-provider retrieval completeness
        Validates: Requirements 1.1
        """
        # Create mock providers
        providers = []
        for i in range(num_providers):
            now = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
            schedules = [
                Schedule(
                    id=f"event{j}",
                    title=f"Event {j}",
                    description=None,
                    start_time=now,
                    end_time=now + timedelta(hours=1),
                    provider=f"provider{i}",
                    location=None,
                    attendees=[]
                )
                for j in range(schedules_per_provider)
            ]
            provider = create_mock_provider(f"provider{i}", schedules)
            providers.append(provider)
        
        # Create aggregator
        aggregator = ScheduleAggregator(providers)
        
        # Get schedules
        schedules, errors = aggregator.get_schedules(ViewType.DAILY)
        
        # Verify all providers were called
        for provider in providers:
            provider.is_available.assert_called()
            provider.get_events.assert_called_once()


class TestScheduleConsolidation:
    """
    Property-based tests for schedule consolidation.
    
    Feature: calendar-aggregator, Property 2: Schedule consolidation preserves all events
    """
    
    @given(
        provider1_count=st.integers(min_value=0, max_value=10),
        provider2_count=st.integers(min_value=0, max_value=10)
    )
    @settings(max_examples=100)
    def test_consolidation_preserves_all_schedules(self, provider1_count, provider2_count):
        """
        Property: For any set of schedules returned by multiple providers, the
        consolidated response should contain all schedules from all providers without loss.
        
        Feature: calendar-aggregator, Property 2: Schedule consolidation preserves all events
        Validates: Requirements 1.2
        """
        # Use today's date
        now = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        
        # Create schedules for provider 1
        provider1_schedules = [
            Schedule(
                id=f"p1_event{i}",
                title=f"Provider1 Event {i}",
                description=None,
                start_time=now,
                end_time=now + timedelta(hours=1),
                provider="provider1",
                location=None,
                attendees=[]
            )
            for i in range(provider1_count)
        ]
        
        # Create schedules for provider 2
        provider2_schedules = [
            Schedule(
                id=f"p2_event{i}",
                title=f"Provider2 Event {i}",
                description=None,
                start_time=now,
                end_time=now + timedelta(hours=1),
                provider="provider2",
                location=None,
                attendees=[]
            )
            for i in range(provider2_count)
        ]
        
        # Create mock providers
        provider1 = create_mock_provider("provider1", provider1_schedules)
        provider2 = create_mock_provider("provider2", provider2_schedules)
        
        # Create aggregator
        aggregator = ScheduleAggregator([provider1, provider2])
        
        # Get schedules
        schedules, errors = aggregator.get_schedules(ViewType.DAILY)
        
        # Verify all schedules are present
        assert len(schedules) == provider1_count + provider2_count
        
        # Verify schedules from provider1
        provider1_ids = {s.id for s in schedules if s.provider == "provider1"}
        expected_provider1_ids = {f"p1_event{i}" for i in range(provider1_count)}
        assert provider1_ids == expected_provider1_ids
        
        # Verify schedules from provider2
        provider2_ids = {s.id for s in schedules if s.provider == "provider2"}
        expected_provider2_ids = {f"p2_event{i}" for i in range(provider2_count)}
        assert provider2_ids == expected_provider2_ids


class TestPartialFailureResilience:
    """
    Property-based tests for partial failure resilience.
    
    Feature: calendar-aggregator, Property 3: Partial failure resilience
    """
    
    @given(
        num_working=st.integers(min_value=1, max_value=3),
        num_failing=st.integers(min_value=1, max_value=3)
    )
    @settings(max_examples=100)
    def test_partial_failure_returns_available_schedules(self, num_working, num_failing):
        """
        Property: For any subset of providers that fail, the system should
        successfully return schedules from available providers and include
        error information for failed providers.
        
        Feature: calendar-aggregator, Property 3: Partial failure resilience
        Validates: Requirements 1.3
        """
        # Use today's date
        now = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        
        # Create working providers
        working_providers = []
        for i in range(num_working):
            schedules = [
                Schedule(
                    id=f"working{i}_event0",
                    title=f"Working{i} Event",
                    description=None,
                    start_time=now,
                    end_time=now + timedelta(hours=1),
                    provider=f"working{i}",
                    location=None,
                    attendees=[]
                )
            ]
            provider = create_mock_provider(f"working{i}", schedules, should_fail=False)
            working_providers.append(provider)
        
        # Create failing providers
        failing_providers = []
        for i in range(num_failing):
            provider = create_mock_provider(f"failing{i}", [], should_fail=True)
            failing_providers.append(provider)
        
        # Create aggregator with mixed providers
        all_providers = working_providers + failing_providers
        aggregator = ScheduleAggregator(all_providers)
        
        # Get schedules
        schedules, errors = aggregator.get_schedules(ViewType.DAILY)
        
        # Verify we got schedules from working providers
        assert len(schedules) == num_working
        
        # Verify we got errors for failing providers
        assert len(errors) == num_failing
        
        # Verify error messages identify the failing providers
        for i in range(num_failing):
            assert any(f"failing{i}" in error for error in errors)


class TestDuplicateEventInclusion:
    """
    Property-based tests for duplicate event inclusion.
    
    Feature: calendar-aggregator, Property 5: Duplicate event inclusion
    """
    
    @given(num_duplicates=st.integers(min_value=1, max_value=5))
    @settings(max_examples=100)
    def test_duplicate_events_all_included(self, num_duplicates):
        """
        Property: For any event that appears in multiple providers, all instances
        should be included in the response (no automatic deduplication).
        
        Feature: calendar-aggregator, Property 5: Duplicate event inclusion
        Validates: Requirements 1.5
        """
        # Use today's date
        now = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
        
        # Create the same event across multiple providers
        providers = []
        for i in range(num_duplicates):
            # Same event ID and details, but different provider
            schedule = Schedule(
                id="duplicate_event",
                title="Duplicate Event",
                description="This event appears in multiple calendars",
                start_time=now,
                end_time=now + timedelta(hours=1),
                provider=f"provider{i}",
                location="Conference Room",
                attendees=["user@example.com"]
            )
            provider = create_mock_provider(f"provider{i}", [schedule])
            providers.append(provider)
        
        # Create aggregator
        aggregator = ScheduleAggregator(providers)
        
        # Get schedules
        schedules, errors = aggregator.get_schedules(ViewType.DAILY)
        
        # Verify all duplicate instances are included
        assert len(schedules) == num_duplicates
        
        # Verify all have the same event ID but different providers
        assert all(s.id == "duplicate_event" for s in schedules)
        provider_names = {s.provider for s in schedules}
        expected_providers = {f"provider{i}" for i in range(num_duplicates)}
        assert provider_names == expected_providers



class TestTimeBasedFilteringCorrectness:
    """
    Property-based tests for time-based filtering correctness.
    
    Feature: calendar-aggregator, Property 6: Time-based filtering correctness
    """
    
    @given(
        num_schedules=st.integers(min_value=5, max_value=20),
        view_type=st.sampled_from([ViewType.DAILY, ViewType.WEEKLY, ViewType.MONTHLY])
    )
    @settings(max_examples=100)
    def test_only_overlapping_schedules_included(self, num_schedules, view_type):
        """
        Property: For any set of schedules and any view type (daily/weekly/monthly),
        only schedules whose time ranges overlap with the requested period should
        be included in the filtered results.
        
        Feature: calendar-aggregator, Property 6: Time-based filtering correctness
        Validates: Requirements 2.1, 2.2, 2.3, 2.4
        """
        now = datetime.now()
        
        # Create schedules at various times (some in range, some out of range)
        schedules = []
        for i in range(num_schedules):
            # Create schedules at different offsets from now
            days_offset = i - (num_schedules // 2)  # Some before, some after
            start_time = now + timedelta(days=days_offset, hours=10)
            end_time = start_time + timedelta(hours=1)
            
            schedule = Schedule(
                id=f"event{i}",
                title=f"Event {i}",
                description=None,
                start_time=start_time,
                end_time=end_time,
                provider="test",
                location=None,
                attendees=[]
            )
            schedules.append(schedule)
        
        # Create mock provider
        provider = create_mock_provider("test", schedules)
        aggregator = ScheduleAggregator([provider])
        
        # Get filtered schedules
        filtered_schedules, errors = aggregator.get_schedules(view_type)
        
        # Calculate expected date range
        start_date, end_date = aggregator._get_date_range(view_type)
        
        # Verify all returned schedules overlap with the date range
        for schedule in filtered_schedules:
            # Event overlaps if: event_start < range_end AND event_end > range_start
            assert schedule.start_time < end_date
            assert schedule.end_time > start_date
        
        # Verify no schedules outside the range are included
        for schedule in schedules:
            is_in_range = schedule.start_time < end_date and schedule.end_time > start_date
            is_in_result = schedule in filtered_schedules
            assert is_in_range == is_in_result
    
    @given(view_type=st.sampled_from([ViewType.DAILY, ViewType.WEEKLY, ViewType.MONTHLY]))
    @settings(max_examples=100)
    def test_empty_schedule_list_returns_empty(self, view_type):
        """
        Property: For any view type, when no schedules exist for the requested
        period, an empty schedule list should be returned.
        
        Feature: calendar-aggregator, Property 6: Time-based filtering correctness
        Validates: Requirements 2.5
        """
        # Create provider with no schedules
        provider = create_mock_provider("test", [])
        aggregator = ScheduleAggregator([provider])
        
        # Get schedules
        schedules, errors = aggregator.get_schedules(view_type)
        
        # Should return empty list
        assert schedules == []
        assert len(errors) == 0
    
    @given(
        hours_before_start=st.integers(min_value=1, max_value=24),
        hours_after_end=st.integers(min_value=1, max_value=24)
    )
    @settings(max_examples=100)
    def test_events_outside_range_excluded(self, hours_before_start, hours_after_end):
        """
        Property: For any schedule that doesn't overlap with the requested period,
        it should be excluded from results.
        
        Feature: calendar-aggregator, Property 6: Time-based filtering correctness
        Validates: Requirements 2.1, 2.2, 2.3, 2.4
        """
        now = datetime.now()
        
        # Create schedule before today (should be excluded from DAILY view)
        past_schedule = Schedule(
            id="past_event",
            title="Past Event",
            description=None,
            start_time=now - timedelta(hours=hours_before_start + 24),
            end_time=now - timedelta(hours=hours_before_start + 23),
            provider="test",
            location=None,
            attendees=[]
        )
        
        # Create schedule far in future (should be excluded from DAILY view)
        future_schedule = Schedule(
            id="future_event",
            title="Future Event",
            description=None,
            start_time=now + timedelta(hours=hours_after_end + 24),
            end_time=now + timedelta(hours=hours_after_end + 25),
            provider="test",
            location=None,
            attendees=[]
        )
        
        # Create provider with out-of-range schedules
        provider = create_mock_provider("test", [past_schedule, future_schedule])
        aggregator = ScheduleAggregator([provider])
        
        # Get daily schedules
        schedules, errors = aggregator.get_schedules(ViewType.DAILY)
        
        # Both should be excluded
        assert len(schedules) == 0
