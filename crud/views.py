from django.template.loader import render_to_string
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .models import Genders, Users
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required



# Create your views here.

@login_required
def gender_list(request):
   try:
      genders = Genders.objects.all()

      data = {
         'genders':genders
      }

      return render(request, 'gender/GendersList.html', data)
   except Exception as e:
     return HttpResponse(f'Error Occured During Loading Gender List: {e}')

@login_required
def add_gender(request):
    try:
      if request.method == 'POST':
        gender = request.POST.get('gender')

        Genders.objects.create(gender=gender).save()
        messages.success(request, 'Gender Added Successfully!')
        return redirect('/gender/list')
      else:
        return render(request, 'gender/AddGender.html')
    except Exception as e: 
        return HttpResponse(f'Error Occurred During Add Gender: {e}')  

@login_required
def edit_gender(request, genderId):
   try:
      if request.method == 'POST':
        genderObj = Genders.objects.get(pk=genderId)

        gender = request.POST.get('gender')    

        genderObj.gender = gender
        genderObj.save()

        messages.success(request, 'Gender Updated Successfully')

        data = {
         'gender': genderObj
      }

        return render(request, 'gender/EditGender.html', data)
      else:
        genderObj = Genders.objects.get(pk=genderId)

      data = {
         'gender': genderObj
      }

      return render(request, 'gender/EditGender.html', data)
   
   except Exception as e:
      return HttpResponse(f'Error Occurred During Edit Gender: {e}')

@login_required 
def delete_gender(request, genderId):
    try:
        if request.method == 'POST':
          genderObj = Genders.objects.get(pk=genderId)
          genderObj.delete()

          messages.success(request, 'Gender Deleted Successfully')
          return redirect('/gender/list')

        else:
          genderObj = Genders.objects.get(pk=genderId)

        data = {
            'gender': genderObj
        }

        return render(request, 'gender/DeleteGender.html', data)
    except Exception as e:
        return HttpResponse(f'Error Occurred During Delete Gender: {e}')

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print("POST username:", username)
        print("POST password:", password)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/gender/list')
        else:
            error_message = "Invalid login credentials"
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')



@login_required
def user_list(request):
    try:
        search_query = request.GET.get('search', '')
        
        # Filter users based on the search query across all fields
        if search_query:
            userObj = Users.objects.filter(
                Q(full_name__icontains=search_query) |
                Q(gender__gender__iexact=search_query) |
                Q(birth_date__icontains=search_query) |
                Q(address__icontains=search_query) |
                Q(contact_number__icontains=search_query) |
                Q(email__icontains=search_query)
            ).select_related('gender')
        else:
            userObj = Users.objects.select_related('gender')

        # Pagination logic
        paginator = Paginator(userObj, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Render the table body as HTML
        table_html = render_to_string('user/user_table_body.html', {'page_obj': page_obj})

        # Check if request is AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'html': table_html})

        # Render page with data
        data = {
            'page_obj': page_obj,
            'search_query': search_query
        }
        return render(request, 'user/UsersList.html', data)

    except Exception as e:
        return HttpResponse(f'Error Occurred During Loading User List: {e}')

@login_required
def add_user(request):
    if request.method == 'POST':
        # Retrieve data from the form
        full_name = request.POST.get('full_name')
        gender = request.POST.get('gender')  # Get gender ID from form submission
        birth_date = request.POST.get('birth_date')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check if any required fields are empty
        errors = {}
        if not full_name:
            errors['full_name'] = "Full name is required."
        if not gender:
            errors['gender'] = "Gender is required."
        if not birth_date:
            errors['birth_date'] = "Birth date is required."
        if not address:
            errors['address'] = "Address is required."
        if not contact_number:
            errors['contact_number'] = "Contact number is required."
        if not username:
            errors['username'] = "Username is required."
        if not password:
            errors['password'] = "Password is required."
        if not confirm_password:
            errors['confirm_password'] = "Confirm password is required."
        elif password != confirm_password:
            errors['confirm_password'] = "Passwords do not match."
        if Users.objects.filter(username=username).exists():
            errors['username'] = "Username already exists."

        # If there are errors, return the form with errors and retain values
        if errors:
            genders = Genders.objects.all()
            return render(request, 'user/AddUser.html', {
                'errors': errors,
                'full_name': full_name,
                'gender': gender,  # Pass the selected gender ID to the template
                'birth_date': birth_date,
                'address': address,
                'contact_number': contact_number,
                'email': email,
                'username': username,
                'genders': genders,  # Pass genders back to the template
            })

        # Create new user if no errors
        try:
            user = Users(
                full_name=full_name,
                gender=Genders.objects.get(gender_id=gender),  # Use the gender ID to retrieve the gender object
                birth_date=birth_date,
                address=address,
                contact_number=contact_number,
                email=email,
                username=username,
                password=password  # Securely hash the password
            )
            user.save()
            messages.success(request, "User added successfully!")
            return redirect('user_list')

        except ValidationError as e:
            return HttpResponse(f"Invalid data: {e}")
    else:
        # If not a POST request, just render the empty form
        genders = Genders.objects.all()
        return render(request, 'user/AddUser.html', {'genders': genders})

@login_required 
def edit_user(request, id):
    user_obj = get_object_or_404(Users, user_id=id)

    if request.method == 'POST':
        # Retrieve data from the form
        full_name = request.POST.get('full_name')
        gender = request.POST.get('gender')
        birth_date = request.POST.get('birth_date', user_obj.birth_date)  # Default to user's birth_date if not in POST
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')
        email = request.POST.get('email')
        username = request.POST.get('username')

        # Manual validation
        errors = {}
        if not full_name:
            errors['full_name'] = "Full name is required."
        if not gender:
            errors['gender'] = "Gender is required."
        if not birth_date:
            errors['birth_date'] = "Birth date is required."
        if not address:
            errors['address'] = "Address is required."
        if not contact_number:
            errors['contact_number'] = "Contact number is required."
        if not username:
            errors['username'] = "Username is required."
        elif username != user_obj.username and Users.objects.filter(username=username).exists():
            errors['username'] = "Username already exists."

        # If there are errors, return to form with current values
        if errors:
            genders = Genders.objects.all()
            return render(request, 'user/EditUser.html', {
                'user': user_obj,
                'genders': genders,
                'errors': errors,
                'full_name': full_name,
                'gender_id': gender,
                'birth_date': birth_date,  # Ensure birth_date is passed back
                'address': address,
                'contact_number': contact_number,
                'email': email,
                'username': username,
            })

        # Update user if no errors
        user_obj.full_name = full_name
        user_obj.gender = Genders.objects.get(pk=gender)
        user_obj.birth_date = birth_date
        user_obj.address = address
        user_obj.contact_number = contact_number
        user_obj.email = email
        user_obj.username = username
        user_obj.save()

        messages.success(request, "User updated successfully!")
        return redirect('/user/list')

    else:
        genders = Genders.objects.all()
        return render(request, 'user/EditUser.html', {
            'user': user_obj,
            'genders': genders
        })

@login_required  
def delete_user(request, id):
    user = get_object_or_404(Users, pk=id)
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, 'User deleted successfully!')
        return redirect('/user/list')  # Or use `reverse()`

    # If GET, show confirmation page
    return render(request, 'user/DeleteUser.html', {'user': user})