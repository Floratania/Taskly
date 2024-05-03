from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.db.models.functions import TruncDay
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordResetDoneView
from .forms import CreateUserForm, LoginForm, CreateTaskForm, UpdateUserForm, UpdateProfileForm, PasswordChangeForm, UpdateProfilePhoneNumberForm
from django.contrib.auth.models import auth, User
from django.contrib.auth import authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .models import Task, Profile, Activity
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta, datetime, date
from django.db.models import Q,  Count
from django.views import generic
from django.utils.safestring import mark_safe
from .utils import Calendar
from django.views.generic import ListView


class CalendarView(generic.ListView):
    model = Task
    template_name = 'calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        d = get_date(self.request.GET.get('day', None))

        cal = Calendar(d.year, d.month)

        html_cal = cal.formatmonth(withyear=True)
        
        context['calendar'] = mark_safe(html_cal)
        
        return context



def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()


@login_required(login_url='my-login')
def activity(request):
    user_id = request.user.id

    profile_pic = Profile.objects.get(user=request.user)
    activity = Activity.objects.get(user=request.user)

    now = timezone.now()
    first_day = now.replace(day=1)
    last_day = first_day.replace(month=(first_day.month % 12) + 1, day=1, hour=23, minute=59, second=59) - timezone.timedelta(days=1)
    
    all_days_of_month = [first_day + timezone.timedelta(days=i) for i in range((last_day - first_day).days + 1)]

    all_days_of_month.sort()

    task_counts_by_day = Task.objects.filter(
        user_id=user_id,
        date_posted__range=(first_day, last_day - timezone.timedelta(days=1))
    ).annotate(
        day=TruncDay('date_posted')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')

    task_count_today = Task.objects.filter(
        user_id=user_id,
        date_posted__date=now.date()
    ).count()

    task_counts_dict = {entry['day'].date(): entry['count'] for entry in task_counts_by_day}

    task_counts = [task_counts_dict.get(day.date(), 0) for day in all_days_of_month]

    task_counts.append(task_count_today)

    dates = [day.strftime('%Y-%m-%d') for day in all_days_of_month]


    context = {
        'profile': profile_pic,
        'activity': activity,
        'dates': dates,
        'task_counts': task_counts
    }
    
    return render(request, 'profile/activity.html', context=context)

class ActivityView(ListView):
    model = Activity
    template_name = 'profile/activity.html'

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(user=self.request.user)
        return qs.order_by('-last_login')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = datetime.now().strftime('%Y-%m-%d %H:%M')
        if today in context['chart_labels']:
            index = context['chart_labels'].index(today)
            for dataset in context['chart_data']:
                del dataset['data'][index]
            del context['chart_labels'][index]

        today_completed = Task.objects.filter(user=self.request.user, status='completed', date_posted__date=datetime.now().date()).count()
        today_assigned = Task.objects.filter(user=self.request.user, status='assigned', date_posted__date=datetime.now().date()).count()
        today_in_progress = Task.objects.filter(user=self.request.user, status='in_progress', date_posted__date=datetime.now().date()).count()

        context['chart_labels'].append(today)
        context['chart_data'][0]['data'].append(today_completed)
        context['chart_data'][1]['data'].append(today_assigned)
        context['chart_data'][2]['data'].append(today_in_progress)

        return context


@login_required
def task_daily_count(request):
    user_id = request.user.id
    
    now = datetime.now()
    first_day = now.replace(day=1)
    last_day = (first_day.replace(month=first_day.month % 12 + 1, day=1) - timedelta(days=1)).replace(hour=23, minute=59, second=59)

   
    all_days_of_month = [first_day + timedelta(days=i) for i in range((last_day - first_day).days + 1)]

   
    task_counts_by_day = Task.objects.filter(user_id=user_id, date_posted__range=(first_day, last_day)).annotate(
        day=TruncDay('date_posted')
    ).values('day').annotate(
        count=Count('id')
    ).order_by('day')

   
    task_counts_dict = {entry['day'].date(): entry['count'] for entry in task_counts_by_day}

   
    task_counts = [task_counts_dict.get(day.date(), 0) for day in all_days_of_month]

    dates = [day.strftime('%Y-%m-%d') for day in all_days_of_month]

    return render(request, 'profile/task_daily_count.html', {'dates': dates, 'task_counts': task_counts})




@login_required(login_url='my-login') 
def profile_management(request):
    user_form = UpdateUserForm(instance=request.user)
    profile = Profile.objects.get(user=request.user)
    form_2 = UpdateProfileForm(instance=profile)
    phone_number_form = UpdateProfilePhoneNumberForm(instance=profile)

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        form_2 = UpdateProfileForm(request.POST, request.FILES, instance=profile)
        phone_number_form = UpdateProfilePhoneNumberForm(request.POST, instance=profile)
        
        if user_form.is_valid() and phone_number_form.is_valid():
            user_form.save()
            phone_number_form.save()

            return redirect('dashboard')
        
        if form_2.is_valid():
            form_2.save()
            return redirect('dashboard')
        


    context = {
        'user_form': user_form,
        'form_2': form_2,
        'phone_number_form': phone_number_form
    }

    return render(request, 'profile/profile-management.html', context=context)


def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk)
    return render(request, 'task_detail.html', {'task': task})



