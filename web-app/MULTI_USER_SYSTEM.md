# Multi-User & Household System Documentation

## Overview
The Reptile Tracker now supports multiple users sharing reptile collections through a household system. This enables couples, families, or roommates to collaboratively track their reptiles and receive notifications on all their devices.

## Architecture

### Database Schema

#### Users Table
- `id`: Primary key
- `email`: Unique email address (used for login)
- `password_hash`: Bcrypt hashed password
- `name`: Display name
- `is_active`: Account status
- `created_at`: Registration timestamp
- `last_login`: Last login timestamp

#### Households Table
- `id`: Primary key
- `name`: Household name (e.g., "Smith Family Reptiles")
- `created_by`: User ID of creator
- `created_at`: Creation timestamp

#### Household Members Table
- `id`: Primary key
- `household_id`: Reference to household
- `user_id`: Reference to user
- `role`: 'owner' or 'member'
- `joined_at`: Join timestamp
- **Unique constraint**: (household_id, user_id)

#### Push Subscriptions Table (Updated)
- `id`: Primary key
- `user_id`: Reference to user (who owns this device)
- `device_name`: Friendly device name
- `subscription_json`: Web push subscription data
- `user_agent`: Browser/device info
- `created_at`: Registration timestamp
- `last_used`: Last notification sent timestamp

#### Reptiles Table (Updated)
- Added `household_id`: Reference to household
- All reptiles belong to a household
- All household members can view/edit

## User Flow

### 1. Registration & First Login
```
User visits app → Register with email/password → 
Create default household → Redirect to dashboard
```

### 2. Inviting Partner/Family Member
```
User A: Settings → Household → Generate invite code →
Share code with User B →
User B: Register → Enter invite code → 
Join User A's household → See shared reptiles
```

### 3. Device Registration
```
User logs in on new device → 
Browser requests notification permission →
Device registers push subscription →
Linked to user account →
User receives notifications on all their devices
```

### 4. Notification Distribution
```
Feeding reminder triggers →
Scheduler finds all household members →
Gets all devices for each member →
Sends push notification to each device →
All household members notified on all their devices
```

## Features

### Shared Data
- ✅ All reptiles visible to all household members
- ✅ All feeding logs, shed records, expenses shared
- ✅ Collaborative tracking and updates
- ✅ Real-time sync across devices

### Individual Settings
- ✅ Each user has their own login
- ✅ Each user can have multiple devices
- ✅ Notification preferences per user
- ✅ Personal notification history

### Security
- ✅ Password hashing with Bcrypt
- ✅ Session management with Flask-Login
- ✅ Household isolation (can't see other households' data)
- ✅ Invite-only household joining

## Implementation Status

### ✅ Completed
- Database schema design
- User and household tables
- Push subscription linking to users

### 🔄 In Progress
- User authentication routes (login, register, logout)
- Household management UI
- Device registration UI
- Migration script for existing data

### 📋 TODO
- Invite code generation system
- Email verification (optional)
- Password reset functionality
- Household settings page
- Member management (remove members, change roles)

## Migration Strategy

### For Existing Users
When updating to the multi-user system:

1. **First user to log in** after update:
   - Prompted to create account
   - All existing reptiles assigned to their household
   - Becomes household owner

2. **Adding partner**:
   - Owner generates invite code
   - Partner registers with invite code
   - Automatically joins household
   - Sees all existing reptiles

3. **Device registration**:
   - Each device prompts for notification permission
   - Links to user account
   - All devices receive notifications

## API Changes

### New Routes
- `POST /auth/register` - Create new user account
- `POST /auth/login` - Authenticate user
- `GET /auth/logout` - End session
- `GET /household` - View household info
- `POST /household/invite` - Generate invite code
- `POST /household/join` - Join with invite code
- `GET /devices` - List user's registered devices
- `DELETE /devices/<id>` - Remove device
- `POST /devices/register` - Register push subscription

### Modified Routes
- All reptile routes now filter by household_id
- Notification routes send to all household members
- Settings routes are user-specific

## Configuration

### Environment Variables
```bash
SECRET_KEY=your-secret-key-here  # For session encryption
DATABASE_URL=sqlite:///reptile_tracker.db
```

### Flask-Login Configuration
```python
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
```

## Testing

### Test Scenarios
1. **Single user**: Register → Add reptiles → Set reminders → Receive notifications
2. **Two users, one household**: User A invites User B → Both see same reptiles → Both receive notifications
3. **Multiple devices**: User logs in on phone and tablet → Both devices receive notifications
4. **Household isolation**: User A and User B in different households → Can't see each other's reptiles

## Future Enhancements

### Planned Features
- [ ] Role-based permissions (owner vs member privileges)
- [ ] Household activity feed
- [ ] Per-reptile notification preferences
- [ ] Guest access (view-only)
- [ ] Multiple households per user
- [ ] Social features (share photos, achievements)

### Advanced Features
- [ ] OAuth login (Google, Apple, Facebook)
- [ ] Two-factor authentication
- [ ] Email notifications for household events
- [ ] Mobile app (React Native)
- [ ] API for third-party integrations

## Support

### Common Issues

**Q: I can't see my partner's reptiles**
A: Ensure you both joined the same household using the invite code.

**Q: Notifications only work on one device**
A: Each device must register for notifications separately. Log in on each device and enable notifications.

**Q: How do I remove someone from my household?**
A: Go to Settings → Household → Members → Remove (owner only).

**Q: Can I be in multiple households?**
A: Currently no, but this feature is planned for future releases.

## Development Notes

### Database Migrations
When deploying updates:
```bash
# Backup existing database
cp reptile_tracker.db reptile_tracker.db.backup

# Run migration script
python migrate_to_multiuser.py

# Verify data integrity
python verify_migration.py
```

### Testing Locally
```bash
# Create test users
python create_test_users.py

# Run development server
flask run --debug

# Test notifications
python test_notifications.py
```

---

**Last Updated**: 2026-01-18
**Version**: 2.0.0
**Author**: Bob (AI Assistant)