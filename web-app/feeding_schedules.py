"""
Feeding Schedule Suggestions
Smart feeding interval recommendations based on species, age, and feeding history
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

# Species-specific feeding intervals (in days)
# Format: species_name: {age_category: (min_days, max_days, recommended_days)}
FEEDING_SCHEDULES = {
    # Snakes
    "Ball Python": {
        "hatchling": (5, 7, 5),      # Every 5-7 days, recommend 5
        "juvenile": (7, 10, 7),       # Every 7-10 days, recommend 7
        "sub-adult": (10, 14, 10),    # Every 10-14 days, recommend 10
        "adult": (14, 21, 14),        # Every 14-21 days, recommend 14
    },
    "Corn Snake": {
        "hatchling": (5, 7, 5),
        "juvenile": (7, 10, 7),
        "sub-adult": (10, 14, 10),
        "adult": (14, 21, 14),
    },
    "Boa Constrictor": {
        "hatchling": (5, 7, 5),
        "juvenile": (7, 10, 7),
        "sub-adult": (10, 14, 10),
        "adult": (14, 28, 14),
    },
    "King Snake": {
        "hatchling": (5, 7, 5),
        "juvenile": (7, 10, 7),
        "sub-adult": (10, 14, 10),
        "adult": (14, 21, 14),
    },
    "Milk Snake": {
        "hatchling": (5, 7, 5),
        "juvenile": (7, 10, 7),
        "sub-adult": (10, 14, 10),
        "adult": (14, 21, 14),
    },
    "Carpet Python": {
        "hatchling": (5, 7, 5),
        "juvenile": (7, 10, 7),
        "sub-adult": (10, 14, 10),
        "adult": (14, 21, 14),
    },
    
    # Lizards
    "Bearded Dragon": {
        "hatchling": (1, 1, 1),       # Daily
        "juvenile": (1, 2, 1),        # Daily to every other day
        "sub-adult": (2, 3, 2),       # Every 2-3 days
        "adult": (2, 3, 2),           # Every 2-3 days
    },
    "Leopard Gecko": {
        "hatchling": (1, 2, 1),
        "juvenile": (2, 3, 2),
        "sub-adult": (3, 4, 3),
        "adult": (3, 4, 3),
    },
    "Crested Gecko": {
        "hatchling": (1, 2, 1),
        "juvenile": (2, 3, 2),
        "sub-adult": (3, 4, 3),
        "adult": (3, 4, 3),
    },
    "Blue Tongue Skink": {
        "hatchling": (2, 3, 2),
        "juvenile": (3, 4, 3),
        "sub-adult": (4, 5, 4),
        "adult": (5, 7, 5),
    },
    
    # Default for unknown species
    "default": {
        "hatchling": (5, 7, 7),
        "juvenile": (7, 10, 7),
        "sub-adult": (10, 14, 10),
        "adult": (14, 21, 14),
    }
}


def get_age_category(date_of_birth: Optional[str]) -> str:
    """
    Determine age category based on date of birth
    Returns: hatchling, juvenile, sub-adult, or adult
    """
    if not date_of_birth:
        return "adult"  # Default to adult if no DOB
    
    try:
        dob = datetime.strptime(date_of_birth, '%Y-%m-%d')
        age_days = (datetime.now() - dob).days
        age_months = age_days / 30.44  # Average days per month
        
        if age_months < 6:
            return "hatchling"
        elif age_months < 12:
            return "juvenile"
        elif age_months < 24:
            return "sub-adult"
        else:
            return "adult"
    except:
        return "adult"


def get_feeding_interval(species: str, date_of_birth: Optional[str] = None) -> Tuple[int, int, int]:
    """
    Get feeding interval for a species and age
    Returns: (min_days, max_days, recommended_days)
    """
    age_category = get_age_category(date_of_birth)
    
    # Find species in database (case-insensitive partial match)
    species_lower = species.lower()
    for species_key in FEEDING_SCHEDULES.keys():
        if species_key.lower() in species_lower or species_lower in species_key.lower():
            schedule = FEEDING_SCHEDULES[species_key]
            if age_category in schedule:
                return schedule[age_category]
            # Fallback to adult if age category not found
            return schedule.get("adult", FEEDING_SCHEDULES["default"]["adult"])
    
    # Use default schedule if species not found
    return FEEDING_SCHEDULES["default"][age_category]


def suggest_next_feeding_date(species: str, last_feeding_date: str, 
                              date_of_birth: Optional[str] = None,
                              feeding_history: Optional[list] = None) -> Dict:
    """
    Suggest next feeding date based on species, age, and feeding history
    
    Args:
        species: Reptile species
        last_feeding_date: Date of last feeding (YYYY-MM-DD)
        date_of_birth: Date of birth (YYYY-MM-DD)
        feeding_history: List of recent feeding logs
    
    Returns:
        Dict with suggestion details
    """
    min_days, max_days, recommended_days = get_feeding_interval(species, date_of_birth)
    
    # Parse last feeding date
    last_fed = datetime.strptime(last_feeding_date, '%Y-%m-%d')
    
    # Calculate based on feeding history if available
    if feeding_history and len(feeding_history) >= 3:
        # Calculate average interval from recent feedings
        intervals = []
        for i in range(len(feeding_history) - 1):
            date1 = datetime.strptime(feeding_history[i]['feeding_date'], '%Y-%m-%d')
            date2 = datetime.strptime(feeding_history[i + 1]['feeding_date'], '%Y-%m-%d')
            intervals.append(abs((date1 - date2).days))
        
        if intervals:
            avg_interval = sum(intervals) / len(intervals)
            # Use average if it's within reasonable range
            if min_days <= avg_interval <= max_days:
                recommended_days = round(avg_interval)
    
    # Calculate suggested date
    suggested_date = last_fed + timedelta(days=recommended_days)
    earliest_date = last_fed + timedelta(days=min_days)
    latest_date = last_fed + timedelta(days=max_days)
    
    # Calculate days until feeding
    days_until = (suggested_date - datetime.now()).days
    
    # Determine status
    if days_until < 0:
        status = "overdue"
        status_message = f"Overdue by {abs(days_until)} day{'s' if abs(days_until) != 1 else ''}"
    elif days_until == 0:
        status = "today"
        status_message = "Feed today"
    elif days_until == 1:
        status = "tomorrow"
        status_message = "Feed tomorrow"
    elif days_until <= 2:
        status = "soon"
        status_message = f"Feed in {days_until} days"
    else:
        status = "scheduled"
        status_message = f"Feed in {days_until} days"
    
    age_category = get_age_category(date_of_birth)
    
    return {
        "suggested_date": suggested_date.strftime('%Y-%m-%d'),
        "earliest_date": earliest_date.strftime('%Y-%m-%d'),
        "latest_date": latest_date.strftime('%Y-%m-%d'),
        "days_until": days_until,
        "status": status,
        "status_message": status_message,
        "recommended_interval": recommended_days,
        "interval_range": f"{min_days}-{max_days} days",
        "age_category": age_category,
        "confidence": "high" if feeding_history and len(feeding_history) >= 3 else "medium"
    }


def get_feeding_recommendation(reptile: Dict, feeding_logs: list) -> Optional[Dict]:
    """
    Get feeding recommendation for a reptile
    
    Args:
        reptile: Reptile dictionary with species, date_of_birth, etc.
        feeding_logs: List of feeding logs for this reptile
    
    Returns:
        Recommendation dict or None if no feeding history
    """
    if not feeding_logs:
        # No feeding history, provide basic recommendation
        min_days, max_days, recommended_days = get_feeding_interval(
            reptile['species'], 
            reptile.get('date_of_birth')
        )
        age_category = get_age_category(reptile.get('date_of_birth'))
        
        return {
            "suggested_date": None,
            "recommended_interval": recommended_days,
            "interval_range": f"{min_days}-{max_days} days",
            "age_category": age_category,
            "status": "no_history",
            "status_message": f"Recommended: Every {recommended_days} days",
            "confidence": "low"
        }
    
    # Get last feeding
    last_feeding = feeding_logs[0]
    
    return suggest_next_feeding_date(
        species=reptile['species'],
        last_feeding_date=last_feeding['feeding_date'],
        date_of_birth=reptile.get('date_of_birth'),
        feeding_history=feeding_logs[:10]  # Use last 10 feedings
    )

# Made with Bob
