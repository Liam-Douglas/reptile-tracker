# Alert Banner System Documentation

## Overview
A full-width notification banner system that displays alerts for overdue feedings and low/out-of-stock inventory items on the Reptiles page.

## Implementation Date
December 16, 2025

## Features Implemented

### 1. Alert Banner
- **Location**: Top of Reptiles page, outside main container for full-width display
- **Style**: Zendesk-inspired design with softer red/brown color (#a85751)
- **Layout**: Single-line text with icon, message, and action buttons
- **Functionality**:
  - Displays total alert count
  - Shows specific alert types (low inventory, overdue feedings)
  - "View Details" button opens modal with full alert list
  - "X" button dismisses banner
  - Fixed position at top of page

### 2. Alert Modal
- **Trigger**: Clicking "View Details" button
- **Content Sections**:
  - Overdue Feedings: Shows reptiles with missed feeding schedules
  - Out of Stock: Items with 0 quantity
  - Low Stock: Items with quantity ≤ 5
- **Features**:
  - Each alert item is clickable
  - Links to relevant pages (reptile details or finance page)
  - Dark, readable text colors
  - Close button and click-outside-to-close functionality

### 3. Backend Logic
- **File**: `web-app/app.py`
- **Route**: `/reptiles` (reptiles_page function)
- **Data Fetching**:
  ```python
  inventory = db.get_food_inventory()
  low_stock = [item for item in inventory if 0 < item['quantity'] <= 5]
  out_of_stock = [item for item in inventory if item['quantity'] == 0]
  overdue_feedings = db.get_overdue_feedings()
  total_alerts = len(overdue_feedings) + len(low_stock) + len(out_of_stock)
  ```
- **Debug Logging**: Prints alert counts to server logs

## File Structure

### Modified Files
1. **web-app/app.py** (lines 335-357)
   - Added inventory alert logic
   - Passes alert data to template

2. **web-app/templates/base.html** (line 188)
   - Added `{% block alert_banner %}` before main container

3. **web-app/templates/reptiles.html** (lines 5-26, 28-118)
   - Alert banner HTML in new block
   - Alert modal HTML with sections
   - JavaScript functions (lines 1183-1200)

4. **web-app/static/css/style.css** (lines 3838-3988)
   - Alert banner styles
   - Alert modal styles
   - Mobile responsive styles

## Technical Details

### CSS Classes
- `.alert-banner` - Main banner container (fixed position, full width)
- `.alert-banner-container` - Content wrapper with padding
- `.alert-banner-content` - Left side (icon + text)
- `.alert-banner-text` - Text content
- `.alert-banner-actions` - Right side (buttons)
- `.alert-banner-btn` - View Details button
- `.alert-banner-close` - Close (X) button
- `.alert-section` - Modal section container
- `.alert-section-title` - Section heading
- `.alert-items` - Alert items container
- `.alert-item` - Individual alert card
- `.alert-item-icon` - Circular icon with gradient
- `.alert-item-title` - Alert title (e.g., "Rat - Large")
- `.alert-item-subtitle` - Alert details (e.g., "2 remaining")

### JavaScript Functions
```javascript
showAlertModal()      // Opens alert modal
closeAlertModal()     // Closes alert modal
dismissAlertBanner()  // Hides banner
```

### Color Scheme
- Banner background: `#a85751` (softer red/brown)
- Text: White on banner, dark (#1f2937) in modal
- Icons: Gradient backgrounds (orange for low stock, red for out of stock)

## Alert Thresholds
- **Low Stock**: Quantity > 0 AND ≤ 5
- **Out of Stock**: Quantity = 0
- **Overdue Feeding**: Based on feeding reminder schedule

## Known Issues & Limitations

### Current Issues
1. **CSS Caching**: Browser may cache old styles
   - **Solution**: Added cache-busting parameter `?v=20251216` to CSS link
   - **Workaround**: Hard refresh (Ctrl+Shift+R / Cmd+Shift+R)

2. **Inline Style Override**: Banner color uses `!important` to force display
   - **Location**: `reptiles.html` line 8
   - **Reason**: Bypass CSS caching issues

### Limitations
1. Banner only appears on Reptiles page
2. No persistent dismissal (reappears on page reload)
3. No notification preferences/settings
4. No email/push notifications

## Future Recommendations

### High Priority
1. **Persistent Banner Dismissal**
   - Store dismissal state in session or database
   - Add "Don't show again today" option
   - Implement user preferences for alert types

2. **Expand to Other Pages**
   - Show banner on all pages when alerts exist
   - Add page-specific alert filtering
   - Create global alert counter in navigation

3. **Enhanced Alert Types**
   - Upcoming feedings (within 24-48 hours)
   - Shed cycle reminders
   - Tank cleaning overdue
   - Weight tracking alerts (significant changes)
   - Temperature/humidity alerts (if sensors added)

4. **Alert Customization**
   - User-defined thresholds for low stock
   - Custom alert priorities
   - Snooze functionality
   - Alert categories (critical, warning, info)

### Medium Priority
5. **Notification System**
   - Email notifications for critical alerts
   - SMS/push notifications (via service like Twilio)
   - Daily/weekly alert digest emails
   - Notification preferences per alert type

6. **Alert History**
   - Log when alerts were triggered
   - Track alert resolution
   - Alert analytics dashboard
   - Export alert history

7. **Improved UI/UX**
   - Animated alert count badge
   - Sound notifications (optional)
   - Alert severity indicators (color-coded)
   - Quick actions from alert items (e.g., "Mark as fed")

8. **Mobile Optimization**
   - Swipe to dismiss on mobile
   - Bottom sheet modal on mobile devices
   - Native app notifications (if mobile app developed)

### Low Priority
9. **Advanced Features**
   - Alert scheduling (quiet hours)
   - Multi-user alert assignments
   - Alert escalation rules
   - Integration with calendar apps
   - Webhook support for external integrations

10. **Performance Optimization**
    - Cache alert calculations
    - Lazy load alert modal content
    - Implement WebSocket for real-time updates
    - Background job for alert processing

## Testing Checklist

### Functional Testing
- [ ] Banner appears when alerts exist
- [ ] Banner hidden when no alerts
- [ ] View Details button opens modal
- [ ] Close button dismisses banner
- [ ] Modal displays correct alert counts
- [ ] Alert items link to correct pages
- [ ] Click outside modal closes it
- [ ] Mobile responsive layout works

### Data Testing
- [ ] Low stock detection (≤5 items)
- [ ] Out of stock detection (0 items)
- [ ] Overdue feeding detection
- [ ] Correct total alert count
- [ ] Alert details display correctly

### Browser Testing
- [ ] Chrome/Edge
- [ ] Firefox
- [ ] Safari
- [ ] Mobile browsers

## Maintenance Notes

### Regular Checks
1. Monitor server logs for DEBUG output
2. Verify alert thresholds are appropriate
3. Check for false positives/negatives
4. Review user feedback on alert usefulness

### Code Locations for Updates
- **Alert Logic**: `web-app/app.py` lines 340-352
- **Banner HTML**: `web-app/templates/reptiles.html` lines 5-26
- **Modal HTML**: `web-app/templates/reptiles.html` lines 28-118
- **Styles**: `web-app/static/css/style.css` lines 3838-3988
- **JavaScript**: `web-app/templates/reptiles.html` lines 1183-1200

## Support & Troubleshooting

### Common Issues

**Banner not appearing:**
1. Check server logs for DEBUG output
2. Verify `total_alerts > 0`
3. Check if banner is being rendered in HTML source
4. Clear browser cache

**Wrong color displaying:**
1. Hard refresh browser (Ctrl+Shift+R)
2. Check inline style in HTML
3. Verify CSS file version parameter

**Modal not opening:**
1. Check browser console for JavaScript errors
2. Verify `showAlertModal()` function exists
3. Check if modal HTML is present in page

**Incorrect alert counts:**
1. Review database inventory quantities
2. Check feeding reminder schedules
3. Verify threshold logic in app.py

## Version History
- **v1.0** (2025-12-16): Initial implementation
  - Full-width banner
  - Alert modal with sections
  - Low stock and overdue feeding detection
  - Mobile responsive design

## Contributors
- Bob (AI Assistant) - Implementation
- Liam Douglas - Requirements & Testing