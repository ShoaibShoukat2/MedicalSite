from django.urls import path
from . import avatar_views

urlpatterns = [
    path('generate-avatar-response/', avatar_views.generate_avatar_response, name='generate_avatar_response'),
    path('get-idle-avatar/', avatar_views.get_idle_avatar, name='get_idle_avatar'),
    path('pregenerate-common-responses/', avatar_views.pregenerate_common_responses, name='pregenerate_common_responses'),
]