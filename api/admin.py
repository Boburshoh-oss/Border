from django.contrib import admin
from django.contrib.auth.models import User, Group
from .models import *
from import_export.admin import ExportActionMixin, ImportExportModelAdmin

admin.site.site_header = "Santexnika Admin Panel"
admin.site.site_title = "Santexnika API"
admin.site.index_title = "Santexnika API"

admin.site.unregister(Group)
admin.site.register(Kamomad)
admin.site.unregister(User)


admin.site.register(MobilUser)
admin.site.register(MyOwnToken)
admin.site.register(Banner)

@admin.register(MOrder)
class MOrderProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'total')

@admin.register(Telegramid)
class TelegramidProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'telegram_id')

@admin.register(MCart)
class MCartProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'price', 'status')

# admin.site.register(Groups)


class TokenAdmin(admin.ModelAdmin):
    list_display = ('key', 'user', 'created')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'password', 'first_name', 'last_name', 'phone', 'filial')
    # list_display = ('id', 'username', 'password', 'first_name', 'last_name', 'phone', 'filial')


@admin.register(Groups)
class GroupsAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('id', 'name')


@admin.register(Pereotsenka)
class PereotsenkaAdmin(admin.ModelAdmin):
    list_display = ('id', 'filial', 'som', 'dollar', 'date')
    list_filter = ('id', 'filial', 'som', 'dollar', 'date')
    date_hierarchy = 'date'


@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address')


@admin.register(Deliver)
class DeliverAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone1', 'phone2', 'som', 'dollar', 'difference')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'som')


@admin.register(ProductFilial)
class ProductFilialAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ('id', 'som', 'dollar', 'quantity', 'filial', 'barcode')
    search_fields = ('id', 'som', 'dollar', 'quantity', 'filial__name', 'barcode')
    list_filter = ('filial',)


@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('id', 'naqd_som', 'naqd_dollar', 'plastik', 'nasiya_som', 'nasiya_dollar', 'transfer', 'skidka_som', 'skidka_dollar', 'date', 'saler', 'filial')
    search_fields = ('id', 'naqd_som', 'naqd_dollar', 'plastik', 'nasiya_som', 'nasiya_dollar', 'transfer', 'skidka_som', 'skidka_dollar', 'saler', 'filial__name')
    list_filter = ('filial', 'saler')


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'shop', 'product', 'quantity', 'total')
    search_fields = ('id', 'shop', 'product', 'quantity', 'total')


@admin.register(Recieve)
class RecieveAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'som', 'dollar', 'status', 'date')
    search_fields = ('id', 'name', 'som', 'dollar', 'status', 'date')
    date_hierarchy = 'date'


@admin.register(RecieveItem)
class RecieveItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'recieve', 'product', 'som', 'dollar', 'kurs', 'quantity')
    search_fields = ('id', 'recieve', 'product', 'som', 'dollar', 'kurs', 'quantity')


@admin.register(Faktura)
class FakturaAdmin(admin.ModelAdmin):
    list_display = ('id', 'som', 'dollar', 'filial', 'date', 'status', 'difference_som', 'difference_dollar')
    search_fields = ('id', 'som', 'dollar', 'filial', 'date', 'status', 'difference_som', 'difference_dollar')
    date_hierarchy = 'date'
    list_filter = ('filial', 'status')


@admin.register(FakturaItem)
class FakturaItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'faktura', 'product', 'som', 'dollar', 'quantity', 'barcode')
    search_fields = ('id', 'faktura', 'product', 'som', 'dollar', 'quantity', 'barcode')
    list_filter = ('faktura',)


@admin.register(Debtor)
class DebtorAdmin(admin.ModelAdmin):
    list_display = ('id', 'fio', 'phone1', 'phone2', 'som', 'dollar', 'difference')
    search_fields = ('id', 'fio', 'phone1', 'phone2', 'som', 'dollar', 'difference')


# @admin.register(DebtHistory)
# class DebtHistoryAdmin(admin.ModelAdmin):
#     list_display = ('id', 'debtor', 'product', 'debt_quan', 'pay_quan', 'debt', 'pay', 'difference')
#     search_fields = ('id', 'debtor', 'product', 'debt_quan', 'pay_quan', 'debt', 'pay', 'difference')
#     list_filter = ('debtor',)


