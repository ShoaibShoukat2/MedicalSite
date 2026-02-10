# Chat Flow Debug Guide

## Current Setup:

### Patient Side:
1. Patient goes to `/patient-dashboard/chat/`
2. Sees list of practitioners
3. Clicks on practitioner → Redirects to `/chat/room/{id}/`
4. Uses chat interface to send messages

### Practitioner Side:
1. Practitioner goes to `/practitioner-dashboard/chat/`
2. Sees list of patients
3. Clicks on patient → Redirects to `/chat/room/{id}/`
4. Uses chat interface to send messages

### Backend:
- `/chat/send-message/` - POST endpoint (working)
- `/chat/get-messages/{id}/` - GET endpoint (working)
- Messages saved to database with sender_type and sender_id

## Possible Issues:

### Issue 1: Messages not appearing for the other user
**Cause:** No real-time updates, only polling
**Solution:** Need to implement polling or refresh

### Issue 2: Session not persisting
**Cause:** Session data lost
**Solution:** Check session middleware

### Issue 3: Wrong room_id
**Cause:** Multiple chat rooms created
**Solution:** Check ChatRoom.objects.get_or_create logic

## Testing Steps:

1. **Check if message is saved:**
   - Open Django admin
   - Go to Chat → Messages
   - Check if practitioner's message is there

2. **Check sender_type:**
   - Message should have sender_type='practitioner'
   - Message should have correct sender_id

3. **Check if patient can see it:**
   - Patient opens same chat room
   - Should see practitioner's message
   - If not, check get_messages_http function

4. **Check polling:**
   - Is polling implemented?
   - Is it calling get_messages_http?
   - Is it updating the UI?
