from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

User = get_user_model()

class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput,
        help_text='Usa una contraseña segura'
    )
    password2 = forms.CharField(
        label='Repite la contraseña',
        widget=forms.PasswordInput,
        strip=False
    )

    class Meta:
        model = User
        fields = ["email", "first_name", "last_name"]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este email ya está registrado.')
        return email
    
    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1:
            validate_password(p1)
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Las contraseñas no coinciden.')
        return cleaned
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email'].lower().strip()
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            base = "w-full rounded-2xl border border-black/10 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-black/20"
            if getattr(field.widget, "input_type", "") == "password":
                field.widget.attrs.update({"class": base, "autocomplete": "new-password"})
            else:
                field.widget.attrs.update({"class": base})
        base = "w-full rounded-2xl border border-black/10 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-black/20"
        for f in self.fields.values():
            f.widget.attrs.setdefault("class", base)
        
class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        self.user_cache = None

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get("email")
        password = cleaned.get("password")

        if email and password:
            user = authenticate(self.request, username=email, password=password)
            if user is None:
                raise ValidationError('Email o contraseña incorrectos.')
            if not user.is_active:
                raise ValidationError('La cuenta está inactiva.')
            self.user_cache = user
        return cleaned
    
    def get_user(self):
        return self.user_cache
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)
        self.user_cache = None
        base = "w-full rounded-2xl border border-black/10 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-black/20"
        self.fields["email"].widget.attrs.update({"class": base, "autocomplete": "email"})
        self.fields["password"].widget.attrs.update({"class": base, "autocomplete": "current-password"})
        base = "w-full rounded-2xl border border-black/10 px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-black/20"
        for f in self.fields.values():
            f.widget.attrs.setdefault("class", base)
    
