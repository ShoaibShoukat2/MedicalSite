# Patient Cancel Button - Visual Guide

## Before vs After Fix

### ❌ BEFORE (Incorrect Behavior)
```
Patient books appointment
    ↓
Status: Pending
[Cancel Button] ✅ Visible
    ↓
Practitioner confirms
    ↓
Status: Accepted
[Cancel Button] ❌ DISAPPEARED (BUG!)
    ↓
Patient cannot cancel confirmed appointment
```

### ✅ AFTER (Correct Behavior)
```
Patient books appointment
    ↓
Status: Pending
[Cancel Button] ✅ Visible
    ↓
Practitioner confirms
    ↓
Status: Accepted
[Cancel Button] ✅ STILL VISIBLE (FIXED!)
    ↓
Patient can cancel until 2 hours before
```

## Button States by Scenario

### Scenario 1: Pending Appointment (24 hours away)
```
┌─────────────────────────────────────────────────────────┐
│ Dr. John Smith - Cardiology                             │
│ 📅 Jan 15, 2026  🕐 10:00 AM                           │
│                                                         │
│ Status: [Pending]                                       │
│                                                         │
│ [💳 Pay Now] [🛡️ Insurance] [❌ Cancel]                │
└─────────────────────────────────────────────────────────┘
```
**Cancel Button**: ✅ Active (Red border, clickable)

---

### Scenario 2: Confirmed Appointment (5 hours away)
```
┌─────────────────────────────────────────────────────────┐
│ Dr. John Smith - Cardiology                             │
│ 📅 Jan 15, 2026  🕐 10:00 AM                           │
│                                                         │
│ Status: [Accepted]                                      │
│                                                         │
│ [💬 Chat] [📹 Join Call] [❌ Cancel]                   │
└─────────────────────────────────────────────────────────┘
```
**Cancel Button**: ✅ Active (Red border, clickable)
**Key Point**: Button STILL shows after confirmation!

---

### Scenario 3: Confirmed Appointment (1.5 hours away)
```
┌─────────────────────────────────────────────────────────┐
│ Dr. John Smith - Cardiology                             │
│ 📅 Jan 15, 2026  🕐 10:00 AM                           │
│                                                         │
│ Status: [Accepted]                                      │
│                                                         │
│ [💬 Chat] [📹 Join Call] [🕐 Too Late to Cancel]      │
└─────────────────────────────────────────────────────────┘
```
**Cancel Button**: ⚠️ Disabled (Gray, not clickable)
**Tooltip**: "Cannot cancel - less than 2 hours before appointment"

---

### Scenario 4: Already Cancelled
```
┌─────────────────────────────────────────────────────────┐
│ Dr. John Smith - Cardiology                             │
│ 📅 Jan 15, 2026  🕐 10:00 AM                           │
│                                                         │
│ Status: [Cancelled]                                     │
│ Cancelled on Jan 14, 2026 at 15:30                     │
│                                                         │
│ (No action buttons)                                     │
└─────────────────────────────────────────────────────────┘
```
**Cancel Button**: ❌ Hidden (Already cancelled)

---

## Timeline Visualization

```
Appointment Time: 10:00 AM
Current Time: →

├─────────────┼─────────────┼─────────────┼──────────────┤
24h before    5h before     2h before     Appointment    
                                          Time
├─────────────┴─────────────┴─────────────┤
│     CAN CANCEL (Button Active)          │
                            ├──────────────┴──────────────┤
                            │  CANNOT CANCEL (Too Late)   │
```

### Time-Based Rules:
- **> 2 hours before**: ✅ Cancel button active
- **= 2 hours before**: ✅ Cancel button active (exactly at limit)
- **< 2 hours before**: ❌ "Too Late to Cancel" (disabled)
- **After appointment**: ❌ "Too Late to Cancel" (disabled)

---

## User Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    PATIENT ACTIONS                       │
└─────────────────────────────────────────────────────────┘
                            │
                            ↓
                    [Book Appointment]
                            │
                            ↓
                ┌───────────────────────┐
                │   Status: Pending     │
                │   [Cancel] ✅         │
                └───────────────────────┘
                            │
                            ↓
            ┌───────────────────────────────┐
            │  Practitioner Confirms        │
            └───────────────────────────────┘
                            │
                            ↓
                ┌───────────────────────┐
                │   Status: Accepted    │
                │   [Cancel] ✅         │  ← STILL AVAILABLE!
                └───────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ↓                       ↓
    ┌─────────────────────┐   ┌─────────────────────┐
    │  > 2 hours before   │   │  < 2 hours before   │
    │  [Cancel] ✅        │   │  [Too Late] ❌      │
    └─────────────────────┘   └─────────────────────┘
                │                       │
                ↓                       ↓
    ┌─────────────────────┐   ┌─────────────────────┐
    │  Click Cancel       │   │  Cannot cancel      │
    │  Confirm reason     │   │  Must attend        │
    └─────────────────────┘   └─────────────────────┘
                │
                ↓
    ┌─────────────────────┐
    │  Status: Cancelled  │
    │  No cancel button   │
    └─────────────────────┘
```

---

## Button Styling Reference

### Active Cancel Button
```css
.cancel-btn {
    border: 1px solid #dc2626;  /* Red border */
    color: #dc2626;              /* Red text */
    background: white;
    cursor: pointer;
}

.cancel-btn:hover {
    background: #dc2626;         /* Red background on hover */
    color: white;                /* White text on hover */
}
```

### Disabled "Too Late" Button
```css
.disabled-cancel {
    border: 1px solid #d1d5db;  /* Gray border */
    color: #9ca3af;              /* Gray text */
    background: #f3f4f6;         /* Light gray background */
    cursor: not-allowed;
}
```

---

## Modal Flow

### When Patient Clicks Cancel:
```
┌─────────────────────────────────────────────────────────┐
│              ❌ Cancel Appointment                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Please provide a reason for cancelling:                │
│                                                         │
│  ○ Schedule conflict                                    │
│  ○ Found another doctor                                 │
│  ○ No longer need appointment                           │
│  ○ Personal reasons                                     │
│  ○ Other                                                │
│                                                         │
│  Additional details (optional):                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │                                                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  [Go Back]  [❌ Cancel Appointment]                    │
└─────────────────────────────────────────────────────────┘
```

### Success Message:
```
┌─────────────────────────────────────────────────────────┐
│  ✅ Appointment cancelled successfully                  │
│  You cancelled with sufficient advance notice.          │
└─────────────────────────────────────────────────────────┘
```

### Error Message (Too Late):
```
┌─────────────────────────────────────────────────────────┐
│  ❌ Cancellation denied                                 │
│  You must cancel at least 2 hours before your           │
│  appointment. Only 1.5 hours remaining.                 │
└─────────────────────────────────────────────────────────┘
```

---

## Testing Checklist

### Visual Tests:
- [ ] Cancel button visible on Pending appointments
- [ ] Cancel button visible on Accepted appointments
- [ ] Cancel button visible on Confirmed appointments
- [ ] Cancel button changes to "Too Late" when < 2 hours
- [ ] Cancel button hidden on Cancelled appointments
- [ ] Button styling correct (red border, hover effect)
- [ ] Disabled button styling correct (gray, no hover)

### Functional Tests:
- [ ] Click Cancel opens modal
- [ ] Select reason and confirm cancels appointment
- [ ] Cancellation within 2-hour window is blocked
- [ ] Error message shows time remaining
- [ ] Success message shows after cancellation
- [ ] Practitioner receives notification
- [ ] Appointment moves to Cancelled tab

---

**Status**: ✅ Fully Documented
**Last Updated**: January 2026
