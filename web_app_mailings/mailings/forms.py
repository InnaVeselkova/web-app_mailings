from django import forms

from .models import Mailing, Recipient, Message


class MailingForm(forms.ModelForm):
    class Meta:
        model = Mailing
        fields = ('start_time', 'end_time', 'message', 'recipients')
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'placeholder': 'YYYY-MM-DD HH:MM',
                }
            ),
            'end_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'placeholder': 'YYYY-MM-DD HH:MM',
                }
            ),
            'message': forms.Select(),
            'recipients': forms.CheckboxSelectMultiple(),
        }



class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = '__all__'
        exclude = ['owner']


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = '__all__'
        exclude = ['owner']
