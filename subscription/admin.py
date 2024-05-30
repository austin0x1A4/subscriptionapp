from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth.models import User
from .models import InvestmentModel, UserProfile

class InvestmentModelInline(admin.TabularInline):
    model = InvestmentModel
    extra = 0
    readonly_fields = ('investment_amount', 'start_date', 'investment_duration')

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    readonly_fields = ('account_number', 'account_balance')

class CustomUserAdmin(DefaultUserAdmin):
    inlines = [UserProfileInline, InvestmentModelInline]
    list_display = ('username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_filter = ('is_staff', 'is_active', 'date_joined')

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

# Unregister the original User admin and register the new one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

class UserFilter(admin.SimpleListFilter):
    title = 'user'
    parameter_name = 'user'

    def lookups(self, request, model_admin):
        users = User.objects.all()
        return [(user.id, user.username) for user in users]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(user__id=self.value())
        return queryset

class InvestmentModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'get_first_name', 'get_last_name', 'get_email', 'investment_amount', 'start_date', 'investment_duration')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')
    list_filter = ('start_date', 'investment_duration', UserFilter)

    def get_first_name(self, obj):
        return obj.user.first_name
    get_first_name.short_description = 'First Name'

    def get_last_name(self, obj):
        return obj.user.last_name
    get_last_name.short_description = 'Last Name'

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

admin.site.register(InvestmentModel, InvestmentModelAdmin)

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_number', 'account_balance')
    search_fields = ('user__username', 'account_number')
    list_filter = ('account_balance',)

admin.site.register(UserProfile, UserProfileAdmin)
