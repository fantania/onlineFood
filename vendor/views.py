from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse

from accounts.forms import UserProfileForm
from accounts.models import UserProfile
from accounts.views import check_role_vendor
from menu.models import Category, FoodItem
from vendor.forms import OpeningHourForm, VendorForm
from vendor.models import OpeningHour, Vendor
from django.template.defaultfilters import slugify

from menu.forms import CategoryForm, FoodForm

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

def get_vendor(request):
    vendor = Vendor.objects.get(user=request.user)
    return vendor

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def v_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    vendor = get_object_or_404(Vendor, user=request.user)

    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, request.FILES, instance= profile)
        vendor_form = VendorForm(request.POST, request.FILES, instance= vendor)
        if profile_form.is_valid() and vendor_form.is_valid():
            profile_form.save()
            vendor_form.save()
            messages.success(request, 'Your restaurant has been updated')
            return redirect('v_profile')
        else:
            #messages.error('Forms invalid')
            print(profile_form.errors)
            print(vendor_form.errors)
    else:
        profile_form = UserProfileForm(instance= profile)
        vendor_form = VendorForm(instance= vendor)

    context = {
        'profile_form': profile_form,
        'vendor_form': vendor_form,
        'profile': profile,
        'vendor': vendor,


    }
    return render(request, 'vendor/v_profile.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def menu_builder(request):
    vendor = get_vendor(request)
    categories = Category.objects.filter(vendor=vendor).order_by('created_at')
    context = {
        'categories': categories,
    }
    return render(request, 'vendor/menu_builder.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def food_items_by_category(request, pk=None):
    vendor = get_vendor(request)
    category = get_object_or_404(Category, pk=pk)
    food_items = FoodItem.objects.filter(vendor=vendor, category=category).order_by('created_at')
    context = {
        'food_items': food_items,
        'category': category,
    }
    return render(request, 'vendor/food_items_by_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Category added successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_category(request, pk=None):
    category= get_object_or_404(Category, pk = pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            category_name = form.cleaned_data['category_name']
            category = form.save(commit=False)
            category.vendor = get_vendor(request)
            category.slug = slugify(category_name)
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('menu_builder')
        else:
            print(form.errors)
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'category': category,
        
    }

    return render(request, 'vendor/edit_category.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_category(request, pk=None):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    messages.success(request, 'Category has been deleted successfully!')
    return redirect('menu_builder')

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def add_food(request):
    if request.method == 'POST':
        form = FoodForm(request.POST, request.FILES)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.slug = slugify(food_title)
            food.vendor = get_vendor(request)    
            form.save()
            messages.success(request, 'Food added successfully!')
            return redirect('food_items_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodForm()
        form.fields['category'].queryset = Category.objects.filter(vendor = get_vendor(request))
    
    context = {
        'form': form,
    }
    return render(request, 'vendor/add_food.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def edit_food(request, pk=None):
    food= get_object_or_404(FoodItem, pk = pk)
    if request.method == 'POST':
        form = FoodForm(request.POST, request.FILES, instance=food)
        if form.is_valid():
            food_title = form.cleaned_data['food_title']
            food = form.save(commit=False)
            food.slug = slugify(food_title)
            food.vendor = get_vendor(request)    
            form.save()
            messages.success(request, 'Food updated successfully!')
            return redirect('food_items_by_category', food.category.id)
        else:
            print(form.errors)
    else:
        form = FoodForm(instance=food)
        form.fields['category'].queryset = Category.objects.filter(vendor = get_vendor(request))
    
    context = {
        'form': form,
        'food': food,
        
    }

    return render(request, 'vendor/edit_food.html', context)

@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def delete_food(request, pk=None):
    food = get_object_or_404(FoodItem, pk=pk)
    category = food.category
    food.delete()
    messages.success(request, 'Food has been deleted successfully!')
    return redirect(reverse('food_items_by_category', args=[category.id]))


def opening_hours(request):
   opening_hours = OpeningHour.objects.filter(vendor = get_vendor(request))
   form = OpeningHourForm()
   context = {
       'form': form,
       'opening_hours': opening_hours,
   }
   return render(request, 'vendor/opening_hours.html', context)

def add_opening_hours(request):
    # handle the data and save them inside the database
    if request.user.is_authenticated:
        if is_ajax(request) and request.method == 'POST':
            day = request.POST.get('day')
            from_hour = request.POST.get('from_hour')
            to_hour = request.POST.get('to_hour')
            is_closed = request.POST.get('is_closed')
            try:
                hour = OpeningHour.objects.create(vendor = get_vendor(request), day =day, from_hour = from_hour, to_hour = to_hour, is_closed = is_closed)
                if hour:
                    day = OpeningHour.objects.get(id = hour.id)
                    if day.is_closed:
                        response = {'status': 'success', 'id':hour.id, 'day': day.get_day_display(),'is_closed': 'Closed'}
                    else:
                        response = {'status': 'success', 'id':hour.id, 'day': day.get_day_display(),'from_hour': day.from_hour, 'to_hour': day.to_hour}
                return JsonResponse(response)
            except IntegrityError as e:
                    response = {'status': 'failed', 'message': from_hour+'-'+to_hour+' already exists for this day!'}
                    return JsonResponse(response)

        else:
            HttpResponse('Invalid request')

def remove_opening_hours(request, pk =None):
    if request.user.is_authenticated:
        if is_ajax(request):
            hour = get_object_or_404(OpeningHour, pk=pk)
            hour.delete()
            return JsonResponse({'status':'success','id':pk})





