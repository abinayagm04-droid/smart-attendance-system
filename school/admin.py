from django.contrib import admin
from .models import Classroom, Student, Attendance

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'teacher', 'created_at')
    search_fields = ('name', 'teacher__username')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'name', 'classroom')
    list_filter = ('classroom',)
    search_fields = ('name', 'roll_number')

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'date', 'status', 'marked_at')
    list_filter = ('date', 'status')
    search_fields = ('student_name', 'student_roll_number')