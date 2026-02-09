from django import forms
from django.contrib.auth.models import User
from quit_smoking_webapp.models import UserProfile, DailyLog, Emotion, Situation
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

class RegisterForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput()
    )

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Repeat password",
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ["username", "email"]

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")

        return email

    def clean(self):
        cleaned_data = super().clean()

        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")

        if p1 and p2:
            if p1 != p2:
                raise forms.ValidationError("Passwords do not match")

            try:
                validate_password(p1)
            except ValidationError as e:
                self.add_error("password1", e)

        return cleaned_data
    

class StartingPointForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['cigarettes_per_day', 'pack_price', 'reason_to_quit', 'reminder_enabled']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['cigarettes_per_day'].label = "How many cigarettes per day do you smoke?"
        self.fields['pack_price'].label = "Price of one pack of cigarettes"
        self.fields['reason_to_quit'].label = "Why do you want to quit smoking?"
        self.fields['reminder_enabled'].label = "Do you want to receive reminders?"


class UserProfileForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Your password",
        widget=forms.PasswordInput,
        required=False
    )
    password2 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput,
        required=False
    )
    password3 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = UserProfile
        fields = ['cigarettes_per_day', 'pack_price', 'reason_to_quit', 'reminder_enabled']

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        self.fields['cigarettes_per_day'].label = "How many cigarettes per day do you smoke?"
        self.fields['pack_price'].label = "Price of one pack of cigarettes"
        self.fields['reason_to_quit'].label = "Why do you want to quit smoking?"
        self.fields['reminder_enabled'].label = "Do you want to receive reminders?"

    def clean(self):
        cleaned_data = super().clean()

        current = cleaned_data.get("password1")
        p1 = cleaned_data.get("password2")
        p2 = cleaned_data.get("password3")

        if not current and not p1 and not p2:
            return cleaned_data

        if not current or not p1 or not p2:
            raise forms.ValidationError("Fill all password fields to change password.")

        if not self.user.check_password(current):
            raise forms.ValidationError("Current password is incorrect.")

        if p1 != p2:
            raise forms.ValidationError("New passwords do not match.")

        validate_password(p1, self.user)


class DailyLogForm(forms.ModelForm):
    emotions = forms.ModelMultipleChoiceField(
        queryset=Emotion.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required = True
    )

    situations = forms.ModelMultipleChoiceField(
        queryset=Situation.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required = True
    )

    class Meta:
        model = DailyLog
        fields = ['cigarettes_smoked', 'smoke_free_day', 'first_cigarette_time', 'craving_level']

        widgets = {
            'first_cigarette_time': forms.TimeInput(attrs={'type': 'time'})
        }


class SendPasswordResetLinkForm(forms.Form):
    email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput()
    )


class ResetPasswordForm(forms.Form):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label="Repeat password",
        widget=forms.PasswordInput
    )

    def clean(self):
            cleaned_data = super().clean()

            p1 = cleaned_data.get("password1")
            p2 = cleaned_data.get("password2")

            if p1 and p2 and p1 != p2:
                raise forms.ValidationError("Passwords do not match")
            
            try:
                validate_password(p1)
            except ValidationError as e:
                self.add_error("password1", e)

            return cleaned_data