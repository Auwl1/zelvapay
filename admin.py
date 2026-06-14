# admin.py — ZelvaPay / AjosData Django Admin Customization
# Place this in your vtuapp/admin.py (or whichever app has your models)
# 
# Run after: python manage.py createsuperuser
# Access at: yourdomain.com/admin/

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.urls import path
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
import json

# ── Import your models (adjust names to match yours) ─────────────────────────
from .models import (
    CustomUser,           # your user model
    Wallet,               # user wallets
    Transaction,          # all transactions
    Plan,                 # data plans
    WebsiteConfiguration, # site settings
    # Add others as needed: VirtualCard, GiftCard, etc.
)


# ── SITE HEADER ──────────────────────────────────────────────────────────────
admin.site.site_header  = "ZelvaPay Admin"
admin.site.site_title   = "ZelvaPay"
admin.site.index_title  = "Control Panel"


# ══════════════════════════════════════════════════════════════════════════════
# USER ADMIN
# ══════════════════════════════════════════════════════════════════════════════

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ('email', 'FullName', 'phone', 'plan_badge', 'wallet_balance',
                     'is_active', 'date_joined', 'user_actions')
    list_filter   = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('email', 'FullName', 'phone')
    ordering      = ('-date_joined',)
    list_per_page = 50

    readonly_fields = ('date_joined', 'last_login', 'wallet_balance_display')

    fieldsets = (
        ('Personal Info', {
            'fields': ('email', 'FullName', 'phone', 'password')
        }),
        ('Account Status', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')
        }),
        ('Wallet Info', {
            'fields': ('wallet_balance_display',),
            'description': 'Read-only. Use "Credit Wallet" action to add funds.'
        }),
        ('Dates', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'FullName', 'phone', 'password1', 'password2', 'is_active'),
        }),
    )

    actions = ['credit_wallet_500', 'credit_wallet_1000', 'suspend_users', 'activate_users']

    def plan_badge(self, obj):
        colors = {'Business': '#6C63FF', 'Pro': '#22D3A5', 'Starter': '#475569'}
        plan = getattr(obj, 'plan', 'Starter')
        color = colors.get(plan, '#475569')
        return format_html(
            '<span style="background:{}20;color:{};padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700">{}</span>',
            color, color, plan
        )
    plan_badge.short_description = 'Plan'

    def wallet_balance(self, obj):
        try:
            wallet = obj.wallet
            color = '#22D3A5' if wallet.balance > 0 else '#F87171'
            return format_html(
                '<strong style="color:{};font-family:monospace">₦{:,.2f}</strong>',
                color, wallet.balance
            )
        except Exception:
            return format_html('<span style="color:#475569">No wallet</span>')
    wallet_balance.short_description = 'Balance'

    def wallet_balance_display(self, obj):
        try:
            return f"₦{obj.wallet.balance:,.2f}"
        except Exception:
            return "No wallet"
    wallet_balance_display.short_description = 'Wallet Balance'

    def user_actions(self, obj):
        return format_html(
            '<a style="color:#6C63FF;text-decoration:none;font-size:12px" '
            'href="/admin/vtuapp/customuser/{}/change/">Edit</a>',
            obj.pk
        )
    user_actions.short_description = 'Action'

    # ── BULK ACTIONS ─────────────────────────────────────────────────────────
    @admin.action(description='Credit ₦500 to selected users')
    def credit_wallet_500(self, request, queryset):
        count = 0
        for user in queryset:
            try:
                wallet = user.wallet
                wallet.balance += 500
                wallet.save()
                count += 1
            except Exception:
                pass
        self.message_user(request, f'₦500 credited to {count} wallets.', messages.SUCCESS)

    @admin.action(description='Credit ₦1,000 to selected users')
    def credit_wallet_1000(self, request, queryset):
        count = 0
        for user in queryset:
            try:
                wallet = user.wallet
                wallet.balance += 1000
                wallet.save()
                count += 1
            except Exception:
                pass
        self.message_user(request, f'₦1,000 credited to {count} wallets.', messages.SUCCESS)

    @admin.action(description='Suspend selected users')
    def suspend_users(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users suspended.', messages.WARNING)

    @admin.action(description='Activate selected users')
    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users activated.', messages.SUCCESS)


# ══════════════════════════════════════════════════════════════════════════════
# WALLET ADMIN
# ══════════════════════════════════════════════════════════════════════════════

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display  = ('user', 'balance_display', 'total_funded', 'total_spent', 'updated_at')
    search_fields = ('user__email', 'user__FullName')
    list_filter   = ('updated_at',)
    ordering      = ('-balance',)
    readonly_fields = ('user', 'total_funded', 'total_spent')
    list_per_page = 50

    fieldsets = (
        ('Wallet Owner', {'fields': ('user',)}),
        ('Balance', {'fields': ('balance',)}),
        ('Stats (Read Only)', {'fields': ('total_funded', 'total_spent'), 'classes': ('collapse',)}),
    )

    def balance_display(self, obj):
        color = '#22D3A5' if obj.balance > 0 else '#F87171'
        return format_html(
            '<strong style="color:{};font-family:monospace">₦{:,.2f}</strong>',
            color, obj.balance
        )
    balance_display.short_description = 'Balance'
    balance_display.admin_order_field = 'balance'

    def total_funded(self, obj):
        total = obj.user.transaction_set.filter(
            transaction_type='funding', status='success'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        return format_html('<span style="color:#22D3A5;font-family:monospace">₦{:,.2f}</span>', total)
    total_funded.short_description = 'Total Funded'

    def total_spent(self, obj):
        total = obj.user.transaction_set.filter(
            status='success'
        ).exclude(transaction_type='funding').aggregate(Sum('amount'))['amount__sum'] or 0
        return format_html('<span style="color:#F87171;font-family:monospace">₦{:,.2f}</span>', total)
    total_spent.short_description = 'Total Spent'


# ══════════════════════════════════════════════════════════════════════════════
# TRANSACTION ADMIN
# ══════════════════════════════════════════════════════════════════════════════

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display  = ('reference', 'user', 'type_badge', 'amount_display',
                     'status_badge', 'provider', 'created_at', 'txn_actions')
    list_filter   = ('status', 'transaction_type', 'created_at')
    search_fields = ('reference', 'user__email', 'user__FullName', 'phone_number')
    ordering      = ('-created_at',)
    list_per_page = 50
    date_hierarchy = 'created_at'

    readonly_fields = ('reference', 'user', 'transaction_type', 'amount',
                       'status', 'provider', 'phone_number', 'created_at',
                       'api_response_display')

    fieldsets = (
        ('Transaction Info', {
            'fields': ('reference', 'user', 'transaction_type', 'phone_number')
        }),
        ('Financial', {
            'fields': ('amount', 'status', 'provider')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
        ('API Response (Debug)', {
            'fields': ('api_response_display',),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_success', 'mark_failed', 'refund_to_wallet']

    def type_badge(self, obj):
        colors = {
            'data': '#6C63FF', 'airtime': '#22D3A5',
            'electricity': '#F97316', 'cable': '#38BDF8',
            'funding': '#22D3A5', 'transfer': '#A78BFA',
            'giftcard': '#F87171',
        }
        t = getattr(obj, 'transaction_type', '').lower()
        color = colors.get(t, '#475569')
        return format_html(
            '<span style="background:{}20;color:{};padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;text-transform:uppercase">{}</span>',
            color, color, t
        )
    type_badge.short_description = 'Type'

    def amount_display(self, obj):
        is_credit = getattr(obj, 'transaction_type', '') == 'funding'
        color = '#22D3A5' if is_credit else '#F87171'
        sign = '+' if is_credit else '-'
        return format_html(
            '<strong style="color:{};font-family:monospace">{} ₦{:,.2f}</strong>',
            color, sign, obj.amount
        )
    amount_display.short_description = 'Amount'
    amount_display.admin_order_field = 'amount'

    def status_badge(self, obj):
        colors = {'success': '#22D3A5', 'pending': '#F97316', 'failed': '#F87171'}
        color = colors.get(obj.status, '#475569')
        return format_html(
            '<span style="background:{}20;color:{};padding:2px 8px;border-radius:4px;font-size:11px;font-weight:700;text-transform:uppercase">{}</span>',
            color, color, obj.status
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'

    def api_response_display(self, obj):
        try:
            data = json.loads(obj.api_response) if isinstance(obj.api_response, str) else obj.api_response
            return format_html('<pre style="font-size:12px;color:#94A3B8">{}</pre>', json.dumps(data, indent=2))
        except Exception:
            return obj.api_response or '—'
    api_response_display.short_description = 'API Response'

    def txn_actions(self, obj):
        if obj.status == 'failed':
            return format_html(
                '<a style="color:#22D3A5;font-size:12px;text-decoration:none" '
                'href="/admin/vtuapp/transaction/{}/refund/">Refund</a>',
                obj.pk
            )
        return '—'
    txn_actions.short_description = 'Action'

    # ── BULK ACTIONS ─────────────────────────────────────────────────────────
    @admin.action(description='Mark selected as Success')
    def mark_success(self, request, queryset):
        updated = queryset.update(status='success')
        self.message_user(request, f'{updated} transactions marked successful.', messages.SUCCESS)

    @admin.action(description='Mark selected as Failed')
    def mark_failed(self, request, queryset):
        updated = queryset.update(status='failed')
        self.message_user(request, f'{updated} transactions marked failed.', messages.WARNING)

    @admin.action(description='Refund selected (credit user wallets)')
    def refund_to_wallet(self, request, queryset):
        count = 0
        for txn in queryset.filter(status='failed'):
            try:
                wallet = txn.user.wallet
                wallet.balance += txn.amount
                wallet.save()
                txn.status = 'refunded'
                txn.save()
                count += 1
            except Exception:
                pass
        self.message_user(request, f'{count} refunds issued to user wallets.', messages.SUCCESS)


# ══════════════════════════════════════════════════════════════════════════════
# DATA PLAN ADMIN
# ══════════════════════════════════════════════════════════════════════════════

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display  = ('name', 'network_badge', 'data_size', 'validity',
                     'plan_type', 'price', 'cost_price', 'profit_display',
                     'active_vending_medium', 'is_active_display', 'plan_actions')
    list_filter   = ('network', 'plan_type', 'is_active', 'active_vending_medium')
    search_fields = ('name', 'plan_id')
    ordering      = ('network', 'price')
    list_per_page = 100
    list_editable = ('price', 'cost_price', 'active_vending_medium', 'is_active')

    fieldsets = (
        ('Plan Details', {
            'fields': ('name', 'network', 'plan_type', 'data_size', 'validity', 'plan_id')
        }),
        ('Pricing', {
            'fields': ('price', 'cost_price'),
            'description': 'Set selling price higher than cost price to make profit.'
        }),
        ('API Routing', {
            'fields': ('active_vending_medium',),
            'description': 'Which API provider handles purchases of this plan.'
        }),
        ('Visibility', {
            'fields': ('is_active',)
        }),
    )

    actions = ['activate_plans', 'deactivate_plans', 'switch_to_gsubz', 'switch_to_smeplug',
               'switch_to_vtpass', 'switch_to_autopilotng']

    def network_badge(self, obj):
        colors = {'MTN': '#FBBF24', 'Airtel': '#EF4444', 'Glo': '#22C55E', '9Mobile': '#78716C'}
        color = colors.get(obj.network, '#6B7280')
        return format_html(
            '<span style="color:{};font-weight:700">{}</span>', color, obj.network
        )
    network_badge.short_description = 'Network'
    network_badge.admin_order_field = 'network'

    def profit_display(self, obj):
        try:
            profit = obj.price - obj.cost_price
            color = '#22D3A5' if profit > 0 else '#F87171'
            return format_html(
                '<span style="color:{};font-family:monospace">₦{:,.0f}</span>', color, profit
            )
        except Exception:
            return '—'
    profit_display.short_description = 'Profit'

    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color:#22D3A5;font-weight:700">● Active</span>')
        return format_html('<span style="color:#F87171;font-weight:700">● Off</span>')
    is_active_display.short_description = 'Status'
    is_active_display.admin_order_field = 'is_active'

    def plan_actions(self, obj):
        return format_html(
            '<a style="color:#6C63FF;text-decoration:none;font-size:12px" href="/admin/vtuapp/plan/{}/change/">Edit</a>',
            obj.pk
        )
    plan_actions.short_description = ''

    @admin.action(description='Activate selected plans')
    def activate_plans(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} plans activated.', messages.SUCCESS)

    @admin.action(description='Deactivate selected plans')
    def deactivate_plans(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} plans deactivated.', messages.WARNING)

    @admin.action(description='Switch to GSUBZ')
    def switch_to_gsubz(self, request, queryset):
        updated = queryset.update(active_vending_medium='GSUBZ')
        self.message_user(request, f'{updated} plans switched to GSUBZ.', messages.SUCCESS)

    @admin.action(description='Switch to SMEPlug')
    def switch_to_smeplug(self, request, queryset):
        updated = queryset.update(active_vending_medium='SMEPLUG')
        self.message_user(request, f'{updated} plans switched to SMEPlug.', messages.SUCCESS)

    @admin.action(description='Switch to VTPass')
    def switch_to_vtpass(self, request, queryset):
        updated = queryset.update(active_vending_medium='VTPASS')
        self.message_user(request, f'{updated} plans switched to VTPass.', messages.SUCCESS)

    @admin.action(description='Switch to AutopilotNG')
    def switch_to_autopilotng(self, request, queryset):
        updated = queryset.update(active_vending_medium='AUTOPILOTNG')
        self.message_user(request, f'{updated} plans switched to AutopilotNG.', messages.SUCCESS)


# ══════════════════════════════════════════════════════════════════════════════
# WEBSITE CONFIGURATION ADMIN
# ══════════════════════════════════════════════════════════════════════════════

@admin.register(WebsiteConfiguration)
class WebsiteConfigurationAdmin(admin.ModelAdmin):
    # Only ever one config row — redirect list to the single object
    def changelist_view(self, request, extra_context=None):
        config = WebsiteConfiguration.objects.first()
        if config:
            return HttpResponseRedirect(f'/admin/vtuapp/websiteconfiguration/{config.pk}/change/')
        return super().changelist_view(request, extra_context)

    fieldsets = (
        ('Payment — Monnify', {
            'fields': ('monnify_API_KEY', 'monnify_SECRET_KEY', 'monnify_CONTRACT_CODE',
                       'monnify_BASE_URL'),
        }),
        ('Payment — Paystack', {
            'fields': ('paystack_PUBLIC_KEY', 'paystack_SECRET_KEY'),
        }),
        ('Data Vending — GSUBZ', {
            'fields': ('gsubz_TOKEN', 'gsubz_BASE_URL'),
        }),
        ('Data Vending — SMEPlug', {
            'fields': ('smeplug_API_KEY',),
        }),
        ('Data Vending — VTPass', {
            'fields': ('vtpass_API_KEY', 'vtpass_SECRET_KEY', 'vtpass_PUBLIC_KEY'),
        }),
        ('Data Vending — AutopilotNG', {
            'fields': ('autopilot_TOKEN',),
        }),
        ('Data Vending — OGDAMS', {
            'fields': ('ogdams_API_KEY',),
        }),
        ('Data Vending — GeoDNATech', {
            'fields': ('geodna_API_KEY', 'geodna_USERNAME'),
        }),
        ('Data Vending — DataMall', {
            'fields': ('datamall_TOKEN',),
        }),
        ('Virtual Cards — Sudo Africa', {
            'fields': ('sudo_API_KEY', 'sudo_BUSINESS_ID'),
        }),
        ('Site Settings', {
            'fields': ('site_name', 'support_email', 'support_whatsapp',
                       'maintenance_mode', 'allow_registration',
                       'transfer_fee', 'card_creation_fee', 'airtime_cashback_percent'),
        }),
        ('Service Toggles', {
            'fields': ('data_enabled', 'airtime_enabled', 'electricity_enabled',
                       'cable_enabled', 'virtual_cards_enabled', 'giftcards_enabled',
                       'transfer_enabled', 'exam_enabled'),
        }),
    )
