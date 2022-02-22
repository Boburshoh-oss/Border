import requests
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from .models import MobilUser, Telegramid, MyOwnToken,MOrder, MCart, ProductFilial, Banner
from rest_framework import viewsets
from .authentication import MyOwnTokenAuthentication
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .serializers import MCartSerializer, MOrderSerializer, ProductFilialSerializer, BannerSerializer

from decimal import Decimal


@api_view(['POST'])
def login(request):
    phone = request.data['phone']
    password = request.data['password']

    try:
        cl = MobilUser.objects.get(phone=phone)
        if password == cl.password:
            status = 200
            try:
                myT = MyOwnToken.objects.get(user_id=cl.id)
            except MyOwnToken.DoesNotExist:
                myT = MyOwnToken.objects.create(user_id=cl.id)

            data = {
                'status': status,
                'user': cl.id,
                'token': myT.key,
                "username": cl.username,
            }
        else:
            status = 403
            massage = "Telefon raqam yoki parol xato!"
            data = {
                'status': status,
                'massage': massage,
            }
    except MobilUser.DoesNotExist:
        status=404
        massage = "Bunday foydalanuvchi mavjud emas!"
        data = {
            'status': status,
            'massage': massage,
        }

    return Response(data)


@api_view(['POST'])
def register(request):
    phone = request.data['phone']
    password = request.data['password']
    username = request.data['username']
    cl = MobilUser.objects.filter(phone=phone).count()
    if cl > 0:
        status = 203
        massage = "Bunday foydalanuvchi mavjud!"
        token = None
        client_id = None
    else:
        cc = MobilUser.objects.create(phone=phone, password=password, username=username)
        tt = MyOwnToken.objects.create(user_id=cc.id)
        massage = "Success"
        status = 200,
        token = tt.key
        client_id = cc.id
    data = {
        'status': status,
        'massage': massage,
        'token': token,
        'user': client_id,
    }
    return Response(data)


