from django.core import validators
from django.utils.translation import gettext_lazy as _


class PhoneNumberValidator(validators.RegexValidator):
    # regex = r"^(?:\d{3}-\d{3}-\d{4}|\(\d{3}\) \d{3}-\d{4})$"
    regex = r"^\+\d{1,15}$"
    message = _("Enter a valid phone number in the format XXX-XXX-XXXX or (XXX) XXX-XXXX.")
    flags = 0
