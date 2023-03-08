import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from userincome.models import *
from django.core.paginator import Paginator
from userpreferences.models import UserPreference


@login_required(login_url='authentication/login')
def index(request):
    sources = Source.objects.all()
    incomes = UserIncome.objects.filter(owner=request.user)
    currency = UserPreference.objects.get(user=request.user).currency
    paginator = Paginator(incomes, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'incomes': incomes,
        'page_obj': page_obj,
        'currency': currency,
        'flag': 'incomes'
    }
    return render(request, 'income/index.html', context)


@login_required(login_url='authentication/login')
def add_edit_income(request, uid=None):
    sources = Source.objects.all()
    if uid:
        income = UserIncome.objects.get(pk=uid)
        context = {
            'income': income,
            'values': income,
            'sources': sources,
            'mode': 'edit_mode',
            'title': 'Edit Income',
            'flag': 'income'
        }

    else:
        context = {
            'sources': sources,
            'values': request.POST,
            'mode': 'add_mode',
            'title': 'Add Income',
            'flag': 'income'
        }

    if request.method == 'POST':
        amount = request.POST["amount"]
        description = request.POST["description"]
        source = request.POST["source"]
        date = request.POST["income_date"]
        if not (amount and description and source and date):
            messages.error(request, 'All fields is required')
            return render(request, 'common/add_edit_income_expense.html', context)
        if uid:
            income.amount = amount
            income.source = source
            income.date = date
            income.description = description
            income.owner = request.user
            income.save()

        else:
            UserIncome.objects.create(amount=amount, source=source, date=date, description=description,
                                      owner=request.user)
        messages.success(request, 'Income saved successfully')
        return redirect('incomes')
    return render(request, 'common/add_edit_income_expense.html', context)


def delete_income(request, uid):
    income = UserIncome.objects.get(pk=uid)
    income.delete()
    messages.success(request, 'Income removed')
    return redirect('incomes')


def search_incomes(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')

        incomes = UserIncome.objects.filter(
            amount__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            date__istartswith=search_str, owner=request.user) | UserIncome.objects.filter(
            description__icontains=search_str, owner=request.user) | UserIncome.objects.filter(
            source__icontains=search_str, owner=request.user)

        data = incomes.values()
        return JsonResponse(list(data), safe=False)


def income_source_summary(request):
    incomes = UserIncome.objects.filter(owner=request.user)
    finalrep = {}

    def get_source(income):
        return income.source

    def get_income_source_amount(source):
        amount = 0
        filtered_by_source = incomes.filter(source=source)
        for item in filtered_by_source:
            amount += item.amount
        return amount

    source_list = list(set(map(get_source, incomes)))

    for src in source_list:
        finalrep[src] = get_income_source_amount(src)

    return JsonResponse({'income_source_data': finalrep}, safe=False)


def income_stats_view(request):
    return render(request, 'income/income_stats.html', {'flag': 'income_stats'})
