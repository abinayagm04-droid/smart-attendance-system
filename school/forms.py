from django import forms
from .models import Classroom, Student

class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Class name (e.g. 10A)'})
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Student name'}),
            'roll_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Roll number'}),
        }