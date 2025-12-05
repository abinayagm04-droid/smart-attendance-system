from django.shortcuts import render, get_object_or_404, redirect
from .models import Classroom, Student, Attendance
from .forms import ClassroomForm, StudentForm
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from datetime import date
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models.functions import TruncMonth

def home(request):
    return render(request, 'school/home.html')


def classroom_list(request):
    # Show all classrooms; you can filter by request.user if you want teacher-specific view
    classrooms = Classroom.objects.all().order_by('-created_at')
    return render(request, 'school/classroom_list.html', {'classrooms': classrooms})


@login_required  # require login to create classes
def classroom_create(request):
    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save(commit=False)
            # assign logged-in user as teacher (User)
            classroom.teacher = request.user
            classroom.save()
            messages.success(request, 'Classroom created successfully.')
            return redirect('school:classroom_list')
    else:
        form = ClassroomForm()
    return render(request, 'school/classroom_form.html', {'form': form})


@login_required
def student_add(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.classroom = classroom
            student.save()
            messages.success(request, 'Student added.')
            return redirect('school:classroom_list')
    else:
        form = StudentForm()
    return render(request, 'school/student_form.html', {'form': form, 'classroom': classroom})


@require_http_methods(["GET", "POST"])
@login_required
def mark_attendance(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    students = classroom.students.all().order_by('roll_number')
    selected_date = request.GET.get('date') or date.today().isoformat()

    if request.method == 'POST':
        selected_date = request.POST.get('date') or date.today().isoformat()
        for student in students:
            key = f"status_{student.id}"
            status = request.POST.get(key, 'A')  # default Absent
            Attendance.objects.update_or_create(
                student=student,
                date=selected_date,
                defaults={'status': status}
            )
        messages.success(request, f'Attendance saved for {selected_date}.')
        return redirect('school:classroom_list')

    # Build student_status list to simplify template lookups
    attendance_map = {}
    for att in Attendance.objects.filter(student__in=students, date=selected_date):
        attendance_map[att.student_id] = att.status

    student_status = []
    for s in students:
        student_status.append({
            'student': s,
            'status': attendance_map.get(s.id, 'A')  # default A
        })

    return render(request, 'school/mark_attendance.html', {
        'classroom': classroom,
        'student_status': student_status,
        'date': selected_date,
    })


@login_required
def monthly_report(request):
    classrooms = Classroom.objects.all()
    report = None
    today = date.today()
    if request.method == 'GET' and request.GET.get('classroom'):
        classroom_id = request.GET.get('classroom')
        classroom = get_object_or_404(Classroom, pk=classroom_id)
        month = int(request.GET.get('month') or today.month)
        year = int(request.GET.get('year') or today.year)
        student_id = request.GET.get('student')

        # attendance queryset for that month
        ats = Attendance.objects.filter(student__classroom=classroom, date__year=year, date__month=month)
        if student_id:
            ats = ats.filter(student_id=student_id)

        students = classroom.students.all()
        data = []
        for s in students:
            total = Attendance.objects.filter(student=s, date__year=year, date__month=month).count()
            present = Attendance.objects.filter(student=s, date__year=year, date__month=month, status='P').count()
            late = Attendance.objects.filter(student=s, date__year=year, date__month=month, status='L').count()
            absent = Attendance.objects.filter(student=s, date__year=year, date__month=month, status='A').count()
            percent = (present / total * 100) if total > 0 else 0
            data.append({
                'student': s, 'total': total, 'present': present, 'late': late, 'absent': absent, 'percent': round(percent, 2)
            })
        report = {'classroom': classroom, 'month': month, 'year': year, 'data': data}

    return render(request, 'school/monthly_report.html', {
        'classrooms': classrooms,
        'report': report,
        'today': today
    })


@login_required
def attendance_filter(request):
    classrooms = Classroom.objects.all()
    results = None
    if request.method == 'GET' and (request.GET.get('student') or request.GET.get('date')):
        student_id = request.GET.get('student')
        selected_date = request.GET.get('date')
        q = Attendance.objects.all()
        if student_id:
            q = q.filter(student_id=student_id)
        if selected_date:
            q = q.filter(date=selected_date)
        results = q.select_related('student').order_by('-date')
    return render(request, 'school/attendance_filter.html', {
        'classrooms': classrooms,
        'results': results
    })


@login_required
def dashboard(request):
    total_students = Student.objects.count()
    total_classes = Classroom.objects.count()
    total_attendance = Attendance.objects.count()

    latest_date = Attendance.objects.order_by('-date').values_list('date', flat=True).first()
    pie = {'P': 0, 'A': 0, 'L': 0}
    if latest_date:
        qs = Attendance.objects.filter(date=latest_date)
        for s in qs:
            pie[s.status] = pie.get(s.status, 0) + 1

    trend_qs = (Attendance.objects.filter(status='P')
                .annotate(month=TruncMonth('date'))
                .values('month')
                .annotate(count=Count('id'))
                .order_by('month'))
    trend = [{'month': i['month'].strftime('%Y-%m'), 'count': i['count']} for i in trend_qs]

    return render(request, 'school/dashboard.html', {
        'total_students': total_students,
        'total_classes': total_classes,
        'total_attendance': total_attendance,
        'pie': pie,
        'trend': trend,
        'latest_date': latest_date
    })




