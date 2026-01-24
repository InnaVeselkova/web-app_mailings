from django import forms

from .models import Mailing, Recipient, Message


class MailingForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if user:
            # фильтр для получателей
            self.fields["recipients"].queryset = Recipient.objects.filter(owner=user)
            # фильтр для сообщений
            self.fields["message"].queryset = Message.objects.filter(owner=user)

    class Meta:
        model = Mailing
        fields = ("start_time", "end_time", "message", "recipients")
        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "placeholder": "YYYY-MM-DD HH:MM",
                }
            ),
            "end_time": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "placeholder": "YYYY-MM-DD HH:MM",
                }
            ),
            "message": forms.Select(),
            "recipients": forms.CheckboxSelectMultiple(),
        }


class RecipientForm(forms.ModelForm):
    class Meta:
        model = Recipient
        fields = "__all__"
        exclude = ["owner"]


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = "__all__"
        exclude = ["owner"]
