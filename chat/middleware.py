from django.shortcuts import redirect
from django.urls import reverse

class ChatAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/chat/'):
            patient_id = request.session.get('patient_id')
            practitioner_id = request.session.get('practitioner_id')
            
            if not patient_id and not practitioner_id:
                return redirect('login')  # Replace with your login URL

        response = self.get_response(request)
        return response