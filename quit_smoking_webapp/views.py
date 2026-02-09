from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from quit_smoking_webapp.forms import RegisterForm, UserProfileForm, StartingPointForm, DailyLogForm, SendPasswordResetLinkForm, ResetPasswordForm
from quit_smoking_webapp.models import UserProfile, DailyLog, DailyLogEmotion, DailyLogSituation

def is_htmx(request):
    return request.headers.get("HX-Request") == "true"


def welcome_view(request):
    return render(request, 'welcome.html', {'is_authenticated': request.user.is_authenticated})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("login")
    
    if request.method == "GET":
        form = RegisterForm()
    else:
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                username = form.data["username"],
                email = form.data["email"],
                password = form.data['password1']
            )

            return redirect('login')

    return render(request, 'register.html', {'form': form})


def login_view(request):  
    if request.method == "GET":
        form = AuthenticationForm()
    else:
        form = AuthenticationForm(request, data=request.POST)
        
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            return redirect('dashboard')

    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    has_profile = UserProfile.objects.filter(user=request.user).exists()
    logs_number = DailyLog.objects.filter(user=request.user).count()
    form = None

    if not has_profile:
        if request.method == "GET":
            form = StartingPointForm()
        else:
            form = StartingPointForm(request.POST)
        
            if form.is_valid():
                profile = form.save(commit=False)
                profile.user = request.user
                profile.save()
                has_profile = True

    return render(request, 'dashboard.html', {'has_profile': has_profile, 'form': form, 'log_number': logs_number})
 
 
@login_required
def dashboard_shell(request):
    return render(request, "dashboard_shell.html")


@login_required
def ui_home(request):
    if not is_htmx(request):
        return redirect("dashboard")
    
    return render(request, "partials/ui_home.html")


@login_required
def ui_starting_point(request):   
    if request.method == "GET":
        form = StartingPointForm()
    else:
        form = StartingPointForm(request.POST)
        
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.save()
            return redirect('dashboard')
    
    if is_htmx(request):
        return render(request, "partials/ui_starting_point.html", {'form': form})
    else:
        return render(request, "dashboard.html", {
            "has_profile": False,
            "content_template": "partials/ui_starting_point.html",
            "form": form
        })


@login_required
def ui_daily_log(request):
    if not is_htmx(request):
        return redirect("dashboard")
    
    if UserProfile.objects.filter(user=request.user).exists() == False:
        return redirect('dashboard')

    logs = DailyLog.objects.filter(user=request.user).order_by("-created_at")

    return render(request, 'partials/ui_daily_log.html', {'logs': logs})


@login_required
def ui_profile(request):
    profile = UserProfile.objects.filter(user=request.user).first()

    if not profile:
        return redirect('dashboard')

    if request.method == "GET":
        form = UserProfileForm(instance=profile)
    else:
        form = UserProfileForm(request.POST, user=request.user, instance=profile)

        if form.is_valid():
            profile.user = request.user
            profile.save()
            request.user.save()

            new_password = form.cleaned_data.get("password2")
            if new_password:
                request.user.set_password(form.cleaned_data["password2"])
                request.user.save()
                login(request, request.user)

            logs = DailyLog.objects.filter(user=request.user).order_by("-created_at")

            if is_htmx(request):
                return render(request, "partials/ui_daily_log.html", {"logs": logs})
            else:
                return render(request, "dashboard.html", {
                    "has_profile": True,
                    "content_template": "partials/ui_daily_log.html",
                    "logs": logs
                })

    if is_htmx(request):
        return render(request, 'partials/ui_profile.html', {'form': form})
    else:
        return render(request, 'dashboard.html', {
            "has_profile": True,
            "content_template": "partials/ui_profile.html",
            "form": form
        })



@login_required
def ui_add_daily_log_view(request):
    if UserProfile.objects.filter(user=request.user).exists() == False:
        return redirect('dashboard')
    
    if request.method == "GET":
        form = DailyLogForm()
    else:
        form = DailyLogForm(request.POST)
        
        if form.is_valid():
            daily_log = form.save(commit=False)
            daily_log.user = request.user
            daily_log.save()

            for emotion in form.cleaned_data['emotions']:
                DailyLogEmotion.objects.create(
                    daily_log=daily_log,
                    emotion=emotion
                )

            for situation in form.cleaned_data['situations']:
                DailyLogSituation.objects.create(
                    daily_log=daily_log,
                    situation=situation
                )

            logs = DailyLog.objects.filter(user=request.user).order_by("-created_at")

            if is_htmx(request):
                return render(request, "partials/ui_daily_log.html", {"logs": logs})
            else:
                return render(request, "dashboard.html", {
                    "has_profile": True,
                    "content_template": "partials/ui_daily_log.html",
                    "logs": logs
                })
    
    if is_htmx(request):
        return render(request, 'partials/ui_add_daily_log.html', {'form': form})
    else:
        return render(request, 'dashboard.html', {
            "has_profile": True,
            "content_template": "partials/ui_add_daily_log.html",
            "form": form
        })


