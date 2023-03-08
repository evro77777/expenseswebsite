from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path('', views.index, name='incomes'),
    path('add_income/', views.add_edit_income, name='add_income'),
    path('edit_income/<int:uid>/', views.add_edit_income, name='edit_income'),
    path('delete_income/<int:uid>/', views.delete_income, name='delete_income'),
    path('search_incomes/', csrf_exempt(views.search_incomes), name='search_incomes'),
    path('income_source_summary/', views.income_source_summary, name='income_source_summary'),
    path('income_stats/', views.income_stats_view, name='income_stats'),
    # path('test/',views.test, name='test')
    # path('test_add/',views.add_edit_expense, name='test_add'),
    # path('test_edit/<int:uid>/',views.add_edit_expense, name='test_edit')
]