@admin.register(PayHistory)
class PayHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'debtor', 'som', 'dollar', 'date')
    search_fields = ('id', 'debtor', 'som', 'dollar', 'date')
    list_filter = ('debtor',)
    date_hierarchy = 'date'


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ('id', 'debtor', 'shop', 'date', 'return_date')
    search_fields = ('id', 'debtor', 'shop')
    list_filter = ('debtor',)


@admin.register(CartDebt)
class CartDebtAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'debtor', 'product', 'price', 'given_quan', 'total', 'return_quan', 'return_sum', 'debt_quan', 'debt_sum',
        'difference')
    search_fields = (
        'id', 'debtor', 'product', 'price', 'given_quan', 'total', 'return_quan', 'return_sum', 'debt_quan', 'debt_sum',
        'difference')


@admin.register(ReturnProduct)
class ReturnProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'return_quan', 'som', 'difference', 'date')
    search_fields = ('id', 'product', 'return_quan', 'som', 'difference', 'date')
    date_hierarchy = 'date'

@admin.register(ChangePrice)
class ChangePriceAdmin(admin.ModelAdmin):
    list_display = ('id', 'filial', 'date')
    search_fields = ('id', 'filial', 'date')
    date_hierarchy = 'date'

@admin.register(ChangePriceItem)
class ChangePriceItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'changeprice', 'product', 'old_som', 'old_dollar', 'new_som', 'new_dollar', 'quantity')
    search_fields = ('id', 'changeprice', 'product', 'old_som', 'old_dollar', 'new_som', 'new_dollar', 'quantity')


@admin.register(ReturnProductToDeliver)
class ReturnProductToDeliverAdmin(admin.ModelAdmin):
    list_display = ('id', 'deliver', 'som', 'dollar', 'date')
    date_hierarchy = 'date'


@admin.register(ReturnProductToDeliverItem)
class ReturnProductToDeliverItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'returnproduct', 'product', 'som', 'dollar', 'quantity')

@admin.register(DebtDeliver)
class DebtDeliverAdmin(admin.ModelAdmin):
    list_display = ('id', 'deliver', 'som', 'dollar', 'date')
    search_fields = ('id', 'deliver', 'som', 'dollar', 'date')
    list_filter = ('deliver',)
    date_hierarchy = 'date'


@admin.register(DeliverPayHistory)
class DeliverPayHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'deliver', 'som', 'dollar', 'date')
    search_fields = ('id', 'deliver', 'som', 'dollar', 'date')
    list_filter = ('deliver',)
    date_hierarchy = 'date'

@admin.register(Kassa)
class KassaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nomi', 'som', 'dollar', 'hisob_raqam', 'plastik')
    list_display_links = ('id', 'nomi', 'som', 'dollar')

@admin.register(ChiqimTuri)
class ChiqimTuriAdmin(admin.ModelAdmin):
    list_display = ('id', 'nomi')
    list_display_links = ('id', 'nomi')

@admin.register(Chiqim)
class ChiqimAdmin(admin.ModelAdmin):
    list_display_links = ('id', 'qayerga', 'qancha_som', 'qancha_dol', 'qachon')
    list_display = ('id', 'qayerga', 'qancha_som', 'qancha_dol', 'qachon')

@admin.register(HodimModel)
class HodimModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'ism', 'familya', 'oylik')
    list_display_links = ('id', 'ism', 'familya', 'oylik')

@admin.register(HodimQarz)
class HodimQarzAdmin(admin.ModelAdmin):
    list_display = ('id', 'hodim', 'qancha_som', 'qancha_dol', 'qaytargani_som', 'qaytargani_dol', 'izox', 'qachon', 'tolandi')
    list_display_links = ('id', 'hodim', 'qancha_som', 'qancha_dol', 'qachon')

@admin.register(OylikTolov)
class OylikTolovAdmin(admin.ModelAdmin):
    list_display_links = ('id', 'pul', 'sana')
    list_display = ('id', 'pul', 'sana')