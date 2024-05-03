from django.forms import ModelForm, DateInput
from todo.models import Task

class EventForm(ModelForm):
  class Meta:
    model = Task
    widgets = {
      'date_posted': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
      'date_end': DateInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
    }
    fields = '__all__'

  def __init__(self, *args, **kwargs):
    super(EventForm, self).__init__(*args, **kwargs)
    self.fields['date_posted'].input_formats = ('%Y-%m-%dT%H:%M',)
    self.fields['date_end'].input_formats = ('%Y-%m-%dT%H:%M',)
