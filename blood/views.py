from django.shortcuts import render, redirect
from . import forms, models
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import logout as auth_logout
from django.contrib import messages
from donor import models as dmodels
from patient import models as pmodels
from donor import forms as dforms
from patient import forms as pforms


def home_view(request):
    x = models.Stock.objects.all()
    if len(x) == 0:
        for bg in ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]:
            models.Stock.objects.create(bloodgroup=bg, unit=0)

    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    
    stocks = models.Stock.objects.all()
    total_donors = dmodels.Donor.objects.all().count()
    total_requests = models.BloodRequest.objects.all().count()
    approved_requests = models.BloodRequest.objects.filter(status='Approved').count()
    total_units_sum = models.Stock.objects.aggregate(Sum('unit'))
    total_units = total_units_sum['unit__sum'] if total_units_sum['unit__sum'] is not None else 0

    context = {
        'stocks': stocks,
        'total_donors': total_donors,
        'total_requests': total_requests,
        'approved_requests': approved_requests,
        'total_units': total_units,
    }
    return render(request, 'blood/index.html', context=context)


def logout_view(request):
    auth_logout(request)
    return redirect('/')


def is_donor(user):
    return user.groups.filter(name='DONOR').exists()


def is_patient(user):
    return user.groups.filter(name='PATIENT').exists()


def afterlogin_view(request):
    if is_donor(request.user):
        return redirect('donor/donor-dashboard')
    elif is_patient(request.user):
        return redirect('patient/patient-dashboard')
    else:
        return redirect('admin-dashboard')


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    totalunit = models.Stock.objects.aggregate(Sum('unit'))
    dict = {
        'A1': models.Stock.objects.get(bloodgroup="A+"),
        'A2': models.Stock.objects.get(bloodgroup="A-"),
        'B1': models.Stock.objects.get(bloodgroup="B+"),
        'B2': models.Stock.objects.get(bloodgroup="B-"),
        'AB1': models.Stock.objects.get(bloodgroup="AB+"),
        'AB2': models.Stock.objects.get(bloodgroup="AB-"),
        'O1': models.Stock.objects.get(bloodgroup="O+"),
        'O2': models.Stock.objects.get(bloodgroup="O-"),
        'totaldonors': dmodels.Donor.objects.all().count(),
        'totalbloodunit': totalunit['unit__sum'],
        'totalrequest': models.BloodRequest.objects.all().count(),
        'totalapprovedrequest': models.BloodRequest.objects.all().filter(status='Approved').count()
    }
    return render(request, 'blood/admin_dashboard.html', context=dict)


@login_required(login_url='adminlogin')
def admin_blood_view(request):
    dict = {
        'bloodForm': forms.BloodForm(),
        'A1': models.Stock.objects.get(bloodgroup="A+"),
        'A2': models.Stock.objects.get(bloodgroup="A-"),
        'B1': models.Stock.objects.get(bloodgroup="B+"),
        'B2': models.Stock.objects.get(bloodgroup="B-"),
        'AB1': models.Stock.objects.get(bloodgroup="AB+"),
        'AB2': models.Stock.objects.get(bloodgroup="AB-"),
        'O1': models.Stock.objects.get(bloodgroup="O+"),
        'O2': models.Stock.objects.get(bloodgroup="O-"),
    }
    if request.method == 'POST':
        bloodForm = forms.BloodForm(request.POST)
        if bloodForm.is_valid():
            bloodgroup = bloodForm.cleaned_data['bloodgroup']
            stock = models.Stock.objects.get(bloodgroup=bloodgroup)
            stock.unit = bloodForm.cleaned_data['unit']
            stock.save()
            messages.success(request, f"Successfully updated {bloodgroup} stock to {stock.unit} units.")
        else:
            messages.error(request, "Please choose a valid blood group and enter a valid unit quantity.")
        return HttpResponseRedirect('admin-blood')
    return render(request, 'blood/admin_blood.html', context=dict)


@login_required(login_url='adminlogin')
def admin_donor_view(request):
    donors = dmodels.Donor.objects.all()
    return render(request, 'blood/admin_donor.html', {'donors': donors})


@login_required(login_url='adminlogin')
def update_donor_view(request, pk):
    donor = dmodels.Donor.objects.get(id=pk)
    user = dmodels.User.objects.get(id=donor.user_id)
    userForm = dforms.DonorUserForm(instance=user)
    donorForm = dforms.DonorForm(request.FILES, instance=donor)
    mydict = {'userForm': userForm, 'donorForm': donorForm}
    if request.method == 'POST':
        userForm = dforms.DonorUserForm(request.POST, instance=user)
        donorForm = dforms.DonorForm(request.POST, request.FILES, instance=donor)
        if userForm.is_valid() and donorForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            donor = donorForm.save(commit=False)
            donor.user = user
            donor.bloodgroup = donorForm.cleaned_data['bloodgroup']
            donor.save()
            messages.success(request, f"Donor {donor.get_name} updated successfully.")
            return redirect('admin-donor')
    return render(request, 'blood/update_donor.html', context=mydict)


