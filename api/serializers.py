from rest_framework import serializers
from .models import *
from rest_framework.authtoken.models import Token


class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = '__all__'


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'

class MOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MOrder
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'password', 'first_name', 'last_name', 'staff', 'filial']


class FilialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filial
        fields = '__all__'


class GroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Groups
        fields = '__all__'


class DeliverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deliver
        fields = '__all__'


class ProductFilialSerializer(serializers.ModelSerializer):
    filial = FilialSerializer(read_only =True)
    class Meta:
        model = ProductFilial
        fields = '__all__'


class ProductFilialSerializerWithCourse(serializers.ModelSerializer):

    class Meta:
        model = ProductFilial
        fields = '__all__'


class RecieveSerializer(serializers.ModelSerializer):
    filial = FilialSerializer(many=False, read_only=True)

    class Meta:
        model = Recieve
        fields = ["id", "filial", "name", "date", "som", "sum_sotish_som", "dollar", "sum_sotish_dollar", "status", "deliver"]


class RecieveItemSerializer(serializers.ModelSerializer):
    product = ProductFilialSerializer(read_only=True, many=False)

    class Meta:
        model = RecieveItem
        fields = ["id", "recieve", "product", "som", "sotish_som", "dollar", "sotish_dollar", "kurs", "quantity"]


class FakturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Faktura
        fields = '__all__'


class FakturaItemSerializer(serializers.ModelSerializer):
    product = ProductFilialSerializer(read_only=True)

    class Meta:
        model = FakturaItem
        fields = '__all__'


class FakturaItemReadSerializer(serializers.ModelSerializer):
    product = ProductFilialSerializer(read_only=True)

    class Meta:
        model = FakturaItem
        fields = '__all__'


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class DebtorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Debtor
        fields = '__all__'


# class DebtHistorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = DebtHistory
#         fields = '__all__'


class DebtSerializer(serializers.ModelSerializer):
    debtor = DebtorSerializer(read_only=True)
    shop = ShopSerializer(read_only=True)

    class Meta:
        model = Debt
        fields = '__all__'


class PayHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PayHistory
        fields = '__all__'


class CartDebtSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartDebt
        fields = '__all__'


class ReturnProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnProduct
        fields = '__all__'


class ChangePriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangePrice
        fields = '__all__'


class ChangePriceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChangePriceItem
        fields = '__all__'


class ReturnProductToDeliverSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnProductToDeliver
        fields = '__all__'


class ReturnProductToDeliverItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReturnProductToDeliverItem
        fields = '__all__'


class KamomadModalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kamomad
        fields = '__all__'


class MCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = MCart
        fields = "__all__"