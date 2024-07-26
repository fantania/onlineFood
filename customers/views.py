from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from django.contrib.auth.decorators import login_required, user_passes_test

from accounts.forms import UserInfoForm, UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_role_customer

@login_required(login_url='login')
@user_passes_test(check_role_customer)
def cprofile(request):
    profile = get_object_or_404(UserProfile, user = request.user)
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance = profile)
        user_form = UserInfoForm(request.POST, instance = request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()

            messages.success(request, 'Profile saved!')
            return redirect('cprofile')
        else:
            print(profile_form.errors)
            print(user_form.errors)
    else:
        profile_form = UserProfileForm(instance = profile)
        user_form = UserInfoForm(instance = request.user)
 
    context = {
        'profile_form': profile_form,
        'user_form' : user_form,
        'profile' : profile,

    }
    return render(request, 'customers/cprofile.html', context)
