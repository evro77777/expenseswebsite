import csv

import xlwt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from userpreferences.models import *

from expenses.models import Category, Expense
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
import json
import datetime


def search_expenses(request):
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')

        expenses = Expense.objects.filter(
            amount__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            date__istartswith=search_str, owner=request.user) | Expense.objects.filter(
            description__icontains=search_str, owner=request.user) | Expense.objects.filter(
            category__icontains=search_str, owner=request.user)

        data = expenses.values()
        return JsonResponse(list(data), safe=False)


@login_required(login_url='authentication/login')
def index(request):
    currency = UserPreference.objects.get(user=request.user).currency \
        if UserPreference.objects.filter(user=request.user).exists() else ''
    expenses = Expense.objects.filter(owner=request.user)
    paginator = Paginator(expenses, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'expenses': expenses,
        'page_obj': page_obj,
        'currency': currency,
        'flag': 'expenses'
    }
    return render(request, 'expenses/index.html', context)


@login_required(login_url='authentication/login')
def add_edit_expense(request, uid=None):
    categories = Category.objects.all()
    if uid:
        expense = Expense.objects.get(pk=uid)
        context = {
            'expense': expense,
            'values': expense,
            'categories': categories,
            'mode': 'edit_mode',
            'title': 'Edit Expense',
            'flag': 'expense'
        }

    else:
        context = {
            'categories': categories,
            'values': request.POST,
            'mode': 'add_mode',
            'title': 'Add Expense',
            'flag': 'expense'
        }

    if request.method == 'POST':
        amount = request.POST["amount"]
        description = request.POST["description"]
        category = request.POST["category"]
        date = request.POST["expense_date"]
        if not (amount and description and category and date):
            messages.error(request, 'All fields is required')
            return render(request, 'common/add_edit_income_expense.html', context)
        if uid:
            expense.amount = amount
            expense.category = category
            expense.date = date
            expense.description = description
            expense.owner = request.user
            expense.save()

        else:
            Expense.objects.create(amount=amount, category=category, date=date, description=description,
                                   owner=request.user)
        messages.success(request, 'Expense saved successfully')
        return redirect('expenses')
    return render(request, 'common/add_edit_income_expense.html', context)


def delete_expense(request, uid):
    expense = Expense.objects.get(pk=uid)
    expense.delete()
    messages.success(request, 'Expense removed')
    return redirect('expenses')


def expense_category_summary(request):
    todays_date = datetime.date.today()
    six_moths_ago = todays_date - datetime.timedelta(days=30 * 6)
    expenses = Expense.objects.filter(date__gte=six_moths_ago, date__lte=todays_date, owner=request.user)
    finalrep = {}

    def get_category(expense):
        return expense.category

    def get_expense_category_amount(category):
        amount = 0
        filtered_by_category = expenses.filter(category=category)
        for item in filtered_by_category:
            amount += item.amount
        return amount

    category_list = list(set(map(get_category, expenses)))

    for cat in category_list:
        finalrep[cat] = get_expense_category_amount(cat)

    return JsonResponse({'expense_category_data': finalrep}, safe=False)


def stats_view(request):
    return render(request, 'expenses/stats.html', {'flag': 'expense_stats'})


def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + str(datetime.datetime.now()) + '.csv'
    writer = csv.writer(response)
    writer.writerow(['Amount', 'Description', 'Category', 'Date'])
    expenses = Expense.objects.filter(owner=request.user)
    for expense in expenses:
        writer.writerow([expense.amount, expense.description, expense.category, expense.date])

    return response


def export_excel(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Expenses' + str(datetime.datetime.now()) + '.xls'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Expenses')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns = ['Amount', 'Descrption', 'Category', 'Date']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()

    rows = Expense.objects.filter(owner=request.user).values_list('amount', 'description', 'category', 'date')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)
    wb.save(response)

    return response


def income_stats_view(request):
    pass