class MCartViewset(viewsets.ModelViewSet):
    queryset = MCart.objects.all()
    serializer_class = MCartSerializer
    authentication_classes = (MyOwnTokenAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    @action(methods=['post'], detail=False)
    def post(self, request):
        user = request.user
        product = request.data.get('product')
        quantity = request.data.get('quantity')

        pr = ProductFilial.objects.get(id=product)
        if MCart.objects.filter(user=user, product=pr, status=1).count() > 0:
            return Response({"message": "Bunday maxsulot savatchada bor!"})
        else:
            if pr.sotish_som > 0:
                total = pr.sotish_som * int(quantity)
                MCart.objects.create(user=user, product=pr, quantity=quantity, price=pr.sotish_som,
                                     status=1, total=total)
            else:
                total = pr.sotish_dollar * int(quantity)
                MCart.objects.create(user=user, product=pr, quantity=quantity, price=pr.sotish_dollar,
                                     status=1, total=total)
            return Response({"message": "Muvofaqiyatli qo'shildi"})


    @action(methods=['get'], detail=False)
    def get(self, request):
        user = request.user
        cart = MCart.objects.filter(user=user, status=1)
        data = []
        for i in cart:
            if i.product.image:
                dt = {
                    'id': i.id,
                    'product': i.product.name,
                    'quantity': int(i.quantity),
                    'price': i.price,
                    'total': i.total,
                    'image': i.product.image.url,
                }
            else:
                dt = {
                    'id': i.id,
                    'product': i.product.name,
                    'quantity': int(i.quantity),
                    'price': i.price,
                    'total': i.total,
                    'image': 'Maxsulot rasmi yoq',
                }
            data.append(dt)
        return Response(data)


    @action(methods=['post'], detail=False)
    def buy(self, request):
        user = request.user
        cart = MCart.objects.filter(user=user, status=1)
        if cart.count() > 0:
            products = []
            total = 0
            mo = MOrder.objects.create(user=user)
            for i in cart:
                cart = MCart.objects.get(id=i.id)
                cart.status = '2'
                cart.save()
                dt = {
                    'maxsulot nomi': cart.product.name,
                    'narxi': cart.price,
                    'miqdori': cart.quantity,
                }

                mo.products.add(cart)
                mo.total += cart.price * cart.quantity
                mo.save()
                total += cart.price * cart.quantity
                products.append(dt)

            text = 'Buyurtma: \n' + '\nKlient: ' + mo.user.username + '\nKlient nomeri: ' + str(mo.user.phone) + '\nMaxsulotlar: ' + str(products) + '\njami: ' + str(total)
            url = 'https://api.telegram.org/bot1976769891:AAGY44HVas_e2NqdsuJjPx7kjpL1h9W7gsQ/sendMessage?chat_id='
            cat_ids = Telegramid.objects.all()
            chat = []
            for id in cat_ids:
                chat.append(id.telegram_id)

            for i in chat:
                requests.get(url + str(i) + '&text=' + text)

            data = {
                'status': 200,
                'message': "Muvofaqiyatli sotib olindi!"
            }
            return Response(data)
        else:
            return Response({"message": "Savatchada maxsulot yoq"})

class ProductFilialViewset(viewsets.ModelViewSet):
    queryset = ProductFilial.objects.all()
    serializer_class = ProductFilialSerializer
    authentication_classes = (MyOwnTokenAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)


    @action(methods=['get'], detail=False)
    def get(self, request):
        product = ProductFilial.objects.all().order_by('-id')
        data = []
        for i in product:
            if i.image:
                dt = {
                    'id': i.id,
                    'name': i.name,
                    'preparer': i.preparer,
                    'som': int(i.som),
                    'sotish_som': int(i.sotish_som),
                    'dollar': int(i.dollar),
                    'sotish_dollar': int(i.sotish_dollar),
                    'group': i.group.name,
                    'measurement': i.measurement,
                    'min_count': int(i.min_count),
                    'filial': i.filial.name,
                    'quantity': int(i.quantity),
                    'image': i.image.url,
                }
                data.append(dt)
            else:
                dt = {
                    'id': i.id,
                    'name': i.name,
                    'preparer': i.preparer,
                    'som': int(i.som),
                    'sotish_som': int(i.sotish_som),
                    'dollar': int(i.dollar),
                    'sotish_dollar': int(i.sotish_dollar),
                    'group': i.group.name,
                    'measurement': i.measurement,
                    'min_count': int(i.min_count),
                    'filial': i.filial.name,
                    'quantity': int(i.quantity),
                    'image': 'Maxsulot rasmi yoq',
                }
                data.append(dt)
        return Response(data)

    @action(methods=['get'], detail=False)
    def search(self, request):
        pr = request.GET.get('product')
        product = ProductFilial.objects.filter(name__icontains=pr)

        data = []
        for i in product:
            if i.image:
                dt = {
                    'id': i.id,
                    'name': i.name,
                    'preparer': i.preparer,
                    'som': int(i.som),
                    'sotish_som': int(i.sotish_som),
                    'dollar': int(i.dollar),
                    'sotish_dollar': int(i.sotish_dollar),
                    'group': i.group.name,
                    'measurement': i.measurement,
                    'min_count': int(i.min_count),
                    'filial': i.filial.name,
                    'quantity': int(i.quantity),
                    'image': i.image.url,
                }
                data.append(dt)
            else:
                dt = {
                    'id': i.id,
                    'name': i.name,
                    'preparer': i.preparer,
                    'som': int(i.som),
                    'sotish_som': int(i.sotish_som),
                    'dollar': int(i.dollar),
                    'sotish_dollar': int(i.sotish_dollar),
                    'group': i.group.name,
                    'measurement': i.measurement,
                    'min_count': int(i.min_count),
                    'filial': i.filial.name,
                    'quantity': int(i.quantity),
                    'image': 'Maxsulot rasmi yoq',
                }
                data.append(dt)

        return Response(data)




class BannerViewset(viewsets.ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    authentication_classes = (MyOwnTokenAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)



class MOrderViewset(viewsets.ModelViewSet):
    queryset = MOrder.objects.all()
    serializer_class = MOrderSerializer
    authentication_classes = (MyOwnTokenAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        user = request.user
        queryset = self.queryset.filter(user=user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False)
    def get_products(self, request):
        order_id = request.GET['order_id']
        order = MOrder.objects.get(id=order_id)

        pr = order.products.all()
        data = []
        for i in pr:
            if i.product.image:
                dt = {
                    'product': i.product.name,
                    'quantity': int(i.quantity),
                    'image': i.product.image.url,
                    'price': i.price,
                }
            else:
                dt = {
                    'product': i.product.name,
                    'quantity': int(i.quantity),
                    'image': "Maxsulot rasmi yoq",
                    'price': i.price,
                }
            data.append(dt)

        return Response(data)
