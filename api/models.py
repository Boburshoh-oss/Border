from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields import DateField



class Filial(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    qarz_som = models.IntegerField(default=0)
    qarz_dol = models.IntegerField(default=0)
    savdo_puli_som = models.IntegerField(default=0)
    savdo_puli_dol = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '2) Filial'


class HodimModel(models.Model):
    ism = models.CharField(max_length=50)
    familya = models.CharField(max_length=50)
    filial = models.ForeignKey(Filial, on_delete=models.SET_NULL, null=True, blank=True)
    oylik = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = 'Hodimlar'

    def __str__(self) -> str:
        return self.ism + " " + self.familya

    def toliq_ism_ol(self):
        return self.ism + " " + self.familya

    
class HodimQarz(models.Model):
    hodim = models.ForeignKey(HodimModel, on_delete=models.CASCADE)
    qancha_som = models.PositiveIntegerField(default=0)
    qancha_dol = models.PositiveIntegerField(default=0)
    qaytargani_som = models.IntegerField(default=0)
    qaytargani_dol = models.IntegerField(default=0)
    izox = models.TextField(null=True, blank=True)
    qaytargandagi_izox = models.TextField(null=True, blank=True)
    tolandi = models.BooleanField(default=False)
    qachon = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.hodim.toliq_ism_ol()

    def qarzni_tekshir(self):
        
        if self.qancha_dol == self.qaytargani_dol and self.qancha_som == self.qaytargani_som:
            self.tolandi = True
            self.save()

        return 0

    class Meta:
        verbose_name_plural  = "Hodimlar qarzi"


class OylikTolov(models.Model):
    hodim = models.ForeignKey(HodimModel, on_delete=models.CASCADE)
    pul  = models.PositiveIntegerField(blank=False, null=False)
    sana = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.hodim.toliq_ism_ol()


class UserProfile(models.Model):
    staffs = [
        (1, 'director'),
        (2, 'manager'),
        (3, 'saler'),
        (4, 'warehouse')
    ]
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255, null=True, blank=True)
    staff = models.IntegerField(choices=staffs, default=3)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.first_name

    class Meta:
        verbose_name_plural = '1) User'


