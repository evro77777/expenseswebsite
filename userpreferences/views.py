from django.contrib import messages
from django.shortcuts import render
import os
import json
from django.conf import settings
from .models import UserPreference


def index(request):
    exists = UserPreference.objects.filter(user=request.user).exists()
    user_preferences = UserPreference.objects.get(user=request.user) if exists else None
    currency_data = []
    file_path = os.path.join(settings.BASE_DIR, 'currencies.json')
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
        for k, v in data.items():
            currency_data.append({'name': k, 'value': v})

    if request.method == 'GET':
        return render(request, 'preferences/index.html', {'currencies': currency_data,
                                                          'user_preferences': user_preferences,
                                                          'flag': 'preferences'})
    else:
        currency = request.POST['currency']
        if exists:
            user_preferences.currency = currency
            user_preferences.save()
        else:
            UserPreference.objects.create(user=request.user, currency=currency)
        messages.success(request, 'Changes saved')

        return render(request, 'preferences/index.html', {'currencies': currency_data,
                                                          'user_preferences': user_preferences,
                                                          'flag': 'preferences'})
