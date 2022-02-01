from django.db.models.fields.related import create_many_to_many_intermediary_model
from rest_framework import viewsets
from .serializers import *
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import datetime
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
import tablib
from django.db.models import Q, Sum
from rest_framework.pagination import PageNumberPagination
import json
from django.conf import settings
from main.sms_sender import sendSmsOneContact



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


def month():
    date = datetime.today()
    year = date.year
    if date.month == 12:
        gte = datetime(year, date.month, 1, 0, 0, 0)
        lte = datetime(year + 1, 1, 1, 0, 0, 0)
    else:
        gte = datetime(year, date.month, 1, 0, 0, 0)
        lte = datetime(year, date.month + 1, 1, 0, 0, 0)

    return gte, lte


class TokenViewset(viewsets.ModelViewSet):
    queryset = Token.objects.all()
    serializer_class = TokenSerializer


class UserProfileViewset(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    @action(methods=['post'], detail=False)
    def login1(self, request):
        r = request.data
        password = r['password']
        try:
            user = UserProfile.objects.get(password=password)
            s = self.get_serializer_class()(user).data
            # token, created = Token.objects.first()
            token, created = Token.objects.get_or_create(user=user)
            print(token)
            return Response({
                'user': s,
                'token': token.key
            })
        except:
            return Response({'message': 'Bunday foydalanuvchi yo`q'}, status=401)

    @action(methods=['post'], detail=False)
    def login(self, request):
        r = request.data
        password = r['password']
        try:
            user = UserProfile.objects.get(password=password)
            s = self.get_serializer_class()(user).data
            token = Token.objects.first()
            return Response({
                'user': s,
                'token': token.key
            })
        except:
            return Response({'message': 'Bunday foydalanuvchi yo`q'}, status=401)

    @action(methods=['get'], detail=False)
    def hodim(self, request):
        emp = UserProfile.objects.filter(staff__gt=1)
        data = []
        for e in emp:
            if e.staff == 2:
                st = 'manager'
            elif e.staff == 3:
                st = 'saler'
            else:
                st = 'warehaouse'
            t = {
                'first_name': e.first_name,
                'last_name': e.last_name,
                'phone': e.phone,
                'staff': st,
                'filial': e.filial.name,
            }
            data.append(t)

        return Response(data)

    @action(methods=['get'], detail=False)
    def by_filial(self, request):
        f = request.GET.get('f')
        emp = UserProfile.objects.filter(staff__gt=1, filial_id=f)
        data = []
        for e in emp:
            if e.staff == 2:
                st = 'manager'
            elif e.staff == 3:
                st = 'saler'
            else:
                st = 'warehaouse'
            t = {
                'id': e.id,
                'first_name': e.first_name,
                'last_name': e.last_name,
                'phone': e.phone,
                'staff': st,
                'filial': e.filial.name,
            }
            data.append(t)

        return Response(data)


class FilialViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Filial.objects.all()
    serializer_class = FilialSerializer

    @action(methods=['post'], detail=False)
    def change_kurs(self, request):
        new_kurs = float(request.data['kurs'])
        exchange = Exchange.objects.first()
        exchange.kurs = new_kurs
        exchange.save()
        return Response({'message': "kurs o'zgartirildi"}, status=200)

    @action(methods=['get'], detail=False)
    def get_kurs(self, request):
        exchange = Exchange.objects.first()
        return Response({'message': exchange}, status=200)


class GroupsViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Groups.objects.all()
    serializer_class = GroupsSerializer


class DeliverViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Deliver.objects.all()
    serializer_class = DeliverSerializer


"""
class ProductViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all().order_by('name')
    serializer_class = ProductSerializer
    search_fields = ['name', ]

    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(methods=['post'], detail=False)
    def add(self, request):
        r = request.data
        recieve = r['recieve']
        re = Recieve.objects.get(id=recieve)

        recieves = RecieveItem.objects.filter(recieve=re)
        for r in recieves:
            product = Product.objects.filter(barcode=r.product.barcode)
            try:
                p = Product.objects.get(name=r.product.name, preparer=r.product.preparer, som=r.som, dollar=r.dollar,
                                        kurs=r.kurs)
                p.quantity += r.quantity
                p.save()
            except:
                Product.objects.create(name=r.product.name, group=r.product.group, preparer=r.product.preparer,
                                       quantity=r.quantity, barcode=r.product.barcode, som=r.som, dollar=r.dollar,
                                       kurs=r.kurs)
            # for p in product:
            #     if p.quantity == 0 and r.product.barcode:
            #         p.delete()
        re.status = 1
        re.deliver.som -= re.som
        re.deliver.dollar -= re.dollar
        re.deliver.save()
        re.save()
        DebtDeliver.objects.create(deliver=re.deliver, som=-re.som, dollar=-re.dollar)

        return Response({'message': 'done'}, status=200)

    @action(methods=['post'], detail=False)
    def add_without_debt(self, request):
        r = request.data
        recieve = r['recieve']
        re = Recieve.objects.get(id=recieve)

        recieves = RecieveItem.objects.filter(recieve=re)
        for r in recieves:
            try:
                p = Product.objects.get(name=r.product.name, preparer=r.product.preparer, som=r.som, dollar=r.dollar,
                                        kurs=r.kurs)
                p.quantity += r.quantity
                p.save()
            except:
                Product.objects.create(name=r.product.name, group=r.product.group, preparer=r.product.preparer,
                                       quantity=r.quantity, barcode=r.product.barcode, som=r.som, dollar=r.dollar,
                                       kurs=r.kurs)
        re.status = 1
        re.deliver.som -= re.som
        re.deliver.dollar -= re.dollar
        re.deliver.save()
        re.save()
        return Response({'message': 'done'}, status=200)

    @action(methods=['post'], detail=False)
    def xlsx(self, request):
        file = request.FILES['file']

        data = tablib.Dataset().load(file, format='xlsx')
        for d in data:
            p = Product.objects.filter(barcode=d[7]).first()
            if p:
                pass
            else:
                if d[2]:
                    Product.objects.create(
                        name=d[0],
                        group_id=d[6],
                        dollar=d[2],
                        kurs=10500,
                        quantity=d[1],
                        barcode=d[7]
                    )
                elif d[3]:
                    Product.objects.create(
                        name=d[0],
                        group_id=d[6],
                        som=d[3],
                        kurs=10500,
                        quantity=d[1],
                        barcode=d[7]
                    )

        return Response({'message': 'done'})

    @action(methods=['post'], detail=False)
    def product_add_from_xlsx(self, request):
        file = request.FILES['file']

        data = tablib.Dataset().load(file, format='xlsx')
        for d in data:
            print(d[1])
            print(d[3])
            Product.objects.create(
                name=d[1],
                group_id=d[3]
            )
        return Response({'message': 'done'})

"""


class Product_FilialViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Filial.objects.all()
    serializer_class = ProductFilialSerializer

    @action(methods=['get'], detail=False)
    def filial_products(self, request):
        filial_id = request.GET['filial_id']
        products = ProductFilial.objects.filter(filial_id=filial_id)
        data = self.get_serializer_class()(products, many=True)
        return Response(data.data, status=200)


class ProductFilialViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ProductFilial.objects.all()
    serializer_class = ProductFilialSerializer
    pagination_class = StandardResultsSetPagination

    def create(self, request):
        data = request.data
        try:
            group = Groups.objects.get(id=int(data["group"]))
            filial = Filial.objects.get(id=int(data["filial_id"]))
            product = ProductFilial(
                name=data["name"],
                preparer=data["preparer"],
                som=float(data["som"]),
                sotish_som=float(data["sotish_som"]),
                dollar=float(data["dollar"]),
                sotish_dollar=float(data["sotish_dollar"]),
                kurs=float(data["kurs"]),
                barcode=data["barcode"],
                group=group,
                measurement=data["measurement"],
                min_count=int(data["min_count"]),
                filial=filial
            )
            product.save()
            serialized_product = ProductFilialSerializer(product, many=False)
            return Response(serialized_product.data, status=201)
        except Exception as e:
            return Response({"message": "error {}".format(str(e))}, status=400)

    @action(methods=['post'], detail=False)
    def add_recive(self, request):
        r = request.data
        recieve = r['recieve']
        filial_id = r['filial_id']
        farq_som = r['farq_som']
        farq_dollar = r['farq_dollar']

        re = Recieve.objects.get(id=recieve)
        re.farq_som = farq_som
        re.farq_dollar = farq_dollar
        re.save()

        recieves = RecieveItem.objects.filter(recieve=re)

        for r in recieves:
            try:
                p = ProductFilial.objects.get(
                    barcode=r.product.barcode
                )
                p.quantity += r.quantity
                p.som = r.som
                p.sotish_som = r.sotish_som
                p.dollar = r.dollar
                p.sotish_dollar = r.sotish_dollar
                p.save()
            except:
                ProductFilial.objects.create(
                    name=r.product.name,
                    group=r.product.group,
                    preparer=r.product.preparer,
                    quantity=r.quantity,
                    barcode=r.product.barcode,
                    som=r.som,
                    sotish_som=r.sotish_som,
                    dollar=r.dollar,
                    sotish_dollar=r.sotish_dollar,
                    kurs=r.kurs,
                    filial_id=filial_id
                )

        re.status = 2
        re.deliver.som -= re.som
        re.deliver.dollar -= re.dollar
        re.deliver.save()
        re.save()
        DebtDeliver.objects.create(deliver=re.deliver, som=-re.som, dollar=-re.dollar)

        return Response({'message': 'done'}, status=200)

    @action(methods=['get'], detail=False)
    def by_filial(self, request):
        id = request.GET.get('f')
        d = ProductFilial.objects.filter(filial_id=id)

        page = self.paginate_queryset(d)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(d, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=False)
    def add(self, request):
        r = request.data
        filial = int(r['filial'])
        faktura = int(r['faktura'])
        # difference = float(r['difference'])
        fakturaitems = FakturaItem.objects.filter(faktura_id=faktura)
        faktura_jonatilgan_filial = Filial.objects.get(id=filial)

        dif_som = 0
        dif_dollar = 0

        for fakturaitem in fakturaitems:
            product = ProductFilial.objects.filter(filial=filial, id=fakturaitem.product.id)

            if len(product) > 0:
                product = product.first()

                if product.som != fakturaitem.som:
                    dif_som += (fakturaitem.som - product.som) * product.quantity
                    product.som = fakturaitem.som
                    product.quantity = product.quantity + fakturaitem.quantity
                    product.save()

                elif product.dollar != fakturaitem.dollar:
                    dif_dollar += (fakturaitem.dollar - product.dollar) * product.quantity
                    product.dollar = fakturaitem.dollar
                    product.quantity = product.quantity + fakturaitem.quantity
                    product.save()

                else:
                    product.quantity = product.quantity + fakturaitem.quantity
                    product.save()
            else:
                ProductFilial.objects.create(som=fakturaitem.som,
                                             dollar=fakturaitem.dollar,
                                             quantity=fakturaitem.quantity, filial_id=filial,
                                             barcode=fakturaitem.barcode, group=fakturaitem.group)

        faktur = Faktura.objects.get(id=faktura)
        faktur.difference_som = dif_som
        faktur.difference_dollar = dif_dollar
        faktur.status = 2
        faktur.save()
        print(faktur)
        faktura_jonatilgan_filial.qarz_som += faktur.som
        faktura_jonatilgan_filial.qarz_dol += faktur.dollar
        faktura_jonatilgan_filial.save()
        print(faktura_jonatilgan_filial.qarz_som)

        return Response({'message': 'done'}, status=200)

    @action(methods=['post'], detail=False)
    def add_without_debt(self, request):
        r = request.data
        filial = int(r['filial'])
        faktura = int(r['faktura'])
        # difference = float(r['difference'])
        fakturaitems = FakturaItem.objects.filter(faktura_id=faktura)
        dif_som = 0
        dif_dollar = 0
        for fakturaitem in fakturaitems:
            product = ProductFilial.objects.filter(filial=filial, product=fakturaitem.product)
            if len(product) > 0:
                product = product.first()
                if product.som != fakturaitem.som:
                    dif_som += (fakturaitem.som - product.som) * product.quantity
                    product.som = fakturaitem.som
                    product.quantity = product.quantity + fakturaitem.quantity
                    product.save()
                elif product.dollar != fakturaitem.dollar:
                    dif_dollar += (fakturaitem.dollar - product.dollar) * product.quantity
                    product.dollar = fakturaitem.dollar
                    product.quantity = product.quantity + fakturaitem.quantity
                    product.save()
                else:
                    product.quantity = product.quantity + fakturaitem.quantity
                    product.save()
            else:
                ProductFilial.objects.create(product=fakturaitem.product, som=fakturaitem.som,
                                             dollar=fakturaitem.dollar,
                                             quantity=fakturaitem.quantity, filial_id=filial,
                                             barcode=fakturaitem.barcode)
        faktur = Faktura.objects.get(id=faktura)
        faktur.difference_som = dif_som
        faktur.difference_dollar = dif_dollar
        faktur.status = 2
        faktur.save()

        return Response({'message': 'done'}, status=200)

    @action(methods=['get'], detail=False)
    def search(self, request):
        f = request.GET.get('f')
        q = request.GET.get('q')
        query_filtered = ProductFilial.objects.all()
        if f:
            query_filtered = query_filtered.filter(filial_id=f)
        if q:
            query_filtered.filter(Q(name__icontains=q) | Q(barcode=q))
        # query = ProductFilial.objects.filter(Q(filial_id=f) & Q(product__name__icontains=q) | Q(product__barcode=q))
        d = ProductFilialSerializerWithCourse(query_filtered, many=True).data

        return Response(d)

        """
            @action(methods=['post'], detail=False)
            def xlsx(self, request):
                file = request.FILES['file']

                data = tablib.Dataset().load(file, format='xlsx')
                for d in data:
                    p = Product.objects.get(barcode=d[7])
                    pro = ProductFilial.objects.filter(barcode=d[7])
                    if len(pro) == 0:
                        ProductFilial.objects.create(
                            product=p,
                            som=d[5],
                            dollar=d[6],
                            quantity=d[1],
                            filial_id=1,
                            barcode=p.barcode
                        )
                    else:
                        pass

                return Response({'message': 'done'})
        """

    @action(methods=['post'], detail=False)
    def up(self, request):
        if request.method == "POST":
            bar = request.data['barcode']
            filial = request.data['filial']
            som = float(request.data['som'])
            dollar = float(request.data['dollar'])
            p = ProductFilial.objects.filter(barcode=bar, filial_id=filial)
            for i in p:
                print(i.som, som)
                if i.som == som:
                    if i.dollar == dollar:
                        print('11')
                        pass
                    else:
                        dollar1 = (dollar - i.dollar) * i.quantity
                        Pereotsenka.objects.create(filial=i.filial, dollar=dollar1)
                        i.dollar = dollar
                        i.save()
                        print('222')
                else:
                    if i.dollar == dollar:
                        som1 = (som - i.som) * i.quantity
                        Pereotsenka.objects.create(filial=i.filial, som=som1)
                        i.som = som
                        i.save()
                        print('333')
                    else:
                        som1 = (som - i.som) * i.quantity
                        dollar1 = (dollar - i.dollar) * i.quantity
                        Pereotsenka.objects.create(filial=i.filial, som=som1, dollar=dollar1)
                        i.som = som
                        i.dollar = dollar
                        i.save()
        return Response({'message': 'done'}, status=200)


class RecieveViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Recieve.objects.all()
    serializer_class = RecieveSerializer

    @action(methods=['post'], detail=False)
    def new(self, request):
        filial_id = request.POST['filial_id']
        name = request.POST['name']
        deliver_id = request.POST['deliver_id']

        created = Recieve.objects.create(filial_id=filial_id, name=name, deliver_id=deliver_id)

        recieve = self.get_serializer_class()(created)

        return Response(recieve.data, status=201)

    @action(methods=['get'], detail=False)
    def get_status_1(self, request):
        recieve = Recieve.objects.filter(status=1)

        data = self.get_serializer_class()(recieve, many=True)

        return Response(data.data, status=200)

    @action(methods=['get'], detail=False)
    def recieve0(self, request):
        recieve = Recieve.objects.filter(status=0)

        s = self.get_serializer_class()(recieve, many=True)
        return Response(s.data, status=200)

    @action(methods=['get'], detail=False)
    def recieve1(self, request):
        id = request.GET.get('id')
        r = Recieve.objects.get(id=id)
        r.status = 1
        r.save()

        return Response({'message': 'done'}, status=200)


class RecieveItemViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = RecieveItem.objects.all()
    serializer_class = RecieveItemSerializer

    @action(methods=['post'], detail=False)
    def add(self, request):
        r = request.data
        recieve = int(r['recieve'])
        product = int(r['product'])
        som = float(r['som'])
        sotish_som = float(r['sotish_som'])
        dollar = float(r['dollar'])
        sotish_dollar = float(r['sotish_dollar'])
        kurs = float(r['kurs'])
        quantity = float(r['quantity'])
        rec = Recieve.objects.get(id=recieve)
        try:
            r = RecieveItem.objects.create(
                recieve=rec,
                product_id=product,
                som=som,
                sotish_som=sotish_som,
                dollar=dollar,
                sotish_dollar=sotish_dollar,
                kurs=kurs,
                quantity=quantity
            )
            if som == 0:
                rec.dollar += dollar * quantity
                rec.sum_sotish_dollar += sotish_dollar * quantity
                rec.save()
            else:
                rec.som += som * quantity
                rec.sum_sotish_som += sotish_som * quantity
                rec.save()

            s = self.get_serializer_class()(r)
            return Response(s.data, status=201)
        except:
            return Response({'message': 'error'}, status=401)

    @action(methods=['get'], detail=False)
    def rv1(self, request):
        rec = request.GET.get('rec')
        revieve = RecieveItem.objects.filter(recieve_id=rec)

        s = self.get_serializer_class()(revieve, many=True)
        return Response(s.data, status=200)

    @action(methods=['post'], detail=False)
    def up(self, request):
        r = request.data
        item = int(r['item'])
        dollar = float(r['dollar'])
        kurs = float(r['kurs'])
        som = float(r['som'])
        sotish_som = float(r['sotish_som'])
        sotish_dollar = float(r['sotish_dollar'])
        quantity = 0

        try:
            quantity = float(r['quantity'])
        except:
            pass

        it = RecieveItem.objects.get(id=item)
        recieve = it.recieve
        if som == 0:
            recieve.dollar = recieve.dollar - (it.dollar * it.quantity) + dollar * quantity
            it.dollar = dollar
            it.kurs = kurs
            try:
                it.quantity = quantity
            except:
                pass
            it.sotish_dollar = sotish_dollar
            recieve.sum_sotish_dollar = recieve.sum_sotish_dollar - (
                        it.sotish_dollar * it.quantity) + sotish_dollar * quantity
            recieve.save()
            it.save()

        elif dollar == 0:
            recieve.som = recieve.som - (it.som * it.quantity) + som * quantity
            it.som = som
            it.quantity = quantity
            try:
                it.quantity = quantity
            except:
                pass
            it.sotish_som = sotish_som
            recieve.sum_sotish_som = recieve.sum_sotish_som - (it.sotish_som * it.quantity) + sotish_som * quantity
            recieve.save()
            it.save()

        s = self.get_serializer_class()(it)
        return Response(s.data, status=200)

    @action(methods=['post'], detail=False)
    def delete(self, request):
        r = request.data
        item = int(r['item'])
        it = RecieveItem.objects.get(id=item)
        recieve = it.recieve

        if it.som == 0:
            recieve.dollar = recieve.dollar - (it.dollar * it.quantity)
            recieve.sum_sotish_dollar = recieve.sum_sotish_dollar - (it.sotish_dollar * it.quantity)
            recieve.save()
        elif it.dollar == 0:
            recieve.som = recieve.som - (it.som * it.quantity)
            recieve.sum_sotish_dollar = recieve.sum_sotish_som - (it.sotish_som * it.quantity)
            recieve.save()
        it.delete()
        return Response({'message': 'done'})


class FakturaViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Faktura.objects.all()
    serializer_class = FakturaSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Faktura.objects.all()
        status = self.request.query_params.get("status")

        if status:
            queryset = queryset.filter(status=int(status))

        return queryset

    @action(methods=['post'], detail=False)
    def st(self, request):
        r = request.data
        faktura = int(r['faktura'])
        try:
            f = Faktura.objects.get(id=faktura)
            f.status = 1
            f.save()
            return Response({'message': 'status o`zgardi'}, status=200)
        except:
            return Response({'message': 'error'}, status=400)

    @action(methods=['get'], detail=False)
    def st1(self, request):
        fil = request.GET.get('fil')
        faktura = Faktura.objects.filter(filial_id=fil, status=1)

        s = self.get_serializer_class()(faktura, many=True)
        return Response(s.data, status=200)

    @action(methods=['get'], detail=False)
    def st2(self, request):
        fil = request.GET.get('fil')
        faktura = Faktura.objects.filter(filial_id=fil, status=2)

        st = []
        for f in faktura:
            t = {
                'id': f.id,
                'date': f.date.strftime('%Y-%m-%d %H:%M:%S'),
                'som': f.som,
                'dollar': f.dollar,
                'filial': f.filial.id,
                'status': f.status,
                'difference_som': f.difference_som,
                'message': "Qabul qilingan",
            }
            st.append(t)
        page = self.paginate_queryset(st)
        if page is not None:
            return self.get_paginated_response(st)

        return Response(st, status=200)

    @action(methods=['get'], detail=False)
    def ombor1(self, request):
        faktura = Faktura.objects.filter(status=1)

        s = self.get_serializer_class()(faktura, many=True)
        return Response(s.data, status=200)

    @action(methods=['get'], detail=False)
    def ombor0(self, request):
        faktura = Faktura.objects.filter(status=0)

        s = self.get_serializer_class()(faktura, many=True)
        return Response(s.data, status=200)

    @action(methods=['get'], detail=False)
    def otkaz(self, request):
        fak = request.GET.get('fak')
        faktura = Faktura.objects.get(id=fak)
        items = FakturaItem.objects.filter(faktura_id=fak)
        try:
            for i in items:
                prod = ProductFilial.objects.get(id=i.product.id)
                prod.quantity += i.quantity
                prod.save()
            faktura.status = 3
            faktura.save()
            return Response({'message': 'done'}, status=200)
        except:
            return Response({'message': 'error'}, status=400)

    @action(methods=['get'], detail=False)
    def monthly(self, request):
        gte, lte = month()
        faks = Faktura.objects.filter(date__gte=gte, date__lte=lte)

        d = self.get_serializer_class()(faks, many=True)

        return Response(d.data, status=200)

    @action(methods=['get'], detail=False)
    def by_filial(self, request):
        gte, lte = month()
        f = request.GET.get('f')
        faks = Faktura.objects.filter(date__gte=gte, date__lte=lte, filial_id=f, status=2)

        d = self.get_serializer_class()(faks, many=True)

        return Response(d.data, status=200)

    @action(methods=['post'], detail=False)
    def range(self, request):
        gte = request.data['sana1']
        lte = request.data['sana2']

        faks = Faktura.objects.filter(date__gte=gte, date__lte=lte)

        d = self.get_serializer_class()(faks, many=True)

        return Response(d.data, status=200)

    @action(methods=['post'], detail=False)
    def range_by_filial(self, request):
        gte = request.data['sana1']
        lte = request.data['sana2']
        f = request.data['f']
        faks = Faktura.objects.filter(date__gte=gte, date__lte=lte, filial_id=f, status=2)

        d = self.get_serializer_class()(faks, many=True)

        return Response(d.data, status=200)


class FakturaItemViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = FakturaItem.objects.all()
    serializer_class = FakturaItemSerializer

    @action(methods=['get'], detail=False)
    def by_faktura(self, request):
        id = request.GET.get('faktura')
        item = FakturaItem.objects.filter(faktura_id=id)
        d = FakturaItemReadSerializer(item, many=True)

        return Response(d.data, status=200)

    @action(methods=['post'], detail=False)
    def add(self, request):
        r = request.data
        name = r['name']
        barcode = r['barcode']
        faktura = int(r['faktura'])
        product = int(r['product'])
        som = float(r['som'])
        dollar = float(r['dollar'])
        body_som = float(r['body_som'])
        body_dollar = float(r['body_dollar'])
        group = int(r['group'])
        quantity = float(r['quantity'])
        try:
            prod = ProductFilial.objects.get(id=product)
            fak = Faktura.objects.get(id=faktura)
            f = FakturaItem.objects.create(faktura_id=faktura, name=name, barcode=barcode, product_id=product,
                                           som=som, dollar=dollar, body_som=body_som, body_dollar=body_dollar,
                                           quantity=quantity, group_id=group)
            if som > 0:
                fak.som += som * quantity
            elif dollar > 0:
                fak.dollar += dollar * quantity
            fak.save()
            prod.quantity -= quantity
            prod.save()
            s = self.get_serializer_class()(f)
            return Response(s.data, status=201)
        except:
            return Response({'message': 'error'}, status=401)

    @action(methods=['get'], detail=False)
    def st1(self, request):
        fak = request.GET.get('fak')
        faktura = FakturaItem.objects.filter(faktura_id=fak)

        s = self.get_serializer_class()(faktura, many=True)
        return Response(s.data, status=200)

    @action(methods=['post'], detail=False)
    def add_kamomad(self, request):
        product_list = request.data.get('item')
        filial_pk = request.data.get('filial')
        filial = Filial.objects.filter(pk=filial_pk).first()
        summa_som = 0
        summa_dollar = 0
        for product in product_list:
            barcode = str(product.get('barcode'))
            quantity = float(product.get('quantity'))
            product_filial = ProductFilial.objects.filter(filial=filial, barcode=barcode).first()
            if not product_filial:
                continue
            summa_som += (quantity - product_filial.quantity) * product_filial.som
            print(quantity, product_filial.quantity, product_filial.som)
            summa_dollar += (quantity - product_filial.quantity) * product_filial.dollar
            product_filial.quantity = quantity
            product_filial.save()
        Kamomad.objects.create(filial=filial, difference_sum=summa_som, difference_dollar=summa_dollar,
                               valyuta='uzb')
        return Response({'message': 'done'})

    @action(methods=['get'], detail=False)
    def get_kamomad(self, request, **kwargs):
        filial = request.query_params.get('filial')
        kamomad = Kamomad.objects.filter(filial_id=filial)
        result = KamomadModalSerializer(instance=kamomad, many=True)
        return Response({"data": result.data})

    @action(methods=['post'], detail=False)
    def up(self, request):
        r = request.data
        item = int(r['item'])
        dollar = float(request.data.get('dollar', None))
        som = float(request.data.get('som', None))
        quantity = float(request.data.get('quantity', None))
        fakturaitem = FakturaItem.objects.get(id=item)
        product = fakturaitem.product
        # product.quantity = product.quantity - fakturaitem.quantity + quantity
        product.quantity = product.quantity - quantity + fakturaitem.quantity
        product.save()
        faktura = fakturaitem.faktura
        if som:
            faktura.som = faktura.som - (fakturaitem.som * fakturaitem.quantity) + som * quantity
            fakturaitem.som = som
        if dollar:
            faktura.dollar = faktura.dollar - (fakturaitem.dollar * fakturaitem.quantity) + dollar * quantity
            fakturaitem.dollar = dollar
        if quantity:
            fakturaitem.quantity = quantity
        fakturaitem.save()
        faktura.save()

        # if dollar:
        #     fak.dollar = dollar
        # if som:
        # faktura 4500
        # faktureitem 900som 5 ta
        #
        #     fak.som = som
        # quantity = float(r['quantity'])
        # if quantity:
        #     fak.quantity = quantity
        #     fak.save()
        # try:     faktura
        #     price = int(r['price'])
        #     faktura = fak.faktura
        #     faktura.som = faktura.som - (fak.price * fak.quantity) + fak.quantity * price
        #     fak.price = price
        #     fak.save()
        #     faktura.save()
        # except:
        #     pass
        # try:
        #     quantity = float(r['quantity'])
        #     faktura = fak.faktura
        #     faktura.som = faktura.som - (fak.price * fak.quantity) + fak.price * quantity
        #     fak.quantity = quantity
        #     fak.save()
        #     faktura.save()
        # except:
        #     pass

        s = self.get_serializer_class()(fakturaitem)
        return Response(s.data, status=200)

    @action(methods=['post'], detail=False)
    def delete(self, request):
        r = request.data
        item = int(r['item'])
        fakturaitem = FakturaItem.objects.get(id=item)
        faktura = fakturaitem.faktura

        faktura.som = faktura.som - fakturaitem.som * fakturaitem.quantity
        faktura.dollar = faktura.dollar - fakturaitem.dollar * fakturaitem.quantity
        product = fakturaitem.product
        product.quantity = product.quantity + fakturaitem.quantity
        product.save()
        faktura.save()
        fakturaitem.delete()

        return Response({'message': 'done'})



# smm replace
def sms_text_replace(sms_text, nasiya_som, customer):
    try:
        format_nasiya_som = '{:,}'.format(int(nasiya_som))
        sms_texts = str(sms_text).format(name=customer.fio, som=format_nasiya_som,  kun = customer.debt_return)
    except Exception as e:
        print(e)
    return sms_texts


# 998997707572 len = 12
def checkPhone(phone):
    try:
        int(phone)
        return (True, phone) if len(phone) >= 12 else (False, None)
    except:
        return False, None


#sms sender  if buy  
def schedular_sms_send_oldi(nasiya_som, id):
    try:
        text = settings.GET_DEBTOR_SMS
        debtor = Debtor.objects.get(id=id)
        sms_text = sms_text_replace(text, nasiya_som, debtor)
        can, phone = checkPhone(debtor.phone1)
        if can:
            result = sendSmsOneContact(debtor.phone1, sms_text)
            print(result)
    except Exception as e:
        print(e)


class ShopViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer

    @action(methods=['post'], detail=False)
    def add(self, request):
        if request.method == 'POST':
            r = request.data
            naqd_som = r["naqd_som"]
            naqd_dollar = r["naqd_dollar"]
            plastik = r["plastik"]
            transfer = r["transfer"]
            skidka_som = r["skidka_som"]
            skidka_dollar = r["skidka_dollar"]
            filial = r["filial"]
            saler = r["saler"]
            cart = r["cart"]
            # new
            debt_return = r.get("debt_return", None)

            filial_obj = Filial.objects.get(id=filial)

            if naqd_som:
                filial_obj.savdo_puli_som += naqd_som - skidka_som

            if plastik:
                print("plastik")
                filial_obj.savdo_puli_som += plastik

            if transfer:
                print("transfer")
                filial_obj.savdo_puli_som += transfer

            if naqd_dollar:
                print("naqd_dol")
                filial_obj.savdo_puli_dol += naqd_dollar - skidka_dollar

            filial_obj.save()

            for c in cart:

                product = ProductFilial.objects.get(barcode=c['barcode'])

                if product.quantity > 0 and c['quantity'] <= product.quantity:
                    product.quantity -= c['quantity']
                    product.save()
                else:
                    product.quantity = 0
                    product.save()

            try:
                nasiya_som = r["nasiya_som"]
                nasiya_dollar = r["nasiya_dollar"]
                fio = request.data['fio']
                sh = Shop.objects.create(
                    naqd_som=naqd_som,
                    naqd_dollar=naqd_dollar,
                    nasiya_som=nasiya_som,
                    nasiya_dollar=nasiya_dollar,
                    plastik=plastik,
                    transfer=transfer,
                    skidka_som=skidka_som,
                    skidka_dollar=skidka_dollar,
                    filial_id=filial,
                    saler_id=saler,
                    # new
                    debt_return=debt_return
                )
                phone = r["phone"]

                d, created = Debtor.objects.get_or_create(fio=fio, phone1=phone)
                d.som += float(nasiya_som)
                d.dollar += float(nasiya_dollar)
                # new sms
                d.debt_return = debt_return
                d.save()
                #new sms
                schedular_sms_send_oldi(nasiya_som, d.id)
                return Response({'message': 'Shop qo`shildi. Debtor yangilandi'}, status=201)

            except Exception as er:
                sh = Shop.objects.create(
                    naqd_som=naqd_som,
                    naqd_dollar=naqd_dollar,
                    plastik=plastik,
                    transfer=transfer,
                    skidka_som=skidka_som,
                    skidka_dollar=skidka_dollar,
                    filial_id=filial,
                    saler_id=saler,
                    # new
                    debt_return=debt_return
                )

                return Response({'message': 'Shop qo`shildi. {}'.format(er)}, status=201)

    @action(methods=['post'], detail=False)
    def by_date(self, request):

        r = request.data
        date1 = r['date1']
        date2 = r['date2']
        f = r['filial']

        sh = Shop.objects.filter(date__gte=date1, date__lt=date2, filial_id=f)
        data = self.get_serializer_class()(sh, many=True).data

        return Response(data)

    @action(methods=['get'], detail=False)
    def by_hodim(self, request):
        id = request.GET.get('id')
        today = datetime.today()
        sana1 = datetime(today.year, today.month, today.day)
        sh = Shop.objects.filter(date__gte=sana1, saler_id=id)
        t = sh.aggregate(jami=Sum('summa'), n=Sum('naqd'), p=Sum('plastik'), t=Sum('transfer'), c=Sum('currency'),
                         nas=Sum('nasiya'))
        j = {
            'jami': t['jami'],
            'naqd': t['n'],
            'plastik': t['p'],
            'transfer': t['t'],
            'nasiya': t['nas'],
            'valyuta': t['c']
        }
        return Response(j)

    @action(methods=['post'], detail=False)
    def by_date_and_hodim(self, request):
        r = request.data
        date1 = r['date1']
        date2 = r['date2']
        id = r['id']
        t = Shop.objects.filter(date__gte=date1, date__lt=date2, saler_id=id).aggregate(jami=Sum('summa'),
                                                                                        n=Sum('naqd'), p=Sum('plastik'),
                                                                                        t=Sum('transfer'),
                                                                                        c=Sum('currency'),
                                                                                        nas=Sum('nasiya'))
        j = {
            'jami': t['jami'],
            'naqd': t['n'],
            'plastik': t['p'],
            'transfer': t['t'],
            'nasiya': t['nas'],
            'valyuta': t['c']
        }
        return Response(j)


class CartViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    @action(methods=['post'], detail=False)
    def add(self, request):
        r = request.data
        summa = r['summa']
        naqd = r['naqd']
        plastik = r['plastik']
        nasiya = r['nasiya']
        transfer = r['transfer']
        currency = r['currency']
        skidka_dollar = r['skidka_dollar']
        skidka_som = r['skidka_som']
        filial = r['filial']
        saler = r['saler']
        items = r['items']

        sh = Shop.objects.create(summa=summa, naqd_som=naqd, plastik=plastik, nasiya=nasiya, transfer=transfer,
                                 filial_id=filial, saler_id=saler, currency=currency, skidka_dollar=skidka_dollar,
                                 skidka_som=skidka_som)
        for i in items:
            pr = ProductFilial.objects.get(id=i['product'])
            Cart.objects.create(shop=sh, product_id=i['product'], quantity=i['quantity'], price=pr.price,
                                total=pr.price * i['quantity'])
        try:
            debtor = r['debtor']
            dollar = r['dollar']
            debt_return = r.get("debt_return", None)
            d = Debtor.objects.get(id=debtor)
            d.debts += nasiya
            d.debts_dollar += dollar
            # new sms
            d.debt_return = debt_return
            d.save()
            Debt.objects.create(debtorr_id=debtor, shop=sh, return_date=r['return_date'], dollar=dollar)
        except:
            pass
        return Response({'message': 'done'})

    @action(methods=['post'], detail=False)
    def mobil_add(self, request):
        if request.method == 'POST':
            r = request.data.get
            naqd_som = r('naqd_som')
            naqd_dollar = r('naqd_dollar')
            plastik = r('plastik')
            transfer = r('transfer')
            skidka_som = r('skidka_som')
            skidka_dollar = r('skidka_dollar')
            filial = r('filial')
            saler = r('saler')

            try:
                nasiya_som = r('nasiya_som')
                nasiya_dollar = r('nasiya_dollar')
                debtor = request.data['debtor']
                debt_return = r.get("debt_return", None)
                sh = Shop.objects.create(naqd_som=naqd_som, naqd_dollar=naqd_dollar, nasiya_som=nasiya_som,
                                         nasiya_dollar=nasiya_dollar, plastik=plastik, transfer=transfer,
                                         skidka_som=skidka_som, skidka_dollar=skidka_dollar, filial_id=filial,
                                         saler_id=saler)
                d = Debtor.objects.get(id=debtor)
                d.som += float(nasiya_som)
                d.dollar += float(nasiya_dollar)
                # new sms
                d.debt_return = debt_return
                d.save()

                return Response({'message': 'Shop qo`shildi. Debtor yangilandi'}, status=201)
            except Exception as e:
                sh = Shop.objects.create(naqd_som=naqd_som, naqd_dollar=naqd_dollar, plastik=plastik, transfer=transfer,
                                         skidka_som=skidka_som, skidka_dollar=skidka_dollar, filial_id=filial,
                                         saler_id=saler)

                return Response({'message': 'Shop qo`shildi.'}, status=201)


class DebtorViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Debtor.objects.all()
    serializer_class = DebtorSerializer

    @action(methods=['post'], detail=False)
    def up(self, request):
        if request.method == 'POST':
            r = request.data
            try:
                fio = r['fio']
                phone1 = r['phone1']
                debts = float(r['debts'])
                debts_dollar = float(r['debts_dollar'])
                difference = float(r['difference'])
                debt_return = r.get("debt_return", None)
                d = Debtor.objects.get(fio=fio, phone1=phone1)
                d.debts = debts
                d.debts_dollar = debts_dollar
                d.difference = difference
                # new sms
                d.debt_return = debt_return
                d.save()
                return Response({'message': 'Debtor update bo`ldi.'}, status=200)
            except:
                return Response({'message': 'data not found'}, status=400)
        else:
            return Response({'message': 'error'}, status=400)


class DebtViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer

    @action(methods=['get'], detail=False)
    def by_debtor(self, request):
        id = request.GET.get('d')
        data = Debt.objects.filter(status=0, debtor_id=id)
        d = self.get_serializer_class()(data, many=True)
        return Response(d.data)



def sms_text_replaces(sms_text,sum, customer):
    try:
        format_tuladi_som = '{:,}'.format(int(sum))
        format_qoldiq_som = '{:,}'.format(int(customer.som))
        sms_texts = str(sms_text).format(name = customer.fio, som=format_tuladi_som, qoldi = format_qoldiq_som )
    except Exception as e:
        print(e)
    return sms_texts



#sms sender   if qarz tulasa  
def schedular_sms_send_qaytardi(id,som):
    try:
        debtor = Debtor.objects.get(id=id)
        text = settings.RETURN_DEBTOR_SMS
        sms_text = sms_text_replaces(text, som, debtor)
        
        can, phone = checkPhone(debtor.phone1)
        if can:
            result = sendSmsOneContact(debtor.phone1, sms_text)
            print(result)
    except Exception as e:
        print(e)


class PayHistoryViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = PayHistory.objects.all()
    serializer_class = PayHistorySerializer

    @action(methods=['post'], detail=False)
    def add(self, request):
        if request.method == 'POST':
            r = request.data
            try:
                fio = r['fio']
                phone1 = r['phone1']
                som = float(r['som'])
                dollar = float(r['dollar'])
                filial = int(r['filial'])
                debt_return = r.get("debt_return", None)
                d = Debtor.objects.get(fio=fio, phone1=phone1)
                try:
                    PayHistory.objects.create(debtor=d, som=som, dollar=dollar, filial_id=filial)
                    d.som = d.som - som
                    d.dollar = d.dollar - dollar
                    # new sms
                    d.debt_return = debt_return
                    d.save()
                    # new
                    schedular_sms_send_qaytardi(d.id, som)
                    return Response({'message': 'To`lov qabul qilindi.'}, 200)
                except:
                    return Response({'message': 'error'}, 401)
            except:
                return Response({'message': 'data not found'}, status=400)
        else:
            return Response({'message': 'error'}, 401)

    @action(methods=['post'], detail=False)
    def pay(self, request):
        r = request.data
        p = PayHistory.objects.create(debtor_id=r['debtor'], filial_id=r['filial'], sum=r['summa'], dollar=r['dollar'])
        d = Debtor.objects.get(id=r['debtor'])
        d.debts -= r['summa']
        d.debts_dollar -= r['dollar']
        d.save()
        # new
        # schedular_sms_send_qaytardi(fio, som, d.id, d.som)
        s = self.get_serializer_class()(p).data
        return Response(s)

    @action(methods=['post'], detail=False)
    def pay_from_mobil(self, request):
        r = request.data
        debt_id = r['debt']
        debt = Debt.objects.get(id=debt_id)
        return_sum = float(r['return_sum'])
        return_dollar = float(r['return_dollar'])
        p = PayHistory.objects.create(debtor=debt.debtor, filial=debt.shop.filial, sum=return_sum)
        d = Debtor.objects.get(id=debt.debtor.id)
        d.debts -= return_sum
        d.debts_dollar -= return_dollar
        d.save()

        debt.return_sum = return_sum
        if debt.shop.nasiya == debt.return_sum:
            debt.status = 1
        debt.save()
        s = self.get_serializer_class()(p).data
        return Response(s)


class CartDebtViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = CartDebt.objects.all()
    serializer_class = CartDebtSerializer

class ReturnProductViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ReturnProduct.objects.all()
    serializer_class = ReturnProductSerializer

    @action(methods=['post'], detail=False)
    def add(self, request):
        if request.method == 'POST':
            r = request.data
            try:
                return_quan = float(r['return_quan'])
                som = float(r['som'])
                dollar = float(r['dollar'])
                filial = r['filial']
                difference = float(r['difference'])
                status = int(r['status'])
                barcode = r['barcode']
                try:
                    prod = ProductFilial.objects.filter(filial_id=filial, barcode=barcode).first()
                    ReturnProduct.objects.create(product=prod, filial_id=filial,
                                                 return_quan=return_quan, som=som, dollar=dollar,
                                                 difference=difference,
                                                 status=status, barcode=barcode)

                    prod = ProductFilial.objects.filter(filial_id=filial, barcode=barcode).first()

                    prod.quantity += return_quan
                    prod.save()
                    if status == 1:
                        fio = r['fio']
                        phone1 = r['phone1']
                        d = Debtor.objects.get(fio=fio, phone1=phone1)
                        d.som = d.som - som
                        d.dollar = d.dollar - dollar
                        d.save()
                    return Response({'message': 'done'}, 200)
                except Exception as e:
                    print(e)
                    return Response({'message': 'create qilishda xatolik'}, 401)
            except Exception as e:
                print(e)
                return Response({'message': 'data not found'}, 401)
        else:
            return Response({'message': 'error'}, 401)

    @action(methods=['post'], detail=False)
    def ad(self, request):
        r = request.data
        product = int(r['product'])
        quantity = float(r['quantity'])
        summa = float(r['summa'])

        prod = ProductFilial.objects.get(id=product)
        r = ReturnProduct.objects.create(product_id=product, return_quan=quantity, summa=summa,
                                         difference=quantity * (summa - prod.price), filial=prod.filial,
                                         barcode=prod.barcode)
        d = self.get_serializer_class()(r).data

        return Response(d)


class ChangePriceViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ChangePrice.objects.all()
    serializer_class = ChangePriceSerializer


class ChangePriceItemViewset(viewsets.ModelViewSet):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ChangePriceItem.objects.all()
    serializer_class = ChangePriceItemSerializer

    @action(methods=['post'], detail=False)
    def add(self, request):
        r = request.data
        filial = r['filial']
        items = r['items']

        ch = ChangePrice.objects.create(filial_id=filial)

        for i in items:
            prod = ProductFilial.objects.filter(barcode=i['barcode']).first()
            ChangePriceItem.objects.create(
                changeprice=ch,
                product=prod,
                old_som=prod.som,
                old_dollar=prod.dollar,
                new_som=i['som'],
                new_dollar=i['dollar'],
                quantity=prod.quantity
            )
            prod.sotish_som = i['som']
            prod.sotish_dollar = i['dollar']
            prod.save()

        chitems = ChangePriceItem.objects.filter(changeprice=ch)
        dt = ChangePriceItemSerializer(chitems, many=True).data
        return Response(dt)


class ReturnProductToDeliverViewset(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = ReturnProductToDeliver.objects.all()
    serializer_class = ReturnProductToDeliverSerializer


class ReturnProductToDeliverItemViewset(viewsets.ModelViewSet):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]
    queryset = ReturnProductToDeliverItem.objects.all()
    serializer_class = ReturnProductToDeliverItemSerializer

    @action(methods=['post'], detail=False)
    def add(self, request):
        r = request.data
        deliver = r['deliver']
        filial = r['filial']
        som = r['som']
        dollar = r['dollar']
        kurs = r.get('dollar')
        items = r['items']
        ret = ReturnProductToDeliver.objects.create(deliver_id=deliver, som=som, dollar=dollar, filial_id=filial,
                                                    kurs=kurs)
        for i in items:
            prod = ProductFilial.objects.get(barcode=i['barcode'], filial_id=filial)
            ReturnProductToDeliverItem.objects.create(returnproduct=ret, product=prod, som=i['som'], dollar=i['dollar'],
                                                      quantity=i['quantity'])
            prod.quantity -= i['quantity']
            prod.save()
        data = ReturnProductToDeliverItem.objects.filter(returnproduct=ret)
        dt = self.get_serializer_class()(data, many=True).data
        return Response(dt)

    @action(methods=['post'], detail=False)
    def add_mobil(self, request):
        r = request.data
        deliver = r['deliver']
        filial = r['filial']
        som = r['som']
        dollar = r['dollar']
        items = r['items']
        ret = ReturnProductToDeliver.objects.create(deliver_id=deliver, som=som, dollar=dollar, filial_id=filial)
        for i in items:
            prod = ProductFilial.objects.get(id=i['product'])
            ReturnProductToDeliverItem.objects.create(returnproduct=ret, product=prod, som=i['som'], dollar=i['dollar'],
                                                      quantity=i['quantity'])
            prod.quantity -= i['quantity']
            prod.save()
        data = ReturnProductToDeliverItem.objects.filter(returnproduct=ret)
        deli = Deliver.objects.get(id=deliver)
        deli.som -= som
        deli.dollar -= dollar
        deli.save()

        dt = self.get_serializer_class()(data, many=True).data
        return Response(dt)
