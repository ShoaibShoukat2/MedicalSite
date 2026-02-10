# Debug: Chat Auto-Close Issue

## Problem:
When practitioner sends message:
1. Chat window closes automatically
2. Message doesn't send

## Possible Causes:

### 1. Form Submission Causing Page Reload
**Check:** Is `e.preventDefault()` working?
**Solution:** Ensure event listener is properly attached

### 2. JavaScript Error Breaking Execution
**Check:** Browser console for errors
**Solution:** Fix any JavaScript errors

### 3. Navigation/Redirect Issue
**Check:** Network tab for unexpected redirects
**Solution:** Remove any redirect code

### 4. Template Inheritance Issue
**Check:** Which template is actually being used
**Solution:** Verify correct template is loaded

## Debug Steps:

### Step 1: Check Browser Console
Open chat room and check console for:
- ✅ "🏥 Chat room initialized"
- ✅ "✅ Chat ready"
- ✅ "🔄 Message polling started"
- ❌ Any error messages

### Step 2: Test Form Submit
1. Type message
2. Click send
3. Check console for:
   - "📤 Sending message: ..."
   - "✅ Message sent"
   - OR error messages

### Step 3: Check Network Tab
1. Open DevTools → Network
2. Send message
3. Look for:
   - POST to `/chat/send-message/`
   - Response status (should be 200)
   - Response data

### Step 4: Check if Event Listener Attached
Add this to console:
```javascript
document.getElementById('chat-form')
// Should return the form element
```

## Quick Fix to Test:

Add this at the end of chat_room_content.html script:
```javascript
// Debug: Log all form submissions
document.addEventListener('submit', function(e) {
    console.log('🔍 Form submitted:', e.target.id);
    console.log('🔍 Default prevented:', e.defaultPrevented);
}, true);
```

## Expected Behavior:
1. User types message
2. User clicks send (or presses Enter)
3. Form submit event fires
4. `e.preventDefault()` stops page reload
5. `sendMessage()` function called
6. AJAX request sent
7. Message added to UI
8. Input cleared
9. Chat stays open ✅
