from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from user_account.models import Patient
class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['greeting', 'first_name', 'last_name', 'gender', 
                 'mobile_phone', 'date_of_birth', 'email', 'profile_photo']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'greeting': forms.Select(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1234567890'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
        }

class PatientPasswordForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')

        if new_password1 and new_password2 and new_password1 != new_password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return cleaned_data


from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'feedback']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-select'}),
            'feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Share your experience with this practitioner'}),
        }