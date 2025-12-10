# Contributing to Reptile Tracker

First off, thank you for considering contributing to Reptile Tracker! It's people like you that make this tool better for the reptile keeping community.

## Code of Conduct

This project and everyone participating in it is governed by respect and professionalism. By participating, you are expected to uphold this standard.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples** to demonstrate the steps
- **Describe the behavior you observed** and what you expected
- **Include screenshots** if relevant
- **Include your environment details**: OS, Python version, etc.

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description** of the suggested enhancement
- **Explain why this enhancement would be useful**
- **List any similar features** in other applications if applicable

### Pull Requests

1. Fork the repository
2. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. Make your changes
4. Test your changes thoroughly
5. Commit your changes with clear commit messages:
   ```bash
   git commit -m "Add feature: description of what you added"
   ```
6. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
7. Open a Pull Request

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/reptile-tracker.git
   cd reptile-tracker
   ```

2. Run the application:
   ```bash
   python3 reptile_tracker.py
   ```

3. Make your changes and test thoroughly

## Coding Standards

### Python Style Guide

- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and concise
- Comment complex logic

### Example:

```python
def calculate_feeding_success_rate(total_feedings: int, successful_feedings: int) -> float:
    """
    Calculate the feeding success rate as a percentage.
    
    Args:
        total_feedings: Total number of feeding attempts
        successful_feedings: Number of successful feedings
    
    Returns:
        Success rate as a percentage (0-100)
    """
    if total_feedings == 0:
        return 0.0
    return (successful_feedings / total_feedings) * 100
```

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests after the first line

Examples:
```
Add weight tracking graph feature

- Implement matplotlib integration
- Add graph view to reptile details page
- Update database schema for weight history
Fixes #123
```

## Project Structure

```
reptile-tracker/
├── reptile_tracker.py          # Main GUI application
├── reptile_tracker_db.py       # Database management
├── REPTILE_TRACKER_README.md   # User documentation
├── README.md                   # Project overview
├── CONTRIBUTING.md             # This file
├── LICENSE                     # MIT License
├── requirements.txt            # Dependencies
├── .gitignore                  # Git ignore rules
└── sample_*.csv                # Sample data files
```

## Testing

Before submitting a pull request:

1. Test all existing features to ensure nothing broke
2. Test your new feature thoroughly
3. Test on different operating systems if possible
4. Test with various data scenarios

### Manual Testing Checklist

- [ ] Application starts without errors
- [ ] Can add a new reptile
- [ ] Can edit reptile information
- [ ] Can delete a reptile
- [ ] Can add feeding logs
- [ ] Can add shed records
- [ ] Can import CSV data
- [ ] Can export CSV data
- [ ] Dashboard displays correctly
- [ ] Statistics calculate correctly
- [ ] All navigation works properly

## Feature Ideas

Here are some features that would be great additions:

### High Priority
- **Automated Notification Scheduler** - Set up APScheduler or cron jobs for automatic daily reminder emails/SMS
- **Health Records & Vet Visits** - Track medical history, medications, and veterinary appointments
- **Temperature & Humidity Logging** - Monitor and log enclosure conditions with graphs
- **Breeding Records** - Track breeding attempts, egg laying, incubation, and genetics

### Medium Priority
- **Expense Tracking** - Log costs for food, supplies, vet visits, and equipment
- **Multiple Enclosures** - Manage and track multiple terrariums/enclosures
- **Feeding Calculator** - Calculate appropriate prey size based on reptile weight/age
- **Growth Rate Analysis** - Analyze and predict growth patterns with ML
- **Medication Reminders** - Track medication schedules and dosages
- **QR Code Labels** - Generate QR codes for enclosures that link to reptile profiles

### Low Priority
- **Mobile-Responsive PWA** - Progressive Web App for mobile devices
- **Multi-User Support** - Family/team access with different permission levels
- **Integration with Smart Devices** - Connect to smart thermostats, cameras, etc.
- **Social Features** - Share reptile profiles, connect with other keepers
- **Dark/Light Theme Toggle** - User preference for interface theme
- **Multi-Language Support** - Internationalization for global users
- **Voice Commands** - "Hey Reptile Tracker, when did I last feed my snake?"
- **AI-Powered Insights** - Predictive analytics for health issues or feeding patterns

## Documentation

When adding new features:

1. Update the main README.md if needed
2. Update REPTILE_TRACKER_README.md with usage instructions
3. Add docstrings to new functions and classes
4. Update sample CSV files if data format changes

## Questions?

Feel free to open an issue with the "question" label if you need help or clarification on anything.

## Recognition

Contributors will be recognized in the project README. Thank you for your contributions!

---

**Thank you for contributing to Reptile Tracker!** 🦎