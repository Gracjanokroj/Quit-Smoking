import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(_("Password must contain at least one uppercase letter."))
        if not re.search(r'[a-z]', password):
            raise ValidationError(_("Password must contain at least one lowercase letter."))
        if not re.search(r'[0-9]', password):
            raise ValidationError(_("Password must contain at least one digit."))

    def get_help_text(self):
        return _("Your password must contain at least one uppercase letter, one lowercase letter, and one digit.")
