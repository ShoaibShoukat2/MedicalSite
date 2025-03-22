from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect

def ai_chat_view(request):
    patient_id = request.session.get("patient_id")
    
    if not patient_id:
        return redirect("frontend:patient_login")  # Redirect to login if session is missing

    return render(request, "ai_chat.html", {"patient_id": patient_id})
