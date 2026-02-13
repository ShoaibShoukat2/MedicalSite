# Cancel Button Logic - Complete Explanation

## 🎯 Cancel Button KAB Show Hoga?

Cancel button show hone ke liye **2 CONDITIONS** dono TRUE honi chahiye:

---

## ✅ Condition 1: Appointment Status

```python
appointment.status != 'Cancelled'
```

### Matlab:
- ✅ Status = "Pending" → Button SHOW hoga
- ✅ Status = "Accepted" → Button SHOW hoga  
- ✅ Status = "Confirmed" → Button SHOW hoga
- ❌ Status = "Cancelled" → Button NAHI dikhega

**Simple Rule**: Agar appointment already cancelled nahi hai, to button show hoga.

---

## ✅ Condition 2: Time Remaining

```python
time_until_appointment >= timedelta(hours=2)
```

### Matlab:
Appointment se **kam se kam 2 hours pehle** hona chahiye.

### Examples:

#### ✅ Button SHOW Hoga:
```
Current Time: 8:00 AM
Appointment: 12:00 PM (Noon)
Difference: 4 hours
Result: ✅ Cancel button ACTIVE
```

```
Current Time: 8:00 AM
Appointment: 10:00 AM
Difference: 2 hours (exactly)
Result: ✅ Cancel button ACTIVE
```

```
Current Time: Monday 9:00 AM
Appointment: Tuesday 10:00 AM
Difference: 25 hours
Result: ✅ Cancel button ACTIVE
```

#### ❌ Button DISABLED Hoga:
```
Current Time: 8:30 AM
Appointment: 10:00 AM
Difference: 1.5 hours
Result: ⚠️ "Too Late to Cancel" (Gray button)
```

```
Current Time: 9:00 AM
Appointment: 10:00 AM
Difference: 1 hour
Result: ⚠️ "Too Late to Cancel" (Gray button)
```

```
Current Time: 9:45 AM
Appointment: 10:00 AM
Difference: 15 minutes
Result: ⚠️ "Too Late to Cancel" (Gray button)
```

---

## 📊 Complete Logic Table

| Appointment Status | Time Until Appointment | Cancel Button |
|-------------------|------------------------|---------------|
| Pending | 24 hours | ✅ SHOW (Active) |
| Pending | 5 hours | ✅ SHOW (Active) |
| Pending | 2 hours | ✅ SHOW (Active) |
| Pending | 1.5 hours | ⚠️ SHOW (Disabled) |
| Pending | 30 minutes | ⚠️ SHOW (Disabled) |
| **Accepted** | 24 hours | ✅ SHOW (Active) |
| **Accepted** | 5 hours | ✅ SHOW (Active) |
| **Accepted** | 2 hours | ✅ SHOW (Active) |
| **Accepted** | 1.5 hours | ⚠️ SHOW (Disabled) |
| **Confirmed** | 24 hours | ✅ SHOW (Active) |
| **Confirmed** | 5 hours | ✅ SHOW (Active) |
| **Confirmed** | 2 hours | ✅ SHOW (Active) |
| **Confirmed** | 1.5 hours | ⚠️ SHOW (Disabled) |
| Cancelled | Any time | ❌ HIDE (No button) |
| Completed | Any time | ❌ HIDE (No button) |

---

## 🔄 Real-World Scenario

### Scenario 1: Patient Books Appointment
```
Time: Monday 9:00 AM
Appointment: Wednesday 10:00 AM
Status: Pending
Time Until: 49 hours

Cancel Button: ✅ SHOW (Red, Active)
Patient Can: Click and cancel
```

---

### Scenario 2: Doctor Confirms Appointment
```
Time: Monday 2:00 PM
Appointment: Wednesday 10:00 AM
Status: Accepted ← CHANGED!
Time Until: 44 hours

Cancel Button: ✅ STILL SHOW (Red, Active)
Patient Can: Still click and cancel
```

**KEY POINT**: Doctor ke confirm karne se button NAHI hata!

---

### Scenario 3: Day Before Appointment
```
Time: Tuesday 9:00 AM
Appointment: Wednesday 10:00 AM
Status: Accepted
Time Until: 25 hours

Cancel Button: ✅ STILL SHOW (Red, Active)
Patient Can: Still cancel
```

---

### Scenario 4: 3 Hours Before
```
Time: Wednesday 7:00 AM
Appointment: Wednesday 10:00 AM
Status: Accepted
Time Until: 3 hours

Cancel Button: ✅ STILL SHOW (Red, Active)
Patient Can: Still cancel
```

---

### Scenario 5: 2 Hours Before (Exactly)
```
Time: Wednesday 8:00 AM
Appointment: Wednesday 10:00 AM
Status: Accepted
Time Until: 2 hours (exactly)

Cancel Button: ✅ STILL SHOW (Red, Active)
Patient Can: Still cancel (at the limit)
```

---

### Scenario 6: 1.5 Hours Before (TOO LATE!)
```
Time: Wednesday 8:30 AM
Appointment: Wednesday 10:00 AM
Status: Accepted
Time Until: 1.5 hours

Cancel Button: ⚠️ SHOW but DISABLED (Gray)
Text: "Too Late to Cancel"
Patient Can: Cannot cancel (button disabled)
Tooltip: "Cannot cancel - less than 2 hours before appointment"
```

---

