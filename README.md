# 🦎 Reptile Tracker

A comprehensive desktop application for tracking reptile care, feeding schedules, shed records, and health information.

![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

## 📸 Features

- **🦎 Multi-Reptile Management** - Track unlimited reptiles with detailed profiles
- **🍖 Feeding Logs** - Record what you feed, when, and whether they ate
- **🔄 Shed Tracking** - Monitor shed cycles and completeness
- **📊 Statistics & Analytics** - View feeding success rates and health trends
- **📥📤 Import/Export** - CSV support for bulk data management
- **🎨 Modern GUI** - Clean, intuitive dark-themed interface

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or higher
- tkinter (usually comes with Python)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/reptile-tracker.git
cd reptile-tracker
```

2. Run the application:
```bash
python3 reptile_tracker.py
```

That's it! The database will be created automatically on first run.

### For macOS Users

If you encounter tkinter issues:
```bash
brew install python-tk
```

## 📖 Documentation

For detailed documentation, see [REPTILE_TRACKER_README.md](REPTILE_TRACKER_README.md)

### Quick Guide

1. **Add a Reptile**: Click "🦎 Add Reptile" → Fill in details → Save
2. **Log Feeding**: Click "Add Feeding" on reptile card → Enter details → Save
3. **Record Shed**: Open reptile details → Click "+ Add Shed" → Save
4. **Import Data**: Use sample CSV files as templates → File → Import CSV

## 📁 Project Structure

```
reptile-tracker/
├── reptile_tracker.py              # Main GUI application
├── reptile_tracker_db.py           # Database management module
├── REPTILE_TRACKER_README.md       # Comprehensive user guide
├── sample_reptiles_import.csv      # Example reptile data
├── sample_feeding_logs_import.csv  # Example feeding log data
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

## 🎯 Key Features

### Reptile Management
- Store detailed information: name, species, morph, sex, DOB, weight, length
- Automatic age calculation
- Individual profile pages with complete history
- Add custom notes for each reptile

### Feeding Tracking
- Log feeding date, food type, size, and quantity
- Track acceptance/refusal
- Calculate feeding success rates
- View complete feeding history

### Shed Tracking
- Record shed dates and completeness
- Monitor shed cycles
- Track shed problems
- Add detailed notes

### Dashboard & Analytics
- Overview of all reptiles
- Quick statistics cards
- "Needs Feeding" alerts
- Recent activity summaries
- Individual reptile statistics

### Data Management
- Import reptiles and feeding logs from CSV
- Export all data for backup or analysis
- Sample CSV templates included
- Automatic data type detection

## 💾 Database Schema

The application uses SQLite with the following tables:

- **reptiles** - Basic reptile information and details
- **feeding_logs** - Complete feeding history
- **shed_records** - Shed cycle tracking
- **weight_history** - Weight measurements over time

## 🔧 Technology Stack

- **Language**: Python 3
- **GUI Framework**: tkinter
- **Database**: SQLite3
- **Data Format**: CSV for import/export

## 📊 Screenshots

### Dashboard View
The main dashboard shows all your reptiles with quick stats and recent activity.

### Reptile Details
Detailed profile pages show complete history, statistics, and recent records.

### Feeding Logs
Comprehensive feeding history with filtering and search capabilities.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Ideas for Contributions

- Weight tracking graphs and visualizations
- Photo gallery for each reptile
- Veterinary visit tracking
- Temperature/humidity logging
- Breeding records
- Mobile app companion
- Cloud backup integration
- Multi-language support

## 🐛 Bug Reports

Found a bug? Please open an issue with:
- Description of the problem
- Steps to reproduce
- Expected behavior
- Screenshots (if applicable)
- Your operating system and Python version

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with Python and tkinter
- Inspired by the need for better reptile care tracking
- Thanks to the reptile keeping community

## 📧 Contact

For questions or suggestions, please open an issue on GitHub.

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

**Happy Reptile Keeping! 🦎🐍🦴**

Made with ❤️ for responsible reptile owners