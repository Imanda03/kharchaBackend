from django.db import models
from rest_framework import serializers
from .models import AccountBook, Transaction
from django.utils import timezone


class TransactionSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField() #date for outpul

    class Meta:
        model = Transaction
        fields = [
            'id',
            'amount',
            'description',
            'date',
            '_type',
            'account_book'
            ]
        extra_kwargs = {
            "account_book":{"required":False},
        }

    def get_date(self, obj):
        return timezone.localtime(obj.date).strftime("%b. %d, %Y")

    def validate(self, data):
        book_pk = self.context.get("view").kwargs.get("account_book_pk")
        book = AccountBook.objects.get(pk=book_pk)
        data["account_book"] = book
        return data

class AccountBookSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()
    class Meta:
        model = AccountBook
        fields = [
            'id',
            'title',
            'user',
            'created_at',
            'balance',
            'slug'
        ]
        extra_kwargs = {
            "user":{"required":False}
        }
    
    def get_balance(self, obj):
        return obj.balance

    def validate(self, data):
        data["user"] = self.context.get("request").user
        return data


# class TransactionCreateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Transaction
#         fields = ['amount', 'description', '_type']