def calendar_view(request):
    tasks = Task.objects.filter(user=request.user)

    return render(request, 'calendar.html', {'tasks': tasks})



def home(request):

    return render(request, 'index.html')

    
def register(request):
    form = CreateUserForm()

    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        if form.is_valid():
            
            user = form.save(commit=False)
            user.save()
            
            profile = Profile.objects.create(user=user)
            phone_number = form.cleaned_data['phone_number']
            profile.phone_number = phone_number
            profile.save()
            
            messages.success(request, "User registration was successful!")
            
            return redirect('my-login')
        
    context = {'form': form}
    return render(request, 'register.html', context=context)



def my_login(request):
    
    form = LoginForm
    
    if request.method == 'POST':
        
        form = LoginForm(request, data=request.POST)
        
        if form.is_valid():
            
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            user = authenticate(request, username=username, password=password)
        
    

            if user is not None:
                
                auth.login(request, user)
                
                update_user_activity(request.user, 'login')
                
                return redirect("dashboard")
            else:
                # Якщо authenticate повертає None, то користувача не знайдено
                form.add_error(None, "Invalid username or password. Please try again.")
            
            
    context = {'form': form}
            
    return render(request, 'my-login.html', context=context)



def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'change_password.html', {'form': form})


@login_required(login_url='my-login')
def dashboard(request):
    
 
    profile_pic = Profile.objects.get(user=request.user)
    context = {'profile': profile_pic}
    return render(request, 'profile/dashboard.html', context=context)
        


@login_required(login_url='my-login')
def email(request):
    
 
    profile_pic = Profile.objects.get(user=request.user)
    return render(request, 'profile/email.html')
       
       
       
       
