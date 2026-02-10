# Practitioner Chat System - Testing Guide

## Pre-requisites:
✅ Django server running
✅ Database with test data
✅ At least one practitioner and one patient with accepted appointment

---

## Test 1: Access Practitioner Chat Page

### Steps:
1. Start Django server:
   ```bash
   python manage.py runserver
   ```

2. Login as Practitioner:
   - Go to: `http://localhost:8000/practitioner/login/`
   - Enter practitioner credentials
   - Should redirect to dashboard

3. Navigate to Chat:
   - Go to: `http://localhost:8000/practitioner-dashboard/chat/`
   - OR click "Chat" in sidebar menu

### Expected Result:
✅ Page loads successfully
✅ Shows list of patients (if any chats exist)
✅ OR shows "No Patient Conversations Yet" message
✅ Shows available patients with accepted appointments

### Possible Issues:
❌ **500 Error:** Check practitioner_id in session
❌ **Template Error:** Check if chat.html exists
❌ **No Patients:** Need accepted appointments first

---

## Test 2: Open Chat Room

### Steps:
1. From practitioner chat page
2. Click on a patient card
3. Should redirect to: `http://localhost:8000/chat/room/{id}/`

### Expected Result:
✅ Chat room opens
✅ Shows patient name in header
✅ Shows previous messages (if any)
✅ Message input box visible
✅ Send button visible

### Browser Console Should Show:
```
🏥 Chat room initialized
✅ Chat ready
🔄 Message polling started (every 3 seconds)
```

### Possible Issues:
❌ **404 Error:** Chat room doesn't exist
❌ **403 Error:** No permission to access chat
❌ **Blank Page:** Check JavaScript errors in console

---

## Test 3: Send Message to Patient

### Steps:
1. In chat room, type a message: "Hello, this is a test message"
2. Click send button (or press Enter)
3. Watch browser console

### Expected Result:
✅ Message appears immediately in chat
✅ Message has blue background (practitioner color)
✅ Shows timestamp
✅ Shows checkmark icon

### Browser Console Should Show:
```
📤 Sending message: Hello, this is a test message...
✅ Message sent
✅ Message sent successfully
```

### Possible Issues:
❌ **Message not sending:** Check CSRF token
❌ **Error in console:** Check network tab for failed request
❌ **Message disappears:** Check database if message was saved

---

## Test 4: Verify Message in Database

### Steps:
1. Open Django admin: `http://localhost:8000/admin/`
2. Go to: Chat → Messages
3. Find the latest message

### Expected Result:
✅ Message exists in database
✅ `sender_type` = 'practitioner'
✅ `sender_id` = {practitioner_id}
✅ `chat_room_id` = {correct room id}
✅ `content` = "Hello, this is a test message"
✅ `timestamp` = current time

---

## Test 5: Patient Receives Message (Polling Test)

### Steps:
1. Keep practitioner chat open
2. Open new browser/incognito window
3. Login as patient
4. Go to: `http://localhost:8000/patient-dashboard/chat/`
5. Click on same practitioner
6. Wait 3 seconds

### Expected Result:
✅ Patient sees practitioner's message within 3 seconds
✅ Message has gray background (received message)
✅ Shows correct timestamp
✅ Shows practitioner name

### Browser Console Should Show (Patient Side):
```
🏥 Chat room initialized
✅ Chat ready
🔄 Message polling started (every 3 seconds)
📨 1 new message(s) received
```

### Possible Issues:
❌ **Message not appearing:** Check if polling is running
❌ **Console errors:** Check network tab
❌ **Wrong message:** Check sender_type in database

---

## Test 6: Two-Way Conversation

### Steps:
1. Practitioner sends: "How are you feeling today?"
2. Wait 3 seconds
3. Patient sees message
4. Patient replies: "I'm feeling better, thank you!"
5. Wait 3 seconds
6. Practitioner sees reply

### Expected Result:
✅ Both messages appear correctly
✅ Practitioner messages = blue background
✅ Patient messages = gray background
✅ Correct timestamps
✅ Messages in correct order
✅ Both users see all messages

### Browser Console Should Show:
**Practitioner Side:**
```
📨 1 new message(s) received
```

**Patient Side:**
```
📨 1 new message(s) received
```

---

## Test 7: Multiple Messages Rapidly

### Steps:
1. Send 5 messages quickly:
   - "Message 1"
   - "Message 2"
   - "Message 3"
   - "Message 4"
   - "Message 5"

