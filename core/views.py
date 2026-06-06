from django.shortcuts import render , redirect 
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

def index(request):
    
    return render(request, 'core/index.html')


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import CustomUser

def login_view(request):
    if request.method == 'POST':
        teamname = request.POST.get('teamname')
        password = request.POST.get('password')

        user = authenticate(request, username=teamname, password=password)

        if user is not None:
            login(request, user)
            return redirect('core:index')  # change this to wherever you want to redirect after login
        else:
            messages.error(request, 'Invalid team name or password.')

    return render(request, 'core/login.html')  # your login form template

def logout_view(request):
    logout(request)
    return redirect('core:login')  # back to login page

from .models import Challenge , Phase
def challenges(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You have to login to access this page')
        return redirect('core:login')

    challenges = Challenge.objects.filter(is_visible=True)
    challenges = challenges.filter(phase__is_active=True)
    
    phase = Phase.objects.filter(is_active=True).first()

    for challenge in challenges:
        challenge.is_submitted = Submission.objects.filter(user=request.user, challenge=challenge).exists()

    return render(request, 'core/challenges.html', {'challenges': challenges , 'phase':phase})

from .models import Hint, Submission
from django.db.models import Sum
@login_required
def challenge_details(request , pk):
    challenge = Challenge.objects.get(pk=pk)  # Assuming you have a Challenge model
    is_submitted = False
    hints = challenge.hint_set.all()  

    if request.method == 'POST':
        diagnosis = request.POST.get('diagnosis')
        user = request.user
        if user.is_authenticated:

            submission = Submission(user=user, challenge=challenge, solution=diagnosis)
            submission.save()
            messages.success(request, 'Your submission has been recorded.')
        else:
            messages.error(request, 'You need to be logged in to submit a solution.')

    if request.user.is_authenticated:
        is_submitted = Submission.objects.filter(user=request.user, challenge=challenge).exists()
    else:
        is_submitted = False


    return render(request, 'core/challenge_details.html', {'challenge': challenge, 'hints': hints , 'is_submitted': is_submitted})


@login_required
def profile(request):
    if request.user.is_authenticated:
        user = request.user
        submissions = Submission.objects.filter(user=user)
        return render(request, 'core/profile.html', {'user': user, 'submissions': submissions})
    else:
        return redirect('core:login')  



# views.py
from django.http import JsonResponse
from .models import Hint, UserHint
from django.shortcuts import get_object_or_404

@login_required
def use_hint(request, hint_id):
    hint = get_object_or_404(Hint, pk=hint_id)
    user = request.user

    # Already used
    already_used = UserHint.objects.filter(user=user, hint=hint).exists()
    if already_used:
        return JsonResponse({'hint_html': render_to_string('partials/hint_content.html', {'hint': hint}), 'charged': False})

    # Not enough points
    if user.score < hint.value:
        return JsonResponse({'error': 'Not enough points'}, status=403)

    # Deduct points and save usage
    user.score -= hint.value
    user.save()
    UserHint.objects.create(user=user, hint=hint)

    return JsonResponse({'hint_html': render_to_string('partials/hint_content.html', {'hint': hint}), 'charged': True})

@login_required
def leaderboard(request):
    users = CustomUser.objects.all().order_by('-score')[:10]
    return render(request, 'core/leaderboard.html', {'users': users})

@login_required
def api_leaderboard(request):
    users = CustomUser.objects.all().order_by('-score')
    users = users.exclude(is_staff=True)
    if not users:
        return JsonResponse({'error': 'No users found'}, status=404)
    data = [{'teamname': user.teamname, 'score': user.score} for user in users]
    return JsonResponse(data, safe=False)


# Admin Dashboard Views
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count, Q

def is_admin(user):
    """Check if user is staff"""
    return user.is_staff

@user_passes_test(is_admin)
def admin_dashboard(request):
    """
    Admin dashboard to view and validate submissions.
    - Supreme admin (username="admin") sees all submissions
    - Other admins see only submissions for challenges they authored
    """
    user = request.user
    
    # Get challenges authored by this user
    if user.username == "admin":
        # Supreme admin sees all challenges and submissions
        challenges = Challenge.objects.all()
        submissions = Submission.objects.all()
    else:
        # Regular admin sees only their authored challenges and submissions
        challenges = Challenge.objects.filter(author=user)
        challenges = challenges.filter(phase__is_active=True)

        submissions = Submission.objects.filter(challenge__author=user)
    
    # Prepare data for display
    challenges_data = []
    
    for challenge in challenges:
        challenge_submissions = submissions.filter(challenge=challenge)
        
        submissions_list = []
        for submission in challenge_submissions:
            # Get hints used by this team/user
            hints_used = UserHint.objects.filter(user=submission.user, hint__challenge=challenge).select_related('hint')
            hint_details = [
                {
                    'title': hint_used.hint.title,
                    'value': hint_used.hint.value,
                    'number': hint_used.hint.hint_number,
                    'used_at': hint_used.used_at
                }
                for hint_used in hints_used
            ]
            total_hint_value = sum(h['value'] for h in hint_details)
            
            submissions_list.append({
                'id': submission.id,
                'team_name': submission.user.teamname,
                'submission_time': submission.submission_time,
                'solution': submission.solution,
                'is_correct': submission.is_correct,
                'is_false': submission.is_false,
                'hints_used': hint_details,
                'total_hints_count': len(hint_details),
                'total_hints_value': total_hint_value,
            })
        
        if submissions_list:
            challenges_data.append({
                'id': challenge.id,
                'points': challenge.points,
                'title': challenge.title,
                'submissions': submissions_list,
                'submission_count': len(submissions_list)
            })
    
    context = {
        'challenges_data': challenges_data,
        'is_supreme_admin': user.username == "admin"
    }
    
    return render(request, 'core/admin_dashboard.html', context)


@user_passes_test(is_admin)
def update_submission_status(request, submission_id):
    """
    API endpoint to update submission status (is_correct, is_false)
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        submission = Submission.objects.get(id=submission_id)
        user = request.user
        
        # Check authorization - user must be author of the challenge or be supreme admin
        if user.username != "admin" and submission.challenge.author != user:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Get the new status values
        is_correct = request.POST.get('is_correct') == 'true'
        is_false = request.POST.get('is_false') == 'true'
        
        # Update submission
        submission.is_correct = is_correct
        submission.is_false = is_false
        submission.save()
        
        return JsonResponse({
            'success': True,
            'id': submission.id,
            'is_correct': submission.is_correct,
            'is_false': submission.is_false
        })
    
    except Submission.DoesNotExist:
        return JsonResponse({'error': 'Submission not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
