from django.apps import AppConfig


class PatientdashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'patientdashboard'



class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'patientdashboard'

    def ready(self):
        import patientdashboard.signals


