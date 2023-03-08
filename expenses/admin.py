from django.contrib import admin
from .models import Expense, Category


class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('amount', 'description', 'owner', 'date')
    search_field = ('amount', 'description', 'owner', 'date')
    list_per_page = 10


admin.site.register(Expense, ExpenseAdmin)
admin.site.register(Category)

# Register your models here.