class Groups(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '3.1) Group'


class Deliver(models.Model):
    name = models.CharField(max_length=255)
    phone1 = models.CharField(max_length=13)
    phone2 = models.CharField(max_length=13, blank=True, null=True)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    difference = models.FloatField(default=0)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = '3.1) Deliver'


class DebtDeliver(models.Model):
    deliver = models.ForeignKey(Deliver, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)

    def __str__(self):
        return self.deliver.name

    class Meta:
        verbose_name_plural = 'Deliver Qarzi'


class DeliverPayHistory(models.Model):
    type_pay = (
        ("Naqd", "Naqd"),
        ("Plastik", "Plastik"),
        ("Pul o'tkazish", "Pul o'tkazish")
    )
    deliver = models.ForeignKey(Deliver, on_delete=models.CASCADE)
    som = models.FloatField()
    dollar = models.FloatField()
    turi = models.CharField(max_length=50, choices=type_pay, default="Naqd")
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.deliver.name

    class Meta:
        verbose_name_plural = 'Deliver Tolov Tarixi'


class ProductFilial(models.Model):
    measure = [
        ('dona', 'dona'),
        ('kg', 'kg'),
        ('litr', 'litr'),
        ('metr', 'metr')
    ]
    name = models.CharField(max_length=255)
    preparer = models.CharField(max_length=255, default="")
    som = models.FloatField(default=0)
    sotish_som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    sotish_dollar = models.FloatField(default=0)
    kurs = models.FloatField(default=0)
    barcode = models.CharField(max_length=255)
    group = models.ForeignKey(Groups, on_delete=models.CASCADE)
    measurement = models.CharField(choices=measure, default='dona', max_length=4)
    min_count = models.FloatField(default=0)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    quantity = models.FloatField(default=0)
    image = models.ImageField(upload_to="products/", null=True, blank=True)
    # def __str__(self):
    #     return self.name

    class Meta:
        verbose_name_plural = '3.1) Product Filial'


class Recieve(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    deliver = models.ForeignKey(Deliver, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    som = models.FloatField(default=0)
    sum_sotish_som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    sum_sotish_dollar = models.FloatField(default=0)
    status = models.IntegerField(default=0)
    farq_dollar = models.IntegerField(default=0)
    farq_som = models.IntegerField(default=0)
    

    # difference = models.IntegerField(default=0)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = '4) Recieve'


class RecieveItem(models.Model):
    recieve = models.ForeignKey(Recieve, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    som = models.FloatField(default=0)
    sotish_som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    sotish_dollar = models.FloatField(default=0)
    kurs = models.FloatField(default=0)
    quantity = models.FloatField(default=0)

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name_plural = '4.1) RecieveItem'


class Faktura(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    status = models.IntegerField(default=0)
    difference_som = models.IntegerField(default=0)
    difference_dollar = models.FloatField(default=0)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = '6) Faktura'


class FakturaItem(models.Model):
    name = models.CharField(max_length=255)
    faktura = models.ForeignKey(Faktura, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    group = models.ForeignKey(Groups, on_delete=models.CASCADE, blank=True, null=True)
    body_som = models.FloatField(default=0)
    body_dollar = models.FloatField(default=0)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    quantity = models.FloatField(default=0)
    barcode = models.CharField(max_length=255)

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name_plural = '6.1) FakturaItem'


class Course(models.Model):
    som = models.IntegerField()

    def __str__(self):
        return str(self.som)

    class Meta:
        verbose_name_plural = "Dollar kursi"


class Shop(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    naqd_som = models.FloatField(default=0)
    naqd_dollar = models.FloatField(default=0)
    plastik = models.FloatField(default=0)
    nasiya_som = models.FloatField(default=0)
    nasiya_dollar = models.FloatField(default=0)
    transfer = models.FloatField(default=0)
    skidka_dollar = models.FloatField(default=0)
    skidka_som = models.FloatField(default=0)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    saler = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True)

    # discount = models.SmallIntegerField(default=0, verbose_name="Chegirma (skidka) foizi")

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = '5) Shop'


class Cart(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    price = models.IntegerField()
    quantity = models.FloatField()
    total = models.FloatField(blank=True, null=True)

    # def save(self, *args, **kwargs):
    #     self.total = int(self.quantity) * self.product.price
    #     super().save(*args, **kwargs)

    def __str__(self):
        try:
            return self.product.product.name
        except:
            return 'Deleted Product'

    class Meta:
        verbose_name_plural = '5.1) Cart'


class Debtor(models.Model):
    fio = models.CharField(max_length=255)
    phone1 = models.CharField(max_length=13)
    phone2 = models.CharField(max_length=13, blank=True, null=True)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    difference = models.FloatField(default=0)

    def __str__(self):
        return self.fio

    class Meta:
        verbose_name_plural = '7) Nasiyachilar'


#
# class DebtHistory(models.Model):
#     debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE)
#     product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
#     price = models.IntegerField(default=0)
#     debt_quan = models.IntegerField(default=0)
#     pay_quan = models.IntegerField(default=0)
#     debt = models.IntegerField(default=0)
#     pay = models.IntegerField(default=0)
#     difference = models.IntegerField(default=0)
#
#     class Meta:
#         verbose_name_plural = '8) Nasiya Tarixi'


class Debt(models.Model):
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    status = models.IntegerField(default=0)
    return_date = models.DateField()

    def __str__(self):
        return self.debtor.fio

    class Meta:
        verbose_name_plural = 'Qarz Tarixi'


class PayHistory(models.Model):
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    som = models.FloatField()
    dollar = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.debtor.fio

    class Meta:
        verbose_name_plural = '9) Tolov Tarixi'


class CartDebt(models.Model):
    debtor = models.ForeignKey(Debtor, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    price = models.IntegerField(default=0)
    given_quan = models.FloatField(default=0)
    total = models.FloatField(default=0)
    return_quan = models.FloatField(default=0)
    return_sum = models.IntegerField(default=0)
    debt_quan = models.FloatField(default=0)
    debt_sum = models.FloatField(default=0)
    difference = models.FloatField(default=0)

    def __str__(self):
        return self.debtor.fio + " / " + self.product.product.name

    class Meta:
        verbose_name_plural = 'CartDebt'


class ReturnProduct(models.Model):
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    return_quan = models.FloatField(default=0)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    difference = models.FloatField(default=0)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    status = models.PositiveIntegerField(default=0)
    barcode = models.CharField(max_length=255)

    def __str__(self):
        return self.product.product.name

    class Meta:
        verbose_name_plural = 'Return Product'


class Pereotsenka(models.Model):
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = 'Pereotsenka'


class ChangePrice(models.Model):
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name_plural = 'ChangePrice'


class ChangePriceItem(models.Model):
    changeprice = models.ForeignKey(ChangePrice, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    old_som = models.FloatField(default=0)
    old_dollar = models.FloatField(default=0)
    new_som = models.FloatField(default=0)
    new_dollar = models.FloatField(default=0)
    quantity = models.FloatField(default=0)

    def __str__(self):
        return self.product.product.name

    class Meta:
        verbose_name_plural = 'ChangePriceIten'


class ReturnProductToDeliver(models.Model):
    deliver = models.ForeignKey(Deliver, on_delete=models.CASCADE)
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    kurs = models.IntegerField(null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.deliver.name

    class Meta:
        verbose_name_plural = 'Return Product To Deliver'


class ReturnProductToDeliverItem(models.Model):
    returnproduct = models.ForeignKey(ReturnProductToDeliver, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    som = models.FloatField(default=0)
    dollar = models.FloatField(default=0)
    quantity = models.FloatField(default=0)

    def __str__(self):
        return str(self.returnproduct.id)

    class Meta:
        verbose_name_plural = 'Return Product To Deliver Item'


class Kamomad(models.Model):
    filial = models.ForeignKey(Filial, on_delete=models.CASCADE)
    valyuta = models.CharField(max_length=25)
    difference_sum = models.FloatField(default=0)
    difference_dollar = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now=True)


class Exchange(models.Model):
    kurs = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now=True)


class Kassa(models.Model):
    nomi = models.CharField(max_length=50)
    som = models.IntegerField(default=0)
    dollar = models.IntegerField(default=0)
    plastik = models.IntegerField(default=0)
    hisob_raqam = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.nomi


class ChiqimTuri(models.Model):
    nomi = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.nomi


class Chiqim(models.Model):
    qayerga = models.ForeignKey(ChiqimTuri, on_delete=models.CASCADE)
    qancha_som  = models.IntegerField(default=0)
    qancha_dol = models.IntegerField(default=0)
    qancha_hisob_raqamdan = models.IntegerField(default=0)
    izox = models.TextField()
    qachon  = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.qayerga.nomi + " " + str(self.qachon)


class MobilUser(models.Model):
    phone = models.CharField(max_length=25, unique=True)
    password = models.CharField(max_length=25)
    username = models.CharField(max_length=200,null=True)
    is_authenticated = models.BooleanField(default=False)

    def __str__(self):
        return self.phone

    class Meta:
        verbose_name_plural = 'Mobile Users'

import binascii
import os
from django.utils.translation import ugettext_lazy as _

class MyOwnToken(models.Model):
    """
    The default authorization token model.
    """
    key = models.CharField(_("Key"), max_length=40, primary_key=True)

    user = models.OneToOneField(
        MobilUser, related_name='auth_token',
        on_delete=models.CASCADE, verbose_name="Company"
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)

    class Meta:
        verbose_name = _("Mobile Token")
        verbose_name_plural = _("Mobile Tokens")


    def save(self, *args, **kwargs):
        if not self.key:
            self.key = generate_key()
        return super(MyOwnToken, self).save(*args, **kwargs)

    def __str__(self):
        return self.key

def generate_key():
    return binascii.hexlify(os.urandom(20)).decode()


class MCart(models.Model):
    user = models.ForeignKey(MobilUser, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductFilial, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()
    status = models.CharField(choices=(
        ('1', 'Maxsulot Savatchada'),
        ('2', 'Sotib olingan')
    ), max_length=255, default=1)
    total = models.IntegerField()

    class Meta:
        verbose_name_plural = 'Mobile Cart'

class Telegramid(models.Model):
    name = models.CharField(max_length=255)
    telegram_id = models.IntegerField()

class Banner(models.Model):
    image = models.ImageField(upload_to="banner/")

    class Meta:
        verbose_name_plural = "Mobile Banner"

class MOrder(models.Model):
    user = models.ForeignKey(MobilUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(MCart)
    date = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField(default=0)

    class Meta:
        verbose_name_plural = "Mobile order"



