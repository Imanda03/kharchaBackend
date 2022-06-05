from django.contrib.auth.models import Group
from django.contrib import admin
from .models import *
from .forms import UserChangeForm
from django.contrib.auth.admin import UserAdmin


# Text to put at the end of each page's <title>.
admin.site.site_title = "Kharcha | Admin"

# Text to put in each page's <h1> (and above login form).
admin.site.site_header = "Sharing is Caring Administration"

# Text to put at the top of the admin index page.
admin.site.index_title = "Home"


class CustomUserAdmin(UserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ("Personal Info", {'fields': ('first_name', 'last_name','gender','phone',"avatar")}),
        ("Status", {'fields': ('is_active',"email_verified",'is_staff', "is_superuser")}),
        ('Permissions', {'fields': ('role',)}),
        ('Important dates', {'fields': ("date_joined",'last_login',)}),
    )
    add_fieldsets = (
        ("Required", {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
        ("Meta", {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name','role')}
        ),
    )
    list_display = ["id","email", "first_name","last_name","role"]
    list_display_links = ['email']
    search_fields = ('email','first_name','last_name')
    search_help_text = "Search helps by title and ID"
    show_full_result_count = True
    save_as = True
    ordering = ('email','id','first_name','last_name')
    list_filter = [
        'role',
        'gender',
        'is_active',
        'email_verified',
        ]

class CustomerAdmin(CustomUserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ("Personal Info", {'fields': ('first_name', 'last_name','gender','phone',"avatar","dob")}),
        ("Status", {'fields': ('is_active',"email_verified",'is_staff', "is_superuser")}),
        ('Permissions', {'fields': ('role',)}),
        ('Important dates', {'fields': ("date_joined",'last_login',)}),
    )
    add_fieldsets = (
        ("Required", {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')}
        ),
        ("Meta", {
            'classes': ('wide',),
            'fields': ('first_name', 'last_name','role',"dob")}
        ),
    )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Customer, CustomerAdmin)
admin.site.register(UserToken)
admin.site.unregister(Group)