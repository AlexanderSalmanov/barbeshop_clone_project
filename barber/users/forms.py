from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth import get_user_model

User = get_user_model()

class UserAdminCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = User
        fields = ['email','full_name']

    def clean(self):
        """
        Verify both password match
        """
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_2 = cleaned_data.get('password_2')
        if password is not None and password != password_2:
            self.add_error('password_2', 'Your passwords don\'t match.')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class UserAdminChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ['email', 'full_name', 'active', 'staff', 'admin']

    def clean_password(self):
        return self.initial['password']

class SignUpForm(forms.ModelForm):

    password = forms.CharField(label='Enter your password.', widget=forms.PasswordInput)
    password_2 = forms.CharField(label='Verify your password.', widget=forms.PasswordInput)
    is_worker = forms.BooleanField(label='Signing up as worker or as a client?', required=False)

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password', 'password_2', 'is_worker']

    def clean(self):
        """
        Verify both passwords match.
        """
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_2 = cleaned_data.get('password_2')
        if password and password != password_2:
            self.add_error('password_2', 'Passwords don\'t match!')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        is_worker = self.cleaned_data.pop('is_worker')
        if is_worker is not None:
            user.is_worker = True
        if commit:
            user.save()
        return user
