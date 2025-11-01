from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column

User = get_user_model()

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required. Enter a valid email address.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Row(
                Column("username", css_class="col-12 mb-3"),
                Column("email", css_class="col-12 mb-3"),
            ),
            Row(
                Column("password1", css_class="col-12 mb-3"),
                Column("password2", css_class="col-12 mb-3"),
            ),
            Submit("submit", "Create account", css_class="btn btn-primary mt-3")
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        # if you want to set `is_active = False` for email activation:
        # user.is_active = False
        if commit:
            user.save()
        return user
