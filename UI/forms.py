from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, Submit, HTML

from Accounts.models import *

User = get_user_model()

class BaseStyling:
    # Apply CSS property on all the fields
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            
            field.widget.attrs.update({
                    'class': 'form-control',
                })
            
            if isinstance(field.widget, forms.RadioSelect):
                field.widget.attrs.update({
                    'class': 'form-control-RadioSelect',
                })
            
            if isinstance(field.widget, (forms.Select)):
                field.widget.attrs.update({
                    'class': 'form-select',
                })
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'rows': 5,
                })
                
            if not field.widget.attrs.get('col_class'):
                field.widget.attrs['col_class'] = 'col-md-4'

            field.empty_label = "Select"
        
    def __getitem__(self, name):
        bound = super().__getitem__(name)
        # fetch col_class from widget.attrs
        bound.col_class = self.fields[name].widget.attrs.get('col_class', '')
        return bound


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
        # user.is_active = False            # TODO add email verification
        if commit:
            user.save()
        return user

class TravelPlanForm(BaseStyling,forms.ModelForm):
    class Meta:
        model = TravelPlan
        fields = '__all__'
        exclude = ['user','created_at','updated_at','status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].widget.attrs['col_class'] = "col-12"

class TripForm(BaseStyling,forms.ModelForm):
    class Meta:
        model = Trip
        fields = '__all__'
        exclude = ['plan','created_at','updated_at','passengers']
        widgets = {
            'departure_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'estimated_arrival_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['title'].widget.attrs['col_class'] = "col-12"
        self.fields['notes'].widget.attrs['col_class'] = "col-12"
        self.fields['origin_name'].widget.attrs['col_class'] = "col-md-6"
        self.fields['destination_name'].widget.attrs['col_class'] = "col-md-6"
        # Place the datetime fields side by side by default
        if 'departure_time' in self.fields:
            self.fields['departure_time'].widget.attrs['col_class'] = 'col-md-6'
            # Accept HTML5 datetime-local formats
            self.fields['departure_time'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S']
        if 'estimated_arrival_time' in self.fields:
            self.fields['estimated_arrival_time'].widget.attrs['col_class'] = 'col-md-6'
            self.fields['estimated_arrival_time'].input_formats = ['%Y-%m-%dT%H:%M', '%Y-%m-%dT%H:%M:%S']
    

TripFormSet = inlineformset_factory(
    TravelPlan,         # Parent model
    Trip,               # Child model
    form=TripForm,      # The form to use for each child
    extra=1,            # Show 1 blank form by default
    can_delete=True,    # Allow deleting existing trips on edit
    fk_name='plan',     # Explicitly state the foreign key
)
