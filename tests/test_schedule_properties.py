"""
Property-based tests for Schedule data model.

Feature: calendar-aggregator, Property 4: Event data preservation invariant
Validates: Requirements 1.4
"""
import pytest
from hypothesis import given, strategies as st
from datetime import datetime, timedelta
from models.schedule import Schedule


# Hypothesis strategies for generating test data
@st.composite
def schedule_strategy(draw):
    """
    Generate random but valid Schedule instances.
    
    Returns:
        Randomly generated Schedule object
    """
    # Generate random datetime within reasonable range
    base_time = datetime(2025, 1, 1)
    days_offset = draw(st.integers(min_value=0, max_value=365))
    hours_offset = draw(st.integers(min_value=0, max_value=23))
    minutes_offset = draw(st.integers(min_value=0, max_value=59))
    
    start_time = base_time + timedelta(
        days=days_offset,
        hours=hours_offset,
        minutes=minutes_offset
    )
    
    # End time is 1-4 hours after start
    duration_hours = draw(st.integers(min_value=1, max_value=4))
    end_time = start_time + timedelta(hours=duration_hours)
    
    # Generate other fields
    event_id = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        blacklist_characters='\x00'
    )))
    
    title = draw(st.text(min_size=1, max_size=100, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd', 'P', 'Zs'),
        blacklist_characters='\x00'
    )))
    
    description = draw(st.one_of(
        st.none(),
        st.text(min_size=0, max_size=500, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'P', 'Zs'),
            blacklist_characters='\x00'
        ))
    ))
    
    provider = draw(st.sampled_from(['gmail', 'outlook', 'yahoo', 'apple']))
    
    location = draw(st.one_of(
        st.none(),
        st.text(min_size=0, max_size=200, alphabet=st.characters(
            whitelist_categories=('Lu', 'Ll', 'Nd', 'P', 'Zs'),
            blacklist_characters='\x00'
        ))
    ))
    
    # Generate 0-5 attendees
    num_attendees = draw(st.integers(min_value=0, max_value=5))
    attendees = [
        f"user{i}@example.com"
        for i in range(num_attendees)
    ]
    
    return Schedule(
        id=event_id,
        title=title,
        description=description,
        start_time=start_time,
        end_time=end_time,
        provider=provider,
        location=location,
        attendees=attendees
    )


class TestScheduleDataPreservation:
    """
    Property-based tests for Schedule data preservation.
    
    Feature: calendar-aggregator, Property 4: Event data preservation invariant
    """
    
    @given(schedule=schedule_strategy())
    def test_schedule_to_dict_preserves_all_fields(self, schedule):
        """
        Property: For any schedule, converting to dict and back preserves all fields.
        
        This tests that serialization/deserialization maintains data integrity.
        
        Feature: calendar-aggregator, Property 4: Event data preservation invariant
        Validates: Requirements 1.4
        """
        # Convert to dict
        schedule_dict = schedule.to_dict()
        
        # Verify all fields are present in dict
        assert 'id' in schedule_dict
        assert 'title' in schedule_dict
        assert 'description' in schedule_dict
        assert 'start_time' in schedule_dict
        assert 'end_time' in schedule_dict
        assert 'provider' in schedule_dict
        assert 'location' in schedule_dict
        assert 'attendees' in schedule_dict
        
        # Convert back from dict
        restored_schedule = Schedule.from_dict(schedule_dict)
        
        # Verify all fields are preserved
        assert restored_schedule.id == schedule.id
        assert restored_schedule.title == schedule.title
        assert restored_schedule.description == schedule.description
        assert restored_schedule.start_time == schedule.start_time
        assert restored_schedule.end_time == schedule.end_time
        assert restored_schedule.provider == schedule.provider
        assert restored_schedule.location == schedule.location
        assert restored_schedule.attendees == schedule.attendees
    
    @given(schedule=schedule_strategy())
    def test_schedule_field_immutability_after_dict_conversion(self, schedule):
        """
        Property: For any schedule, dict conversion doesn't modify original.
        
        This ensures that serialization is a pure operation with no side effects.
        
        Feature: calendar-aggregator, Property 4: Event data preservation invariant
        Validates: Requirements 1.4
        """
        # Store original values
        original_id = schedule.id
        original_title = schedule.title
        original_description = schedule.description
        original_start = schedule.start_time
        original_end = schedule.end_time
        original_provider = schedule.provider
        original_location = schedule.location
        original_attendees = schedule.attendees.copy()
        
        # Convert to dict (should not modify original)
        _ = schedule.to_dict()
        
        # Verify original is unchanged
        assert schedule.id == original_id
        assert schedule.title == original_title
        assert schedule.description == original_description
        assert schedule.start_time == original_start
        assert schedule.end_time == original_end
        assert schedule.provider == original_provider
        assert schedule.location == original_location
        assert schedule.attendees == original_attendees
    
    @given(schedule=schedule_strategy())
    def test_schedule_datetime_precision_preserved(self, schedule):
        """
        Property: For any schedule, datetime precision is preserved through serialization.
        
        This ensures time information is not lost during conversion.
        
        Feature: calendar-aggregator, Property 4: Event data preservation invariant
        Validates: Requirements 1.4
        """
        # Convert to dict and back
        schedule_dict = schedule.to_dict()
        restored_schedule = Schedule.from_dict(schedule_dict)
        
        # Verify datetime precision (should be exact)
        assert restored_schedule.start_time == schedule.start_time
        assert restored_schedule.end_time == schedule.end_time
        
        # Verify the time difference is preserved
        original_duration = schedule.end_time - schedule.start_time
        restored_duration = restored_schedule.end_time - restored_schedule.start_time
        assert original_duration == restored_duration