@login_required
def ui_edit_daily_log_view(request, log_id):
    if UserProfile.objects.filter(user=request.user).exists() == False:
        return redirect('dashboard')
    
    daily_log = get_object_or_404(DailyLog, id=log_id, user=request.user)

    if request.method == "GET":
    
        daily_log_emotions = DailyLogEmotion.objects.filter(daily_log=daily_log)
        daily_log_situations = DailyLogSituation.objects.filter(daily_log=daily_log)

        initial = {
            'emotions': [element.emotion for element in daily_log_emotions],
            'situations': [element.situation for element in daily_log_situations]
        }

        form = DailyLogForm(instance=daily_log, initial=initial)
    else:
        form = DailyLogForm(request.POST, instance=daily_log)
        if form.is_valid():
            form.save()

            DailyLogEmotion.objects.filter(daily_log=daily_log).delete()
            DailyLogSituation.objects.filter(daily_log=daily_log).delete()

            for emotion in form.cleaned_data['emotions']:
                DailyLogEmotion.objects.create(
                    daily_log=daily_log,
                    emotion=emotion
                )

            for situation in form.cleaned_data['situations']:
                DailyLogSituation.objects.create(
                    daily_log=daily_log,
                    situation=situation
                )
            
            logs = DailyLog.objects.filter(user=request.user).order_by("-created_at")
            if is_htmx(request):
                return render(request, "partials/ui_daily_log.html", {"logs": logs})
            else:
                return render(request, "dashboard.html", {
                    "has_profile": True,
                    "content_template": "partials/ui_daily_log.html",
                    "logs": logs
                })


    if is_htmx(request):
        return render(request, "partials/ui_edit_daily_log.html", {
            "form": form,
            "daily_log": daily_log
        })
    else:
        return render(request, "dashboard.html", {
            "has_profile": True,
            "request": request,
            "content_template": "partials/ui_edit_daily_log.html",
            "form": form,
            "daily_log": daily_log
        })



@login_required
def ui_delete_log_view(request, log_id):
    if not is_htmx(request):
        return redirect("dashboard")
    
    if UserProfile.objects.filter(user=request.user).exists() == False:
        return redirect('dashboard')
    
    daily_log = get_object_or_404(DailyLog, id=log_id, user=request.user)

    if request.method == "POST":
        daily_log.delete()

        logs = DailyLog.objects.filter(user=request.user).order_by("-created_at")
        return render(request, "partials/ui_daily_log.html", {"logs": logs})
    
    return render(
        request,
        'partials/ui_delete_daily_log.html',
        {'log': daily_log}
    )


def password_reset_view(request):
  
    if request.method == "GET":
        form = SendPasswordResetLinkForm()

        return render(request, 'password_reset.html', {'form': form})
    else:
        form  = SendPasswordResetLinkForm(request.POST)

        if form.is_valid():
            user = User.objects.filter(email=form.data["email"]).first()

            if user is not None:
                token = default_token_generator.make_token(user)
                uid = user.pk

                message = f'Click this link to reset a password: 127.0.0.1:8000/password-reset/{uid}/{token}'

                print(message)

                send_mail(
                    subject="Reset your password",
                    message=message,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email]
                )

        return render(request, 'password_reset_done.html') 


def password_reset_confirm_view(request, uidb64, token):
    
    if request.method == "GET":
        form = ResetPasswordForm()
        return render(request, 'password_reset_confirm.html', {'form': form}) 
    else:
        form = ResetPasswordForm(request.POST)

        if form.is_valid():
            user = User.objects.filter(pk=uidb64).first()

            if user is not None:
                if default_token_generator.check_token(user, token) == True:
                    user.set_password(form.data['password1'])
                    user.save()

                    return redirect("login")
                else:
                    return render(request, 'password_reset_confirm.html', {'form': form}) 
        else:
            return render(request, 'password_reset_confirm.html', {'form': form}) 