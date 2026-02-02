from django.db import models
from user_account.models import Patient, Practitioner
from django.utils import timezone

class SocialSecurityPayment(models.Model):
    """Model for Social Security compliant payments"""
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('reimbursed', 'Reimbursed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('social_security', 'Social Security'),
        ('insurance', 'Insurance'),
        ('private', 'Private Payment'),
        ('copay', 'Co-payment'),
        ('deductible', 'Deductible'),
    ]
    
    # Basic Information
    appointment = models.ForeignKey('patientdashboard.Appointment', on_delete=models.CASCADE, related_name='ss_payments')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    practitioner = models.ForeignKey(Practitioner, on_delete=models.CASCADE)
    
    # Payment Details
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='social_security')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    covered_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Amount covered by SS/Insurance
    patient_copay = models.DecimalField(max_digits=10, decimal_places=2, default=0)   # Patient responsibility
    
    # Social Security Information
    ss_number = models.CharField(max_length=20, blank=True, null=True, help_text="Patient's Social Security Number")
    insurance_number = models.CharField(max_length=50, blank=True, null=True, help_text="Insurance Policy Number")
    insurance_provider = models.CharField(max_length=100, blank=True, null=True)
    
    # Medical Codes (Required for SS compliance)
    diagnosis_code = models.CharField(max_length=20, blank=True, null=True, help_text="ICD-10 Diagnosis Code")
    procedure_code = models.CharField(max_length=20, blank=True, null=True, help_text="CPT Procedure Code")
    service_description = models.TextField(blank=True, null=True)
    
    # Payment Status
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    
    # Compliance Fields
    pre_authorization_code = models.CharField(max_length=50, blank=True, null=True)
    referral_number = models.CharField(max_length=50, blank=True, null=True)
    eligibility_verified = models.BooleanField(default=False)
    eligibility_verification_date = models.DateTimeField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(blank=True, null=True)
    
    # Additional Information
    notes = models.TextField(blank=True, null=True)
    rejection_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Social Security Payment"
        verbose_name_plural = "Social Security Payments"
    
    def __str__(self):
        return f"Payment {self.id} - {self.patient.first_name} {self.patient.last_name} - ${self.total_amount}"
    
    def get_coverage_percentage(self):
        """Calculate coverage percentage"""
        if self.total_amount > 0:
            return (self.covered_amount / self.total_amount) * 100
        return 0
    
    def is_fully_covered(self):
        """Check if payment is fully covered by SS/Insurance"""
        return self.covered_amount >= self.total_amount
    
    def get_remaining_balance(self):
        """Get remaining balance after insurance coverage"""
        return max(0, self.total_amount - self.covered_amount)


class PaymentDocument(models.Model):
    """Model for storing payment-related documents"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('insurance_card', 'Insurance Card'),
        ('ss_card', 'Social Security Card'),
        ('id_verification', 'ID Verification'),
        ('pre_auth', 'Pre-Authorization'),
        ('claim_form', 'Claim Form'),
        ('receipt', 'Payment Receipt'),
        ('eob', 'Explanation of Benefits'),
    ]
    
    payment = models.ForeignKey(SocialSecurityPayment, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    file = models.FileField(upload_to='payment_documents/')
    description = models.CharField(max_length=200, blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.get_document_type_display()} - Payment {self.payment.id}"


class EligibilityVerification(models.Model):
    """Model for tracking insurance/SS eligibility verification"""
    
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('not_eligible', 'Not Eligible'),
        ('expired', 'Expired'),
        ('error', 'Verification Error'),
    ]
    
    payment = models.OneToOneField(SocialSecurityPayment, on_delete=models.CASCADE, related_name='eligibility')
    
    # Verification Details
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS_CHOICES, default='pending')
    verified_at = models.DateTimeField(blank=True, null=True)
    verified_by = models.CharField(max_length=100, blank=True, null=True)  # Staff member who verified
    
    # Coverage Information
    coverage_start_date = models.DateField(blank=True, null=True)
    coverage_end_date = models.DateField(blank=True, null=True)
    coverage_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    deductible_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    deductible_met = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Verification Response
    verification_response = models.JSONField(blank=True, null=True)  # Store API response
    error_message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Eligibility for Payment {self.payment.id} - {self.verification_status}"
    
    def is_currently_eligible(self):
        """Check if patient is currently eligible"""
        if self.verification_status != 'verified':
            return False
        
        today = timezone.now().date()
        if self.coverage_start_date and today < self.coverage_start_date:
            return False
        if self.coverage_end_date and today > self.coverage_end_date:
            return False
        
        return True


class PaymentTransaction(models.Model):
    """Model for tracking individual payment transactions"""
    
    TRANSACTION_TYPE_CHOICES = [
        ('charge', 'Charge'),
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('adjustment', 'Adjustment'),
        ('writeoff', 'Write-off'),
    ]
    
    TRANSACTION_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Credit/Debit Card'),
        ('check', 'Check'),
        ('bank_transfer', 'Bank Transfer'),
        ('insurance', 'Insurance Payment'),
        ('social_security', 'Social Security'),
    ]
    
    payment = models.ForeignKey(SocialSecurityPayment, on_delete=models.CASCADE, related_name='transactions')
    
    # Transaction Details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    transaction_method = models.CharField(max_length=20, choices=TRANSACTION_METHOD_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Reference Information
    reference_number = models.CharField(max_length=100, blank=True, null=True)
    check_number = models.CharField(max_length=50, blank=True, null=True)
    card_last_four = models.CharField(max_length=4, blank=True, null=True)
    
    # Processing Information
    processed_by = models.CharField(max_length=100, blank=True, null=True)
    processed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-processed_at']
    
    def __str__(self):
        return f"{self.transaction_type.title()} - ${self.amount} - {self.processed_at.strftime('%Y-%m-%d')}"


# Existing models (if they don't already exist)
class AvailableSlot(models.Model):
    practitioner = models.ForeignKey(Practitioner, on_delete=models.CASCADE, related_name='available_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, default='available')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['practitioner', 'date', 'start_time']
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"Dr. {self.practitioner.first_name} {self.practitioner.last_name} - {self.date} {self.start_time}-{self.end_time}"


class Prescription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='prescriptions')
    practitioner = models.ForeignKey(Practitioner, on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    prescription_file = models.FileField(upload_to='prescriptions/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Prescription for {self.patient.first_name} {self.patient.last_name} - {self.created_at.strftime('%Y-%m-%d')}"


class PractitionerNotification(models.Model):
    recipient = models.ForeignKey(Practitioner, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, default='info')
    url = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient.first_name} {self.recipient.last_name}"