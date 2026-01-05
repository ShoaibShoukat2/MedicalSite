# Appointment Reason and Urgency Implementation

## ✅ **Implementation Complete**

I've successfully integrated the appointment reason and urgency functionality into your existing booking system.

## 🔧 **Changes Made:**

### 1. **Database Model Updates** (`patientdashboard/models.py`)
- Added `reason` field (TextField) to store appointment reason
- Added `urgency` field (CharField) with choices: normal, urgent, emergency
- Default urgency is set to 'normal'

### 2. **Patient Booking Flow** (`patientdashboard/templates/patientdashboard/available_slots.html`)
- **Modal Integration**: Added a booking modal that appears when patient clicks on a time slot
- **Reason Field**: Required textarea for appointment reason
- **Urgency Selection**: Radio buttons with three options:
  - 🟢 **Normal** - Regular consultation
  - 🟡 **Urgent** - Need attention soon  
  - 🔴 **Emergency** - Immediate attention required
- **User-Friendly**: Clear icons and descriptions for each urgency level

### 3. **Backend Processing** (`patientdashboard/views.py`)
- Updated `book_video_consultation()` to handle reason and urgency data
- Added validation to ensure reason is provided
- Store reason and urgency in session during Stripe checkout
- Updated `payment_success()` to save reason and urgency to appointment

### 4. **Practitioner Dashboard** (`practitionerdashboard/templates/practitionerdashboard/dashboard.html`)
- **Enhanced Tables**: Added "Reason" and "Urgency" columns to appointment tables
- **Visual Urgency Indicators**:
  - 🔴 Emergency: Red badge with exclamation circle
  - 🟡 Urgent: Yellow badge with warning triangle  
  - 🟢 Normal: Green badge with clock icon
- **Reason Display**: Shows truncated reason with full text on hover
- **Applied to**: Both pending and accepted appointment tables

### 5. **API Updates** (`practitionerdashboard/views.py`)
- Updated `get_pending_appointments_api()` to include reason and urgency data
- Added urgency display information for frontend components

## 🎯 **How It Works:**

### **For Patients:**
1. Patient selects a time slot
2. Modal opens asking for:
   - Appointment reason (required)
   - Urgency level (normal/urgent/emergency)
3. Patient fills details and clicks "Book Appointment"
4. Proceeds to Stripe payment with reason/urgency stored
5. After payment, appointment is created with all details

### **For Practitioners:**
1. Dashboard shows all appointments with reason and urgency
2. Urgent/Emergency appointments are visually highlighted
3. Can see full reason by hovering over truncated text
4. Urgency badges help prioritize appointments
5. Emergency appointments stand out with red badges

## 📋 **Database Migration Required:**

Run these commands to apply the database changes:

```bash
python manage.py makemigrations patientdashboard
python manage.py migrate
```

## 🎨 **Visual Features:**

- **Urgency Badges**: Color-coded with icons for quick identification
- **Responsive Design**: Works on both desktop and mobile
- **Hover Details**: Full reason text appears on hover
- **Professional UI**: Consistent with existing design system

## 🔒 **Validation:**

- Reason field is required (cannot be empty)
- Urgency defaults to 'normal' if invalid value provided
- Backend validation ensures data integrity
- Frontend validation prevents empty submissions

## 📱 **Mobile Friendly:**

- Modal works perfectly on mobile devices
- Responsive table design for dashboard
- Touch-friendly radio buttons and form elements

The implementation is now complete and ready to use! Patients can specify their appointment reason and urgency level, and practitioners can see this information clearly in their dashboard to prioritize appointments accordingly.