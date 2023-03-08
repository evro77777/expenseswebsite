from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    path('', views.index, name='expenses'),
    path('add_expense/', views.add_edit_expense, name='add_expense'),
    path('edit_expense/<int:uid>/', views.add_edit_expense, name='edit_expense'),
    path('delete_expense/<int:uid>/', views.delete_expense, name='delete_expense'),
    path('search_expenses/', csrf_exempt(views.search_expenses), name='search_expenses'),
    path('expense_category_summary/', views.expense_category_summary, name='expense_category_summary'),
    path('stats/', views.stats_view, name='stats'),
    path('export_csv/', views.export_csv, name='export_csv'),
    path('export_excel/', views.export_excel, name='export_excel'),
    # path('test/',views.test, name='test')
    # path('test_add/',views.add_edit_expense, name='test_add'),
    # path('test_edit/<int:uid>/',views.add_edit_expense, name='test_edit')
]
