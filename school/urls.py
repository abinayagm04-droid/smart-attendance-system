from django.urls import path
from . import views

app_name = 'school'

urlpatterns = [
    path('', views.home, name='home'),
    path('classrooms/', views.classroom_list, name='classroom_list'),
    path('classrooms/add/', views.classroom_create, name='classroom_create'),
    path('classrooms/<int:pk>/students/add/', views.student_add, name='student_add'),
    path('classrooms/<int:pk>/attendance/mark/', views.mark_attendance, name='mark_attendance'),
    path('reports/monthly/', views.monthly_report, name='monthly_report'),
    path('attendance/filter/', views.attendance_filter, name='attendance_filter'),
    path('dashboard/', views.dashboard, name='dashboard'),
]