@login_required(login_url='my-login')
def update_profile(request):
    user_form = UpdateUserForm(instance=request.user)
    profile = Profile.objects.get(user=request.user)
    profile_form = UpdateProfileForm(instance=profile)

    if request.method == 'POST':
        user_form = UpdateUserForm(request.POST, instance=request.user)
        profile_form = UpdateProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('dashboard')

    context = {'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'profile/update_profile.html', context=context)



@login_required(login_url='my-login') 
def deleteAccount(request):
    
    if request.method == 'POST':
        
        deleteUser = User.objects.get(username=request.user)
        
        deleteUser.delete()
        
        return redirect('')
 
    return render(request, 'profile/delete-account.html')



@login_required(login_url='my-login') 
def createTask(request):
    
    form = CreateTaskForm()
    
    if request.method == 'POST':
        
        form = CreateTaskForm(request.POST)
        
        if form.is_valid():
            
            task = form.save(commit=False)
            
            task.user = request.user
            
            task.save()
            
            task=Task.objects.get(id=task.id)
            
            
            if task.status == 'option1' :
                update_user_activity(request.user, 'total_tasks_assigned')
            elif task.status == 'option2' :
                update_user_activity(request.user, 'total_tasks_in_progress')
            elif task.status == 'option3' :
                update_user_activity(request.user, 'total_tasks_completed')
            
            
            return redirect('view-tasks')
        
        
    context = {'form': form}
    
    return render(request, 'profile/create-task.html', context=context)



@login_required(login_url='my-login')
def viewTasks(request):
    current_user = request.user.id
    
    status_filter = request.GET.get('status', None)
    date_due_to = request.GET.get('date_due_to', None)
    
  
    tasks = Task.objects.filter(user=current_user)
    
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    
    if date_due_to:
        
        due_date = datetime.strptime(date_due_to, '%Y-%m-%d')
       
        tasks = tasks.filter(Q(do_to__lte=due_date))
    
    
    
    context = {
        'tasks': tasks,
        'status_filter': status_filter,
        'date_due_to': date_due_to
    }
    
    return render(request, 'profile/view-tasks.html', context=context)


@login_required(login_url='my-login')
def viewTask(request, task_id):
   
    instance = get_object_or_404(Task, pk=task_id)
    form = CreateTaskForm(request.POST or None, instance=instance)
    context = {
        'instance': instance,
        'form': form  
    }
    
    return render(request, 'profile/view-task.html', context)
        

    
   


@login_required(login_url='my-login')
def updateTask(request, pk):
    
    task= Task.objects.get(id=pk)
    
    if task.status == 'option1' :
        
        update_user_activity(request.user, 'total_tasks_assigned_del')
        
    elif task.status == 'option2' :
        
        update_user_activity(request.user, 'total_tasks_in_progress_del')
        
    elif task.status == 'option3' :
        
        update_user_activity(request.user, 'total_tasks_completed_del')
    
    
    form = CreateTaskForm(instance=task)
    
    if request.method == 'POST':
        
        form = CreateTaskForm(request.POST, instance=task)
    
        if form.is_valid():
            
            
            if task.status == 'option1'  :
                
                update_user_activity(request.user, 'total_tasks_assigned')
                
            elif task.status == 'option2' :
                update_user_activity(request.user, 'total_tasks_in_progress')
                
            elif task.status == 'option3' :
                
                update_user_activity(request.user, 'total_tasks_completed')
         
                task.date_end = timezone.now() + timedelta(hours=2)
                
                task.save()
            
            form.save()
            return redirect('view-tasks')
        
    context = {'form': form}
    
    return render(request, 'profile/update-task.html', context=context)




def deleteTask(request, pk):

    task = Task.objects.get(id=pk)
    
    if request.method == 'POST':
        
        if task.status == 'option1'  :
                
                update_user_activity(request.user, 'total_tasks_assigned_del')
                
        elif task.status == 'option2' :
            update_user_activity(request.user, 'total_tasks_in_progress_del')
            
        elif task.status == 'option3' :
            
            update_user_activity(request.user, 'total_tasks_completed_del')
    
        
        task.delete()
        
        return redirect('view-tasks')


    return render(request, 'profile/delete-task.html')





def user_logout(request):
    
    update_user_activity(request.user, 'logout')
    
    auth.logout(request)
    
    return redirect("")



def update_user_activity(user, action_type):
    activity, created = Activity.objects.get_or_create(user=user)
    
    if action_type == 'login':
        activity.last_login = timezone.now()
    elif action_type == 'logout':
        activity.last_logout = timezone.now()
    elif action_type == 'total_tasks_completed':
        activity.total_tasks_completed += 1
    elif action_type == 'total_tasks_assigned':
        activity.total_tasks_assigned += 1
    elif action_type == 'total_tasks_in_progress' :
        activity.total_tasks_in_progress += 1
    elif action_type == 'total_tasks_completed_del' and activity.total_tasks_completed != 0:
        activity.total_tasks_completed -= 1
    elif action_type == 'total_tasks_assigned_del' and activity.total_tasks_assigned != 0:
        activity.total_tasks_assigned -= 1
    elif action_type == 'total_tasks_in_progress_del' and activity.total_tasks_in_progress != 0:
        activity.total_tasks_in_progress -= 1
        
    activity.save()
    
    
    
    
class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset_form.html'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'
    
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'
    success_url = '/reset/done/'  
    
class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'registration/password_reset_complete.html'