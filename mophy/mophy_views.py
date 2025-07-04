from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required 
from payment_app.models import * 
from payment_app.serializers import *
from datetime import datetime
from service_providers.models import *
from django.db.models import Sum
from datetime import date
from users.users_views import context_data
from datetime import timedelta
from django.conf import settings
from auth_app.sendsms import comma_separated
from django.db.models import Q
from .helper import *


transaction =  settings.TRANSACTION
fn_approved = "approved"
fn_queued = "queued"
fn_cancelled = "cancelled"



from Widoph_Remit.package import *
from Widoph_Remit.response import *
from auth_app.models import *
from auth_app.serializers import *
from auth_app.helpers import *

############################### Index Page ###############################
""" Index Page """
@login_required(login_url='mophy:login')
def index(request):
    context = context_data(request)

    #total payins, payouts and pending payouts
    pay = payins_payouts(request)

    context.update(pending_payouts=pay['pending_payout'], total_payins = pay['payin'], 
            total_payouts = pay['payout'], 
            new_customers = total_new_customers(), 
            pending_review_and_processing_transactions = Transaction_details.objects.filter(payment_status=transaction['pending_review']).count(), 
            incomplete_transactions = Transaction_details.objects.filter(payment_status=transaction['incomplete']).count(), 
            pending_transactions = Transaction_details.objects.filter(payment_status=transaction['pending_payment']).count(), 
            approved_transactions = Transaction_details.objects.filter(tm_status=fn_approved).count(), 
            cancelled_transactions = Transaction_details.objects.filter(payment_status=transaction['cancelled']).count(), 
            queued_transactions = Transaction_details.objects.filter(tm_status=fn_queued).count()
        )

    #remittance by corridors data 
    post_dict = remittance_by_corridors(request)
    context.update(post_dict)
    return render(request, "mophy/index.html",context)


############################### Extra Views ###############################

def index_filter(index_time):
    today = date.today()  
    filter_time = today - timedelta(days=int(7))
    if filter_time == "all":
        new_customers = total_new_customers()
        pending_transactions = Transaction_details.objects.filter(payment_status=transaction['pending_payment']).count()
        incomplete_transactions = Transaction_details.objects.filter(payment_status=transaction['incomplete']).count()
        pending_review_and_processing_transactions = Transaction_details.objects.filter(payment_status=transaction['pending_review']).count()
        approved_transactions = Transaction_details.objects.filter(tm_status=fn_approved).count()
        cancelled_transactions = Transaction_details.objects.filter(tm_status=fn_cancelled).count()
        queue_transactions =   Transaction_details.objects.filter(tm_status=fn_queued).count()
    else:
        new_customers = total_new_customers()
        pending_transactions = Transaction_details.objects.filter(date__gte=filter_time, payment_status=transaction['pending_payment']).count()
        incomplete_transactions = Transaction_details.objects.filter(date__gte=filter_time, payment_status=transaction['incomplete']).count()
        pending_review_and_processing_transactions = Transaction_details.objects.filter(date__gte=filter_time, payment_status=transaction['pending_review'])
        approved_transactions = Transaction_details.objects.filter(date__gte=filter_time, tm_status=fn_approved).count()
        cancelled_transactions = Transaction_details.objects.filter(date__gte=filter_time, tm_status=fn_cancelled).count()
        queued_transactions =   Transaction_details.objects.filter(date__gte=filter_time, tm_status=fn_queued).count()
    return {"new_customers":new_customers,"pending_review_and_processing_transactions":pending_review_and_processing_transactions,"incomplete_transactions":incomplete_transactions, "pending_transactions":pending_transactions,"approved_transactions":approved_transactions,"cancelled_transactions":cancelled_transactions,"queued_transactions":queued_transactions}

@login_required(login_url='mophy:login')
def index2(request):
    context={
        "page_title":"Dashboard"
    }
    return render(request,'mophy/index-2.html',context)

@login_required(login_url='mophy:login')
def ui_alert(request):
    context={
        "page_title":"Alert"
    }
    return render(request,'mophy/bootstrap/ui-alert.html',context)

@login_required(login_url='mophy:login')
def ui_button(request):
    context={
        "page_title":"Button"
    }
    return render(request,'mophy/bootstrap/ui-button.html',context)

@login_required(login_url='mophy:login')
def ui_modal(request):
    context={
        "page_title":"Modal"
    }
    return render(request,'mophy/bootstrap/ui-modal.html',context)

@login_required(login_url='mophy:login')
def ui_button_group(request):
    context={
        "page_title":"Button Group"
    }
    return render(request,'mophy/bootstrap/ui-button-group.html',context)

@login_required(login_url='mophy:login')
def ui_dropdown(request):
    context={
        "page_title":"Dropdown"
    }
    return render(request,'mophy/bootstrap/ui-dropdown.html',context)

@login_required(login_url='mophy:login')
def ui_popover(request):
    context={
        "page_title":"Popover"
    }
    return render(request,'mophy/bootstrap/ui-popover.html',context)

@login_required(login_url='mophy:login')
def ui_pagination(request):
    context={
        "page_title":"Pagination"
    }
    return render(request,'mophy/bootstrap/ui-pagination.html',context)
@login_required(login_url='mophy:login')
def ui_grid(request):
    context={
        "page_title":"Grid"
    }
    return render(request,'mophy/bootstrap/ui-grid.html',context)

@login_required(login_url='mophy:login')
def uc_select2(request):
    context={
        "page_title":"Select"
    }
    return render(request,'mophy/plugins/uc-select2.html',context)


@login_required(login_url='mophy:login')
def uc_sweetalert(request):
    context={
        "page_title":"Sweet Alert"
    }
    return render(request,'mophy/plugins/uc-sweetalert.html',context)

@login_required(login_url='mophy:login')
def uc_toastr(request):
    context={
        "page_title":"Toastr"
    }
    return render(request,'mophy/plugins/uc-toastr.html',context)


@login_required(login_url='mophy:login')
def form_pickers(request):
    context={
        "page_title":"Pickers"
    }
    return render(request,'mophy/forms/form-pickers.html',context)

def page_error_400(request):
    return render(request,'400.html')
    
def page_error_403(request):
    return render(request,'403.html')

def page_error_404(request):
    return render(request,'404.html')

def page_error_500(request):
    return render(request,'500.html')

def page_error_503(request):
    return render(request,'503.html')


