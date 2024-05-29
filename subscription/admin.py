from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from .models import InvestmentModel, UserProfile

class InvestmentModelInline(admin.TabularInline):
    model = InvestmentModel
    extra = 0
    readonly_fields = ('name', 'last_name', 'email', 'investment_amount', 'start_date', 'investment_duration')

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    readonly_fields = ('account_number', 'account_balance')

class UserAdmin(DefaultUserAdmin):
    inlines = [UserProfileInline, InvestmentModelInline]

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super(UserAdmin, self).get_inline_instances(request, obj)

# Unregister the original User admin and register the new one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

class InvestmentModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'last_name', 'email', 'investment_amount', 'start_date', 'investment_duration')
    search_fields = ('user__username', 'name', 'email')
    list_filter = ('start_date', 'investment_duration')

admin.site.register(InvestmentModel, InvestmentModelAdmin)