### Scenario 7: Patient Cancels
```
Time: Tuesday 9:00 AM
Appointment: Wednesday 10:00 AM
Status: Cancelled ← CHANGED!
Time Until: 25 hours

Cancel Button: ❌ HIDE (No button at all)
Patient Can: Nothing (already cancelled)
Shows: "Cancelled on Tuesday, Jan 14 at 9:00 AM"
```

---

## 💻 Actual Code Logic

### Backend (views.py):
```python
for appointment in all_appointments:
    # Calculate time until appointment
    appointment_datetime = datetime.combine(
        appointment.slot.date, 
        appointment.slot.start_time
    )
    appointment_datetime = timezone.make_aware(appointment_datetime)
    time_until_appointment = appointment_datetime - current_time
    
    # Set can_cancel flag
    appointment.can_cancel = (
        appointment.status != 'Cancelled' and      # Condition 1
        time_until_appointment >= timedelta(hours=2)  # Condition 2
    )
```

### Frontend (template):
```html
{% if appointment.status != 'Cancelled' %}
    {% if appointment.can_cancel %}
        <!-- ACTIVE BUTTON -->
        <button class="cancel-btn" data-id="{{ appointment.id }}">
            <i class="fas fa-times mr-2"></i>Cancel
        </button>
    {% else %}
        <!-- DISABLED BUTTON -->
        <button disabled class="px-4 py-2 border border-gray-300 text-gray-500 rounded-lg cursor-not-allowed" 
                title="Cannot cancel - less than 2 hours before appointment">
            <i class="fas fa-clock mr-2"></i>Too Late to Cancel
        </button>
    {% endif %}
{% endif %}
```

---

## 🎨 Visual States

### State 1: Active Cancel Button (Green Light ✅)
```
Conditions:
- Status != Cancelled ✅
- Time >= 2 hours ✅

Appearance:
- Color: Red (#dc2626)
- Border: 1px solid red
- Background: White
- Cursor: Pointer (hand)
- Hover: Red background, white text
- Text: "Cancel"
- Icon: ❌

Action: Clickable, opens modal
```

---

### State 2: Disabled Button (Yellow Light ⚠️)
```
Conditions:
- Status != Cancelled ✅
- Time < 2 hours ❌

Appearance:
- Color: Gray (#9ca3af)
- Border: 1px solid gray
- Background: Light gray (#f3f4f6)
- Cursor: Not-allowed (🚫)
- Hover: No change
- Text: "Too Late to Cancel"
- Icon: 🕐

Action: Not clickable, shows tooltip
```

---

### State 3: No Button (Red Light ❌)
```
Conditions:
- Status = Cancelled ❌

Appearance:
- No button at all
- Shows cancellation info instead

Action: Nothing to click
```

---

## 🕐 Timeline Visualization

```
Appointment Time: 10:00 AM
                                    ↓
├────────────────┼────────┼────────┼────────┤
48h before      24h      2h       Now      After
                         ↑
                    Critical Point

├────────────────┴────────┴────────┤
│   CAN CANCEL (Button Active)     │
│   ✅ Green Zone                   │
                         ├─────────┴────────┤
                         │  CANNOT CANCEL   │
                         │  ⚠️ Red Zone      │
```

---

## 🔍 Important Points

### 1. Status Does NOT Matter (Except Cancelled)
```
❌ WRONG THINKING:
"Doctor ne confirm kar diya, ab cancel nahi kar sakte"

✅ CORRECT THINKING:
"Jab tak 2 hours pehle hai, cancel kar sakte hain"
```

### 2. Only Time Matters
```
Status: Pending, Accepted, Confirmed → Same treatment
Only check: Is it 2+ hours before appointment?
```

### 3. 2-Hour Rule is Strict
```
2 hours 1 minute before → ✅ Can cancel
2 hours exactly → ✅ Can cancel
1 hour 59 minutes before → ❌ Cannot cancel
```

### 4. Already Cancelled = No Button
```
Once cancelled → Button disappears forever
Cannot "un-cancel" an appointment
```

---

## 🧪 Quick Test

Want to test? Check these:

### Test 1: Book appointment for tomorrow
**Expected**: Cancel button shows (active) ✅

### Test 2: Ask doctor to confirm
**Expected**: Cancel button STILL shows (active) ✅

### Test 3: Book appointment for 1 hour from now
**Expected**: "Too Late to Cancel" (disabled) ⚠️

### Test 4: Cancel any appointment
**Expected**: Button disappears ❌

---

## 📝 Summary

### Cancel Button Shows When:
1. ✅ Appointment NOT cancelled
2. ✅ At least 2 hours before appointment

### Cancel Button Active When:
1. ✅ Both conditions above met
2. ✅ Patient can click and cancel

### Cancel Button Disabled When:
1. ✅ Appointment NOT cancelled
2. ❌ Less than 2 hours before appointment
3. ⚠️ Shows "Too Late to Cancel"

### Cancel Button Hidden When:
1. ❌ Appointment already cancelled
2. ❌ No button at all

---

## 🎯 Final Answer

**Cancel button HAMESHA show hoga** jab tak:
- Appointment cancelled nahi hai
- Appointment se 2+ hours pehle hai

**Doctor ka confirm karna button ko affect NAHI karta!**

---

**Last Updated**: January 2026
**Status**: ✅ Fully Explained