@login_required(login_url='adminlogin')
def delete_donor_view(request, pk):
    donor = dmodels.Donor.objects.get(id=pk)
    donor_name = donor.get_name
    user = User.objects.get(id=donor.user_id)
    user.delete()
    donor.delete()
    messages.info(request, f"Donor {donor_name} removed.")
    return HttpResponseRedirect('/admin-donor')


@login_required(login_url='adminlogin')
def admin_patient_view(request):
    patients = pmodels.Patient.objects.all()
    return render(request, 'blood/admin_patient.html', {'patients': patients})


@login_required(login_url='adminlogin')
def update_patient_view(request, pk):
    patient = pmodels.Patient.objects.get(id=pk)
    user = pmodels.User.objects.get(id=patient.user_id)
    userForm = pforms.PatientUserForm(instance=user)
    patientForm = pforms.PatientForm(request.FILES, instance=patient)
    mydict = {'userForm': userForm, 'patientForm': patientForm}
    if request.method == 'POST':
        userForm = pforms.PatientUserForm(request.POST, instance=user)
        patientForm = pforms.PatientForm(request.POST, request.FILES, instance=patient)
        if userForm.is_valid() and patientForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            patient = patientForm.save(commit=False)
            patient.user = user
            patient.bloodgroup = patientForm.cleaned_data['bloodgroup']
            patient.save()
            messages.success(request, f"Patient {patient.get_name} updated successfully.")
            return redirect('admin-patient')
    return render(request, 'blood/update_patient.html', context=mydict)


@login_required(login_url='adminlogin')
def delete_patient_view(request, pk):
    patient = pmodels.Patient.objects.get(id=pk)
    patient_name = patient.get_name
    user = User.objects.get(id=patient.user_id)
    user.delete()
    patient.delete()
    messages.info(request, f"Patient {patient_name} removed.")
    return HttpResponseRedirect('/admin-patient')


@login_required(login_url='adminlogin')
def admin_request_view(request):
    requests = models.BloodRequest.objects.all().filter(status='Pending')
    return render(request, 'blood/admin_request.html', {'requests': requests})


@login_required(login_url='adminlogin')
def admin_request_history_view(request):
    requests = models.BloodRequest.objects.all().exclude(status='Pending')
    return render(request, 'blood/admin_request_history.html', {'requests': requests})


@login_required(login_url='adminlogin')
def admin_donation_view(request):
    donations = dmodels.BloodDonate.objects.all()
    return render(request, 'blood/admin_donation.html', {'donations': donations})


@login_required(login_url='adminlogin')
def update_approve_status_view(request, pk):
    req = models.BloodRequest.objects.get(id=pk)
    bloodgroup = req.bloodgroup
    unit = req.unit
    stock = models.Stock.objects.get(bloodgroup=bloodgroup)
    if stock.unit >= unit:
        stock.unit = stock.unit - unit
        stock.save()
        req.status = "Approved"
        req.save()
        messages.success(request, f"Approved request for {req.patient_name} ({unit} unit(s) of {bloodgroup}). Stock updated.")
    else:
        messages.error(request, f"Cannot approve request! Only {stock.unit} unit(s) of {bloodgroup} available.")

    return redirect('admin-request')


@login_required(login_url='adminlogin')
def update_reject_status_view(request, pk):
    req = models.BloodRequest.objects.get(id=pk)
    req.status = "Rejected"
    req.save()
    messages.warning(request, f"Rejected blood request for {req.patient_name}.")
    return HttpResponseRedirect('/admin-request')


@login_required(login_url='adminlogin')
def approve_donation_view(request, pk):
    donation = dmodels.BloodDonate.objects.get(id=pk)
    if donation.status != 'Approved':
        donation_blood_group = donation.bloodgroup
        donation_blood_unit = donation.unit

        stock = models.Stock.objects.get(bloodgroup=donation_blood_group)
        stock.unit = stock.unit + donation_blood_unit
        stock.save()

        donation.status = 'Approved'
        donation.save()
        messages.success(request, f"Donation of {donation_blood_unit} unit(s) of {donation_blood_group} approved and added to inventory.")
    else:
        messages.info(request, "This donation is already approved.")
    return HttpResponseRedirect('/admin-donation')


@login_required(login_url='adminlogin')
def reject_donation_view(request, pk):
    donation = dmodels.BloodDonate.objects.get(id=pk)
    if donation.status != 'Approved':
        donation.status = 'Rejected'
        donation.save()
        messages.warning(request, f"Donation rejected.")
    return HttpResponseRedirect('/admin-donation')