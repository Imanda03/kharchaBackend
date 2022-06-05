from django.contrib import admin
from .models import AccountBook, Transaction

# Register your models here.
admin.site.register(AccountBook)
admin.site.register(Transaction)