### Expected Result:
✅ All 5 messages appear
✅ Correct order maintained
✅ All saved to database
✅ Other user sees all 5 messages

---

## Test 8: Polling Pause/Resume

### Steps:
1. Open chat room
2. Switch to another tab (hide chat tab)
3. Wait 10 seconds
4. Switch back to chat tab

### Expected Result:
✅ Polling stops when tab hidden
✅ Console shows: "⏸️ Message polling stopped"
✅ Polling resumes when tab active
✅ Console shows: "🔄 Message polling started (every 3 seconds)"
✅ New messages load immediately

---

## Test 9: Start New Chat

### Steps:
1. Go to practitioner chat page
2. If no existing chats, should see available patients
3. Click on a patient card
4. Should create new chat room

### Expected Result:
✅ New chat room created
✅ Redirects to `/chat/room/{new_id}/`
✅ Empty chat (no previous messages)
✅ Can send messages

### Browser Console Should Show:
```
Creating chat...
(redirect to chat room)
```

---

## Test 10: Error Handling

### Test 10a: Send Empty Message
1. Click send without typing anything
2. **Expected:** Nothing happens, no error

### Test 10b: Network Error
1. Disconnect internet
2. Try to send message
3. **Expected:** Error message shown

### Test 10c: Invalid Chat Room
1. Go to: `http://localhost:8000/chat/room/99999/`
2. **Expected:** Error page or redirect

---

## Performance Checks:

### Network Tab (Chrome DevTools):
1. Open chat room
2. Open DevTools → Network tab
3. Watch for requests

**Expected:**
- Every 3 seconds: GET `/chat/get-messages/{id}/`
- Response size: ~1-2 KB
- Response time: <100ms
- Status: 200 OK

### Console Logs:
```
🏥 Chat room initialized
✅ Chat ready
🔄 Message polling started (every 3 seconds)
📤 Sending message: ...
✅ Message sent
✅ Message sent successfully
📨 1 new message(s) received
```

---

## Common Issues & Solutions:

### Issue 1: "Not authenticated" error
**Solution:** Check if practitioner_id exists in session
```python
# In Django shell
from django.contrib.sessions.models import Session
# Check session data
```

### Issue 2: Polling not working
**Solution:** Check browser console for errors
- Verify `/chat/get-messages/{id}/` endpoint works
- Check if JavaScript is enabled
- Clear browser cache

### Issue 3: Messages not appearing
**Solution:** 
- Check database if message was saved
- Verify sender_type and sender_id
- Check if chat_room_id is correct
- Verify polling is running

### Issue 4: CSRF token error
**Solution:**
- Check if CSRF middleware is enabled
- Verify CSRF token in cookies
- Check if getCookie function works

### Issue 5: Template not found
**Solution:**
- Verify file exists: `practitionerdashboard/templates/practitionerdashboard/chat.html`
- Check TEMPLATES setting in settings.py
- Run `python manage.py collectstatic`

---

## Quick Test Commands:

### Check if server is running:
```bash
curl http://localhost:8000/
```

### Check if chat endpoint exists:
```bash
curl http://localhost:8000/practitioner-dashboard/chat/
```

### Check if API endpoint works:
```bash
curl -X POST http://localhost:8000/chat/send-message/ \
  -H "Content-Type: application/json" \
  -d '{"room_id": 1, "message": "test"}'
```

---

## Success Criteria:

✅ Practitioner can access chat page
✅ Practitioner can see list of patients
✅ Practitioner can open chat room
✅ Practitioner can send messages
✅ Messages save to database correctly
✅ Patient receives messages within 3 seconds
✅ Two-way conversation works smoothly
✅ Polling works correctly
✅ No JavaScript errors
✅ No server errors
✅ Professional UI appearance

---

## Final Verification:

Run this complete test scenario:

1. **Setup:**
   - Start server
   - Login as practitioner
   - Login as patient (different browser)

2. **Test Flow:**
   - Practitioner opens chat
   - Patient opens same chat
   - Practitioner sends: "Hello"
   - Patient sees it (within 3 seconds)
   - Patient replies: "Hi doctor"
   - Practitioner sees it (within 3 seconds)
   - Continue conversation for 5 messages each

3. **Verify:**
   - All 10 messages visible to both
   - Correct colors (blue/gray)
   - Correct timestamps
   - Correct order
   - No errors in console
   - Smooth experience

**If all above works: ✅ CHAT SYSTEM IS WORKING PERFECTLY!**
