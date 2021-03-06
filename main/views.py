from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Sum
from django.views.generic import TemplateView
from api.models import *
from django.db.models import Q
from datetime import datetime
from django.http.response import HttpResponse, JsonResponse
import json
from django.contrib.auth.mixins import LoginRequiredMixin
#SMS
from django.conf import settings
from .sms_sender import sendSmsOneContact

def monthly():
    date = datetime.now()
    year = date.year
    
    if date.month == 12:
        gte = datetime(year, date.month, 1, 0, 0, 0)
        lte = datetime(year + 1, 1, 1, 0, 0, 0)
    else:
        gte = datetime(year, date.month, 1, 0, 0, 0) #2022-03-01 00:00:00
        lte = datetime(year, date.month + 1, 1, 0, 0, 0) #2022-04-01 00:00:00

    return gte, lte

def daily_data():
    # lte = datetime.now() 2022-03-10 11:31:17.107452  
    # gte = lte - timedelta(days=1) 2022-03-11 11:31:17.107452
    date = datetime.now()
    year = date.year
    if date.month == 12:
        gte = datetime(year, date.month, 1, 0, 0, 0)
        lte = datetime(year + 1, 1, 1, 0, 0, 0)
    else:
        gte = datetime(year, date.month, 1, 0, 0, 0)
        lte = datetime(year, date.month + 1, 1, 0, 0, 0)

    return gte, lte


def ChartHome(request):
    kirims = []
    kirimd = []
    chiqims = []
    chiqimd = []
    yalpi = []
    filial_sum = []
    for i in range(1, 13):
        date = datetime.now().date()
        year = date.year
        if i == 12:
            month2 = 1
            year2 = year + 1
        else:
            month2 = i + 1
            year2 = year
        gte = f'{str(year)}-{str(i)}-01 00:01:00'
        lte = f'{str(year2)}-{str(month2)}-01 00:01:00'
        # kirr = Shop.objects.filter(date__gte=gte, date__lte=lte).aggregate(kir = Sum('naqd')+Sum('plastik')+Sum('nasiya'))
        kirr = Shop.objects.filter(date__gte=gte, date__lte=lte)
        ks = 0
        kd = 0
        filial_count = 0
        for kir in kirr:
            ks += kir.naqd_som + kir.plastik + kir.nasiya_som + kir.transfer + kir.skidka_som
            filial_count += kir.naqd_som + kir.plastik + kir.nasiya_som + kir.transfer 
            kd += kir.naqd_dollar + kir.nasiya_dollar + kir.skidka_dollar
        chs = 0
        chd = 0
        chiqq = Recieve.objects.filter(date__gte=gte, date__lte=lte)
        yalpi_mahsulot = Yalpi_savdo.objects.filter(date__gte=gte, date__lte=lte)
        yalpi_sum = 0
        for item in yalpi_mahsulot:
            yalpi_sum += item.total_sum
        # print(yalpi_sum,"yalpi mahsulot keldi")
        for chiq in chiqq:
            chs += chiq.som
            chd += chiq.dollar
        kirims.append(ks)
        kirimd.append(kd)

        chiqims.append(chs)
        chiqimd.append(chd)
        yalpi.append(yalpi_sum)
        filial_sum.append(filial_count)
    dt = {
        'kirims': kirims,
        'kirimd': kirimd,
        'chiqims': chiqims,
        'chiqimd': chiqimd,
        'yalpi':yalpi,
        'filial_sum':filial_sum
    }
    return JsonResponse(dt)


def FilialKirim(request):
    fil1 = []
    fil2 = []
    fil3 = []
    fil4 = []
    fil5 = []
    for i in range(1, 13):
        date = datetime.now()
        year = date.year
        if i == 12:
            month2 = 1
            year2 = year + 1
        else:
            month2 = i + 1
            year2 = year
        gte = f'{str(year)}-{str(i)}-01 00:01:00'
        lte = f'{str(year2)}-{str(month2)}-01 00:01:00'
        # lte = datetime.now()
        # gte = lte - timedelta(days=1)
        a = Shop.objects.filter(date__gte=gte, date__lte=lte).values('filial').annotate(
            som=Sum('naqd_som') + Sum('plastik') + Sum('nasiya_som') + Sum('transfer') + Sum('skidka_som'),
            dollar=Sum('naqd_dollar') + Sum('nasiya_dollar') + Sum('skidka_dollar'))
        try:
            fil1.extend((a[0]['som'], a[0]['dollar']))
        except:
            fil1.append('0')
        try:
            fil2.extend((a[1]['som'], a[1]['dollar']))
        except:
            fil2.append('0')
        try:
            fil3.extend((a[2]['som'], a[2]['dollar']))
        except:
            fil3.append('0')
        try:
            fil4.extend((a[3]['som'], a[3]['dollar']))
        except:
            fil4.append('0')
        try:
            fil5.extend((a[4]['som'], a[4]['dollar']))
        except:
            fil5.append('0')

    print(fil1, fil2, fil3)
    dt = {
        # 'data': data,
        'filial1': fil1,
        'filial2': fil2,
        'filial3': fil3,
        'filial4': fil4,
        'filial5': fil5,
    }
    return JsonResponse(dt)


def SalerKirim(request):
    saler1 = []
    saler2 = []
    saler3 = []
    for i in range(1, 13):
        date = datetime.now()
        year = date.year
        if i == 12:
            month2 = 1
            year2 = year + 1
        else:
            month2 = i + 1
            year2 = year
        gte = f'{str(year)}-{str(i)}-01 00:01:00'
        lte = f'{str(year2)}-{str(month2)}-01 00:01:00'
        a = Shop.objects.filter(date__gte=gte, date__lte=lte).values('saler').annotate(
            som=Sum('naqd_som') + Sum('plastik') + Sum('nasiya_som') + Sum('transfer') + Sum('skidka_som'),
            dollar=Sum('naqd_dollar') + Sum('nasiya_dollar') + Sum('skidka_dollar'))
        # try:
        #     saler1.append(a[0]['num'])
        # except:
        #     saler1.append('0')
        # try:
        #     saler2.append(a[1]['num'])
        # except:
        #     saler2.append('0')
        # try:
        #     saler3.append(a[2]['num'])
        # except:
        #     saler3.append('0')
        print(a)
    # print(fil1, fil2, fil3)
    dt = {
        'saler1': saler1,
        'saler2': saler2,
        'saler3': saler3,
    }
    return JsonResponse(dt)


def Summa(request):
    gte, lte = monthly()
    shops = Shop.objects.filter(date__gte=gte, date__lte=lte)
    naqd_som = 0
    naqd_dollar = 0
    plastik = 0
    nasiya_som = 0
    nasiya_dollar = 0
    transfer = 0
    skidka_som = 0
    skidka_dollar = 0
    for shop in shops:
        naqd_som += shop.naqd_som
        naqd_dollar += shop.naqd_dollar
        plastik += shop.plastik
        nasiya_som += shop.nasiya_som
        nasiya_dollar += shop.nasiya_dollar
        transfer += shop.transfer
        skidka_som += shop.skidka_som
        skidka_dollar += shop.skidka_dollar
    som = naqd_som + plastik + nasiya_som + transfer + skidka_som
    dollar = naqd_dollar + plastik + nasiya_dollar + transfer + skidka_dollar

    dt = {
        'naqd_som': naqd_som,
        'naqd_dollar': naqd_dollar,
        'plastik': plastik,
        'nasiya_som': nasiya_som,
        'nasiya_dollar': nasiya_dollar,
        'transfer': transfer,
        'skidka_som': skidka_som,
        'skidka_dollar': skidka_dollar,
        'som': som,
        'dollar': dollar,
    }
    return JsonResponse(dt)


# def Qoldiq(request):
#     fil = Filial.objects.extra(
#         select = {
#             'som':'select sum(api_productfilial.som * api_productfilial.quantity) from api_productfilial where api_productfilial.filial_id = api_filial.id',
#             'dollar':'select sum(api_productfilial.dollar * api_productfilial.quantity) from api_productfilial where api_productfilial.filial_id = api_filial.id'
#         }
#     )
#     fils = []
#     for f in fil:
#         fils.append(f.name)
#     filq = []
#     nol = 0
#     for f in fil:
#         if f.som:
#             filq.append(f.som)
#             filq.append(f.dollar)
#         else:
#             filq.append(nol)
#             filq.append(nol)
#     dt = {
#         'qoldiq':filq,
#         'filial':fils
#     }
#     return JsonResponse(dt)

def DataHome(request):
    data = json.loads(request.body)
    gtes = data['date1']
    ltes = data['date2']
    gte = f'{gtes} 00:01:00'
    lte = f'{ltes} 00:01:00'
    salers = UserProfile.objects.extra(
        select={
            'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
        }
    )
    filials = Filial.objects.extra(
        select={
            'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                gte, lte),
            'pay_som': 'select sum(api_payhistory.som) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
                gte, lte),
            'pay_dollar': 'select sum(api_payhistory.dollar) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
                gte, lte),
            'yalpi_daromad': 'select sum(api_yalpi_savdo.total_sum) from api_yalpi_savdo where api_yalpi_savdo.filial_id = api_filial.id and api_yalpi_savdo.date > "{}" and api_yalpi_savdo.date < "{}"'.format(
                gte, lte),
        }
    )
    shops = Shop.objects.filter(date__gte=gte, date__lte=lte)
    naqd_som = 0
    naqd_dollar = 0
    plastik = 0
    nasiya_som = 0
    nasiya_dollar = 0
    transfer = 0
    skidka_som = 0
    skidka_dollar = 0
    for shop in shops:
        naqd_som += shop.naqd_som
        naqd_dollar += shop.naqd_dollar
        plastik += shop.plastik
        nasiya_som += shop.nasiya_som
        nasiya_dollar += shop.nasiya_dollar
        transfer += shop.transfer
        skidka_som += shop.skidka_som
        skidka_dollar += shop.skidka_dollar
    som = naqd_som + plastik + nasiya_som + transfer + skidka_som
    dollar = naqd_dollar + plastik + nasiya_dollar + transfer + skidka_dollar

    if som > 0:
        se = []
        for saler in salers:
            s = {
                'name': saler.first_name,
                'staff': saler.staff,
                'filial': saler.filial.name,
                'naqd_som': saler.naqd_som,
                'naqd_dollar': saler.naqd_dollar,
                'plastik': saler.plastik,
                'nasiya_som': saler.nasiya_som,
                'nasiya_dollar': saler.nasiya_dollar,
                'transfer': saler.transfer,
                'skidka_som': saler.skidka_som,
                'skidka_dollar': saler.skidka_dollar,

            }
            se.append(s)
        fl = []
        for filial in filials:
            t = {
                'name': filial.name,
                'naqd_som': filial.naqd_som,
                'naqd_dollar': filial.naqd_dollar,
                'plastik': filial.plastik,
                'nasiya_som': filial.nasiya_som,
                'nasiya_dollar': filial.nasiya_dollar,
                'transfer': filial.transfer,
                'skidka_som': filial.skidka_som,
                'skidka_dollar': filial.skidka_dollar,
                'yalpi_daromad': filial.yalpi_daromad,
            }
            fl.append(t)
        # print(fl,"fl")
        dt1 = {
            'salers': se,
            'filials': fl,
            'naqd_som': naqd_som,
            'naqd_dollar': naqd_dollar,
            'plastik': plastik,
            'nasiya_som': nasiya_som,
            'nasiya_dollar': nasiya_dollar,
            'transfer': transfer,
            'skidka_som': skidka_som,
            'skidka_dollar': skidka_dollar,
        }
    else:
        se = []
        for saler in salers:
            s = {
                'name': saler.first_name,
                'staff': saler.staff,
                'filial': saler.filial.name,
                'naqd_som': 0,
                'naqd_dollar': 0,
                'plastik': 0,
                'nasiya_som': 0,
                'nasiya_dollar': 0,
                'transfer': 0,
                'skidka_som': 0,
                'skidka_dollar': 0,
            }
            se.append(s)
        fl = []
        for filial in filials:
            t = {
                'name': filial.name,
                'naqd_som': 0,
                'naqd_dollar': 0,
                'plastik': 0,
                'nasiya_som': 0,
                'nasiya_dollar': 0,
                'transfer': 0,
                'skidka_som': 0,
                'skidka_dollar': 0,
            }
            fl.append(t)

        dt1 = {
            'salers': se,
            'filials': fl,
            'naqd_som': 0,
            'naqd_dollar': 0,
            'plastik': 0,
            'nasiya_som': 0,
            'nasiya_dollar': 0,
            'transfer': 0,
            'skidka_som': 0,
            'skidka_dollar': 0,
        }
    return JsonResponse(dt1)


def DataWare(request):
    data = json.loads(request.body)
    date1 = data['date1']
    date2 = data['date2']
    wares = Recieve.objects.filter(date__gte=date1, date__lte=date2)
    wr = []
    for w in wares:
        t = {
            'id': w.id,
            'deliver': w.deliver.name,
            'name': w.name,
            'som': w.som,
            'dollar': w.dollar,
            'date': w.date.strftime("%d-%m-%y %I:%M")

        }
        wr.append(t)
    dt1 = {
        'wares': wr
    }
    return JsonResponse(dt1)


def DebtorHistory(request):
    gte, lte = monthly()
    d_id = request.GET.get('d')
    pays = PayHistory.objects.filter(date__gte=gte, date__lte=lte, debtor_id=d_id)
    debts = Debt.objects.filter(date__gte=gte, date__lte=lte, debtor_id=d_id)
    psom = 0
    pdollar = 0
    dsom = 0
    ddollar = 0
    for p in pays:
        psom += p.som
        pdollar += p.dollar
    for d in debts:
        dsom += d.som
        ddollar += d.dollar

    context = {
        'psom': psom,
        'pdollar': pdollar,
        'dsom': dsom,
        'ddollar': ddollar,
        'pays': pays,
        'debts': debts,
        'd_id': d_id,
        'debtor': "active",
        'debtor_t': "true"
    }

    return render(request, 'debtorhistory.html', context)

def filialinfo(request, id):

    if request.method == 'POST':
        filial_kirim_dollar = request.POST.get('filial_kirim_dollar')
        filial_kirim_som = request.POST.get('filial_kirim_som')
        filial_id = request.POST.get('filial_id')
        kassa_var = Kassa.objects.first()

        filial = Filial.objects.get(id=filial_id)

        if filial.qarz_som:
            filial.qarz_som -= int(filial_kirim_som)
            filial.savdo_puli_som -= int(filial_kirim_som)
            kassa_var.som += int(filial_kirim_som)

        if filial.qarz_dol:    
            filial.qarz_dol -= int(filial_kirim_dollar)
            filial.savdo_puli_dol -= int(filial_kirim_dollar)
            kassa_var.dollar += int(filial_kirim_dollar)

        filial.save()
        kassa_var.save()

        return redirect(f'/filialinfo/{id}')

    filial = Filial.objects.get(id=id)
    products = ProductFilial.objects.all()
    qoldiq_som = 0
    qoldiq_dol = 0

    for product in products:

        qoldiq_som += product.quantity * product.som
        qoldiq_dol += product.quantity * product.dollar

    context = {
        'fil':filial,
        'qoldiq_som':qoldiq_som,
        'qoldiq_dol':qoldiq_dol,
        'filial': "active",
        'filial_t': "true"
    }

    return render(request, 'filialinfo.html', context)

def DeliverHistory(request):
    gte, lte = monthly()
    d_id = request.GET.get('d')
    pays = DeliverPayHistory.objects.filter(date__gte=gte, date__lte=lte, deliver_id=d_id)
    debts = DebtDeliver.objects.filter(date__gte=gte, date__lte=lte, deliver_id=d_id)
    psom = 0
    pdollar = 0
    dsom = 0
    ddollar = 0
    for p in pays:
        psom += p.som
        pdollar += p.dollar
    for d in debts:
        dsom += d.som
        ddollar += d.dollar

    context = {
        'psom': psom,
        'pdollar': pdollar,
        'dsom': dsom,
        'ddollar': ddollar,
        'pays': pays,
        'debts': debts,
        'd_id': d_id,
        'deliver': "active",
        'deliver_t': "true"
    }

    return render(request, 'deliverhistory.html', context)


def NasiyaTarix(request):
    data = json.loads(request.body)
    date1 = data['date1']
    date2 = data['date2']
    d_id = data['d_id']
    # print(date1, date2, d_id)
    pays = PayHistory.objects.filter(date__gte=date1, date__lte=date2, debtor_id=d_id)
    debts = Debt.objects.filter(date__gte=date1, date__lte=date2, debtor_id=d_id)
    psom = 0
    pdollar = 0
    dsom = 0
    ddollar = 0
    for p in pays:
        psom += p.som
        pdollar += p.dollar
    for d in debts:
        dsom += d.som
        ddollar += d.dollar
    pay = []
    for w in pays:
        print("p")
        t = {
            # 'id': w.id,
            'som': w.som,
            'dollar': w.dollar,
            'date': w.date.strftime("%d-%m-%y %I:%M"),
        }
        pay.append(t)
    debt = []
    for w in debts:
        print("d")
        t = {
            # 'id': w.id,
            'som': w.som,
            'dollar': w.dollar,
            'date': w.date,
        }
        debt.append(t)
    dt1 = {
        'psom': psom,
        'pdollar': pdollar,
        'dsom': dsom,
        'ddollar': ddollar,
        'pays': pay,
        'debts': debt,
    }
    return JsonResponse(dt1)


def kurs_page(request):
    if request.method == 'POST':
        kurs = request.POST.get('kurs')
        kurs_baza = 0
        try:
            kurs_baza = Exchange.objects.first()
            kurs = float(kurs)
            kurs_baza.kurs = kurs
            kurs_baza.save()
        except:
            pass
        return render(request, 'change_kurs_page.html', {'kurs': kurs_baza})
    else:
        kurs = Exchange.objects.first()
        return render(request, 'change_kurs_page.html', {'kurs': kurs})


def add_tolov(request):
    deliver_id = request.POST.get('deliver_id')
    som = request.POST.get('som')
    izoh = request.POST.get('izoh')
    dollor = request.POST.get('dollor')
    turi = request.POST.get('turi')
    ht = DeliverPayHistory.objects.create(deliver_id=deliver_id, som=som, dollar=dollor, turi=turi, izoh=izoh)
    
    url = "/deliverhistory/?d=" + str(deliver_id)
    return redirect(url)


def GetItem(request):
    data = json.loads(request.body)
    id = data['id']
    items = RecieveItem.objects.filter(recieve_id=id)
    it = []
    for i in items:
        its = {
            'id': i.id,
            'product': i.product.name,
            'som': i.som,
            'dollar': i.dollar,
            'kurs': i.kurs,
            'quantity': i.quantity
        }
        it.append(its)
    dt1 = {
        'items': it
    }
    return JsonResponse(dt1)


class Home(LoginRequiredMixin, TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        # gte, lte = monthly() 2022-03-01 00:00:00 2022-04-01 00:00:00
        lte = datetime.now() #2022-03-11 11:43:51.290605
        gte = lte - timedelta(days=1) #2022-03-10 11:43:51.290605 
        lte = lte.date()
        gte = gte.date()
        try:
            salers = UserProfile.objects.extra(
                select={
                    'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                        gte, lte),
                    'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                        gte, lte),
                    'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                        gte, lte),
                    'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                        gte, lte),
                    'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                        gte, lte),
                    'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                        gte, lte),
                    'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                        gte, lte),
                    'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                        gte, lte),
                    
                }
            )
            filials = Filial.objects.extra(
                select={
                    'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                        gte, lte),
                    'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                        gte, lte),
                    'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                        gte, lte),
                    'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                        gte, lte),
                    'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                        gte, lte),
                    'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                        gte, lte),
                    'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                        gte, lte),
                    'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                        gte, lte),
                    'pay_som': 'select sum(api_payhistory.som) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
                        gte, lte),
                    'pay_dollar': 'select sum(api_payhistory.dollar) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
                        gte, lte),
                    'yalpi_daromad': 'select sum(api_yalpi_savdo.total_sum) from api_yalpi_savdo where api_yalpi_savdo.filial_id = api_filial.id and api_yalpi_savdo.date > "{}" and api_yalpi_savdo.date < "{}"'.format(
                        gte, lte),
                }
            )
        except Exception as e:
            return HttpResponse(str(e),"nima bu")

        shops = Shop.objects.filter(date__gte=gte, date__lte=lte)
        naqd_som = 0
        naqd_dollar = 0
        plastik = 0
        nasiya_som = 0
        nasiya_dollar = 0
        transfer = 0
        skidka_som = 0
        skidka_dollar = 0
        for shop in shops:
            naqd_som += shop.naqd_som
            naqd_dollar += shop.naqd_dollar
            plastik += shop.plastik
            nasiya_som += shop.nasiya_som
            nasiya_dollar += shop.nasiya_dollar
            transfer += shop.transfer
            skidka_som += shop.skidka_som
            skidka_dollar += shop.skidka_dollar
        som = naqd_som + plastik + nasiya_som + transfer + skidka_som
        dollar = naqd_dollar + plastik + nasiya_dollar + transfer + skidka_dollar

        jami = 0
        try:
            for f in filials:
                
                if f.naqd_som is None:
                    f.naqd_som = 0
                if f.plastik is None:
                    f.plastik = 0
                if f.nasiya_som is None:
                    f.nasiya = 0
                jami += int(f.naqd_som) + int(f.plastik) + int(f.nasiya_som)
        except Exception as e:
            print(e,"nonemi bu")
        context = super().get_context_data(**kwargs)
        context['home'] = 'active'
        context['home_t'] = 'true'
        context['salers'] = salers
        context['filials'] = filials
        context['jamisum'] = jami

        if som != 0:
            context['naqd_som'] = naqd_som
            context['naqd_dollar'] = naqd_dollar
            context['plastik'] = plastik
            context['nasiya_som'] = nasiya_som
            context['nasiya_dollar'] = nasiya_dollar
            context['transfer'] = transfer
            context['skidka_som'] = skidka_som
            context['skidka_dollar'] = skidka_dollar
        else:
            context['naqd_som'] = 0
            context['naqd_dollar'] = 0
            context['plastik'] = 0
            context['nasiya_som'] = 0
            context['nasiya_dollar'] = 0
            context['transfer'] = 0
            context['skidka_som'] = 0
            context['skidka_dollar'] = 0
        return context


class LTV(LoginRequiredMixin, TemplateView):
    template_name = 'LTV.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ltv'] = 'active'
        context['ltv_t'] = 'true'
        
        return context
# get ajax LTV datas 
def get_ltv_data(request):
    try:
        #time
        day = datetime.now()
        month = day.month
        year = day.year

        date_start = request.GET.get('start')
        date_end = request.GET.get('end')

        if month == 12:
            month2 = 1
            year2 = year + 1
        else:
            month2 = month + 1
            year2 = year
       

        ll = []
        if date_start is not None and date_end is not None:
            debrors = Debtor.objects.filter(date__gte=date_start, date__lte=date_end)
            debtor_pay_history = PayHistory.objects.filter(date__gte=date_start, date__lte=date_end)
        else:
            debrors = Debtor.objects.filter(date__month=month)
            debtor_pay_history = PayHistory.objects.filter(date__month=month)
        productfilials=ProductFilial.objects.all()

        all_clint_qarz_som = 0
        all_clint_qarz_dollar = 0

        all_clint_tulagan_som = 0
        all_clint_tulagan_dollar = 0

        all_clint_qarz_qoldiq_som = 0
        all_clint_qarz_qoldiq_dollar = 0

        all_clint_daromad_som = 0
        all_clint_daromad_dollar = 0
        for debror in debrors:
            #qarz
            qarz_sum = debrors.filter(id=debror.id,).aggregate(Sum('som'))['som__sum']
            qarz_dollar = debrors.filter(id=debror.id).aggregate(Sum('dollar'))['dollar__sum']
            #tulanganlari
            total_tulagan_som = debtor_pay_history.filter(debtor_id=debror.id).aggregate(Sum('som'))['som__sum']
            total_tulagan_dollar = debtor_pay_history.filter(debtor_id=debror.id).aggregate(Sum('dollar'))['dollar__sum']
            
            # mijoz olgan tavarlar total sotish summasi
            total_olgan_tavar_sum = productfilials.filter(filial__filial_pay__debtor_id=debror.id).aggregate(Sum('sotish_som'))['sotish_som__sum']
            total_olgan_tavar_dollar = productfilials.filter(filial__filial_pay__debtor_id=debror.id).aggregate(Sum('sotish_dollar'))['sotish_dollar__sum']
            #mijoz olgan avarlar total kelish summasi
            total_olgan_tavar_kelish_sum = productfilials.filter(filial__filial_pay__debtor_id=debror.id).aggregate(Sum('som'))['som__sum']
            total_olgan_tavar_kelish_dollar = productfilials.filter(filial__filial_pay__debtor_id=debror.id).aggregate(Sum('dollar'))['dollar__sum']
            if qarz_sum is None or qarz_dollar is None or total_tulagan_som is None or total_olgan_tavar_sum is None or total_olgan_tavar_dollar is None or total_tulagan_dollar is None or total_olgan_tavar_kelish_sum is None or total_olgan_tavar_kelish_dollar is None:
                qoldiq_qarz_sum = 0
                qoldiq_qarz_dollar = 0
                mijozdan_daromad_sum = 0
                mijozdan_daromad_dollar = 0
                
                all_clint_qarz_som += qarz_sum
                all_clint_qarz_dollar += qarz_dollar
                all_clint_tulagan_som += 0
                all_clint_tulagan_dollar += 0
                
                
            else:
                #qarz
                qoldiq_qarz_sum = float(qarz_sum) - float(total_tulagan_som)
                qoldiq_qarz_dollar = float(qarz_dollar) - float(total_tulagan_dollar)
                #foyda
                mijozdan_daromad_sum = float(total_olgan_tavar_sum) - float(total_olgan_tavar_kelish_sum)
                mijozdan_daromad_dollar = float(total_olgan_tavar_dollar) - float(total_olgan_tavar_kelish_dollar)
                #sum
                all_clint_tulagan_som += total_tulagan_som
                all_clint_tulagan_dollar += total_tulagan_dollar
            #qarz sum
            if qoldiq_qarz_sum > 0:
                all_clint_qarz_qoldiq_som += qoldiq_qarz_sum
            all_clint_qarz_qoldiq_dollar += qoldiq_qarz_dollar
            all_clint_daromad_som += mijozdan_daromad_sum
            all_clint_daromad_dollar += mijozdan_daromad_dollar
                
            dt = { 
                'fio': debror.fio,
                'total_tulagan_som': total_tulagan_som,
                'total_tulagan_dollar': total_tulagan_dollar,
                'qarz_sum': qarz_sum,
                'qarz_dollar': qarz_dollar,
                'total_olgan_tavar_sum': total_olgan_tavar_sum,
                'total_olgan_tavar_dollar': total_olgan_tavar_dollar,
                'qoldiq_qarz_sum': qoldiq_qarz_sum,
                'qoldiq_qarz_dollar': qoldiq_qarz_dollar,
                'mijozdan_daromad_sum': mijozdan_daromad_sum,
                'mijozdan_daromad_dollar': mijozdan_daromad_dollar,
                }
            ll.append(dt)

        context = {
            'malumotlar': ll,
            'all_clint_qarz_som': all_clint_qarz_som,
            'all_clint_qarz_dollar': all_clint_qarz_dollar,
            'all_clint_tulagan_som': all_clint_tulagan_som,
            'all_clint_tulagan_dollar': all_clint_tulagan_dollar,
            'all_clint_qarz_qoldiq_som': all_clint_qarz_qoldiq_som,
            'all_clint_qarz_qoldiq_dollar': all_clint_qarz_qoldiq_dollar,
            'all_clint_daromad_som': all_clint_daromad_som,
            'all_clint_daromad_dollar': all_clint_daromad_dollar,
        }
        return render(request, 'get_ltv_data.html', context)
    
    except Exception as e:
        print(e)
        return JsonResponse({'error': 'error'})
        

class Products(LoginRequiredMixin, TemplateView):
    template_name = 'product.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['productfilials'] = ProductFilial.objects.all()
        context['productfilials_total_som'] = ProductFilial.objects.aggregate(Sum('som'))['som__sum']
        context['productfilials_total_dollar'] = ProductFilial.objects.aggregate(Sum('dollar'))['dollar__sum']
        context['productfilials_total_quantity'] = ProductFilial.objects.aggregate(Sum('quantity'))['quantity__sum']
        context['productfilials_total_min_count'] = ProductFilial.objects.aggregate(Sum('min_count'))['min_count__sum']
        product_filial = ProductFilial.objects.all()
        context['total_product_sum'] = sum(i.som * i.quantity for i in product_filial)
        context['product'] = 'active'
        context['product_t'] = 'true'

        return context


class Filials(LoginRequiredMixin, TemplateView):
    template_name = 'filial.html'

    def get_context_data(self, **kwargs):
        # gte, lte = monthly()
        
        lte = datetime.now()
        gte = lte - timedelta(days=1)
        som = 0
        dollar = 0
        
        filials = Filial.objects.extra(
            select={
                'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.filial_id = api_filial.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'pay_som': 'select sum(api_payhistory.som) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
                    gte, lte),
                'pay_dollar': 'select sum(api_payhistory.dollar) from api_payhistory where api_payhistory.filial_id = api_filial.id and api_payhistory.date > "{}" and api_payhistory.date < "{}"'.format(
                    gte, lte)
            }
        )
        for f in filials:
            if f.naqd_som:
                som += f.naqd_som
                if f.plastik:
                    som += f.plastik
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                else:
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
            else:
                if f.plastik:
                    som += f.plastik
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                else:
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
                            else:
                                if f.pay_som:
                                    som += f.pay_som
                                else:
                                    pass
            if f.naqd_dollar:
                dollar += f.naqd_dollar
                if f.nasiya_dollar:
                    dollar += f.nasiya_dollar
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
                else:
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
            else:
                if f.nasiya_dollar:
                    dollar += f.nasiya_dollar
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
                else:
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
        context = super().get_context_data(**kwargs)
        context['filial'] = 'active'
        context['filial_t'] = 'true'
        context['som'] = som
        context['dollar'] = dollar
        context['filials'] = filials

        return context


class WareFakturas(LoginRequiredMixin, TemplateView):
    template_name = 'warefaktura.html'

    def get_context_data(self, request, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warefakturas'] = 'active'
        context['warefakturas_t'] = 'true'
        context['fakturas'] = Faktura.objects.filter(status=1)
        context['fakturaitems'] = FakturaItem.objects.all()

        return context

class WareFakturaTarix(LoginRequiredMixin, TemplateView):
    template_name = 'warefakturatarix.html'

    def get_context_data(self, **kwargs):
        gte, lte = monthly()
        context = super().get_context_data(**kwargs)
        context['warefakturatarix'] = 'active'
        context['warefakturatarix_t'] = 'true'
        context['fakturas'] = Faktura.objects.filter(date__gte=gte, date__lte=lte)

        return context


class Saler(LoginRequiredMixin, TemplateView):
    template_name = 'saler.html'

    def get_context_data(self, **kwargs):
        gte, lte = monthly()
        salers = UserProfile.objects.extra(
            select={
                'naqd_som': 'select sum(api_shop.naqd_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'naqd_dollar': 'select sum(api_shop.naqd_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'plastik': 'select sum(api_shop.plastik) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'nasiya_som': 'select sum(api_shop.nasiya_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'nasiya_dollar': 'select sum(api_shop.nasiya_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'transfer': 'select sum(api_shop.transfer) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'skidka_som': 'select sum(api_shop.skidka_som) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
                'skidka_dollar': 'select sum(api_shop.skidka_dollar) from api_shop where api_shop.saler_id = api_userprofile.id and api_shop.date > "{}" and api_shop.date < "{}"'.format(
                    gte, lte),
            }
        )
        som = 0
        dollar = 0
        for f in salers:
            if f.naqd_som:
                som += f.naqd_som
                if f.plastik:
                    som += f.plastik
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                else:
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
            else:
                if f.plastik:
                    som += f.plastik
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                else:
                    if f.nasiya_som:
                        som += f.nasiya_som
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                    else:
                        if f.transfer:
                            som += f.transfer
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
                        else:
                            if f.skidka_som:
                                som += f.skidka_som
                            else:
                                pass
            if f.naqd_dollar:
                dollar += f.naqd_dollar
                if f.nasiya_dollar:
                    dollar += f.nasiya_dollar
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
                else:
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
            else:
                if f.nasiya_dollar:
                    dollar += f.nasiya_dollar
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
                else:
                    if f.skidka_dollar:
                        dollar += f.skidka_dollar
                    else:
                        pass
        context = super().get_context_data(**kwargs)
        context['saler'] = 'active'
        context['saler_t'] = 'true'
        context['salers'] = salers
        context['som'] = som
        context['dollar'] = dollar
        return context


class Ombor(LoginRequiredMixin, TemplateView):
    template_name = 'ombor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['ombors'] = ProductFilial.objects.all()
        context['total_som'] = ProductFilial.objects.aggregate(Sum('som'))['som__sum']
        context['total_dollar'] = ProductFilial.objects.aggregate(Sum('dollar'))['dollar__sum']
        context['total_quantity'] = ProductFilial.objects.aggregate(Sum('quantity'))['quantity__sum']

        return context


class OmborQabul(LoginRequiredMixin, TemplateView):
    template_name = 'omborqabul.html'

    def get_context_data(self, **kwargs):
        gte, lte = monthly()
        context = super().get_context_data(**kwargs)
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['wares'] = Recieve.objects.filter(date__gte=gte, date__lte=lte)
        # for r in Recieve.objects.filter(date__gte=gte, date__lte=lte):
        #     print(r.date)
        return context

class OmborMinus(LoginRequiredMixin, TemplateView):
    template_name = 'omborminus.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['ombors'] = ProductFilial.objects.filter(quantity__lte=100)
        context['total_som'] = ProductFilial.objects.filter(quantity__lte=100).aggregate(Sum('som'))['som__sum']
        context['total_dollar'] = ProductFilial.objects.filter(quantity__lte=100).aggregate(Sum('dollar'))['dollar__sum']
        context['total_soni'] = ProductFilial.objects.aggregate(Sum('quantity'))['quantity__sum']

        return context

class Fakturas(LoginRequiredMixin, TemplateView):
    template_name = 'faktura.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['fakturas'] = Faktura.objects.filter(status=1)
        context['fakturaitems'] = FakturaItem.objects.all().order_by('-id')[0:1000]

        return context

class Recieves(LoginRequiredMixin, TemplateView):
    template_name = 'recieves.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['recieves'] = Recieve.objects.all().order_by('-id')
        context['recieveitems'] = RecieveItem.objects.all().order_by('-id')[:1000]

        return context

class FakturaTarix(LoginRequiredMixin, TemplateView):
    template_name = 'fakturatarix.html'

    def get_context_data(self, **kwargs):
        gte, lte = monthly()
        context = super().get_context_data(**kwargs)
        context['ombor'] = 'active'
        context['ombor_t'] = 'true'
        context['fakturas'] = Faktura.objects.filter(date__gte=gte, date__lte=lte)

        return context


def DataFak(request):
    data = json.loads(request.body)
    date1 = data['date1']
    date2 = data['date2']
    wares = Faktura.objects.filter(date__gte=date1, date__lte=date2)
    wr = []
    for w in wares:
        t = {
            'id': w.id,
            'summa': w.summa,
            'filial': w.filial.name,
            'difference': w.difference,
            'date': w.date.strftime("%d-%m-%y %I:%M")

        }
        wr.append(t)
    dt1 = {
        'wares': wr
    }
    return JsonResponse(dt1)


def GetFakturaItem(request):
    data = json.loads(request.body)
    id = data['id']
    items = FakturaItem.objects.filter(faktura_id=id)
    it = []
    for i in items:
        its = {
            'id': i.id,
            'product': i.product.name,
            'price': i.price,
            'quantity': i.quantity
        }
        it.append(its)
    dt1 = {
        'items': it
    }
    return JsonResponse(dt1)

class Table(TemplateView):
    template_name = 'table.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['table'] = 'active'
        context['table_t'] = 'true'

        return context

class DataTable(TemplateView):
    template_name = 'datatable.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['datatable'] = 'active'
        context['datatable_t'] = 'true'

        return context


class Hodim(LoginRequiredMixin, TemplateView):
    template_name = 'hodim.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hodim'] = 'active'
        context['hodim_t'] = 'true'
        context['salers'] = UserProfile.objects.filter(~Q(staff=1))
        context['filials'] = Filial.objects.all()

        return context

def delete_hodim(request, id):
    bad_hodim = UserProfile.objects.get(id=id)
    bad_hodim.staff=1
    bad_hodim.save()
    return redirect('hodim')

class Debtors(LoginRequiredMixin, TemplateView):
    template_name = 'debtor.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['debtor'] = 'active'
        context['debtor_t'] = 'true'
        context['debtors'] = Debtor.objects.all()
        context['total_som'] = Debtor.objects.aggregate(Sum('som'))['som__sum']
        context['total_dollar'] = Debtor.objects.aggregate(Sum('dollar'))['dollar__sum']

        return context


class Delivers(LoginRequiredMixin, TemplateView):
    template_name = 'deliver.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['deliver'] = 'active'
        context['deliver_t'] = 'true'
        context['delivers'] = Deliver.objects.all()

        return context

class FakturaYoqlama(LoginRequiredMixin, TemplateView):
    template_name = 'fakturayoqlama.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['kamomads'] = Kamomad.objects.all()
        return context

class Profile(TemplateView):
    template_name = 'profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['home_t'] = 'true'
        # context['user'] = UserProfile.objects.get(username)

        return context

class ProfileSetting(TemplateView):
    template_name = 'profile-setting.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['home_t'] = 'true'

        return context

class SweetAlert(TemplateView):
    template_name = 'sweet-alert.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sweet_alert'] = 'active'
        context['sweet_alert_t'] = 'true'

        return context

class Date(TemplateView):
    template_name = 'date.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = 'active'
        context['date_t'] = 'true'

        return context

class Widget(TemplateView):
    template_name = 'widget.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['widget'] = 'active'
        context['widget_t'] = 'true'

        return context


def Login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Login yoki Parol notogri kiritildi!')
            return redirect('login')
    else:
        return render(request, 'login.html')


def Logout(request):
    logout(request)
    messages.success(request, "Tizimdan chiqish muvaffaqiyatli yakunlandi!")
    return redirect('login')


def kassa(request):
    
    bugun = datetime.today()
    hodimlar = HodimModel.objects.all()
    kassa_var = Kassa.objects.first()
   
    hodimlar_royxat = []
    hodimlar_qarz = []
    shu_oylik_chiqimlar = Chiqim.objects.filter(qachon__year=bugun.year, qachon__month=bugun.month)
    chiqim_turlari = ChiqimTuri.objects.all()

    for hodim in hodimlar:
        qarz_som = 0
        qarz_dol = 0
        for q in hodim.hodimqarz_set.filter(tolandi=False):
            qarz_som += q.qancha_som
            qarz_dol += q.qancha_dol
        
        dt = {
            'id': hodim.id,
            'ism_familya':hodim.toliq_ism_ol(),
            'filial':hodim.filial.name,
            'qarz_som':qarz_som,
            'qarz_dol':qarz_dol,
            
            
        }

        hodimlar_qarz.append(dt)

    for hodim in hodimlar:
        
        if not  OylikTolov.objects.filter(hodim_id=hodim.id, sana__year=bugun.year, sana__month=bugun.month).exists():
            hodimlar_royxat.append(hodim)
            
    content = {
        'kassa_active':'active',
        'kassa_true':'true',
        'hodimlar':hodimlar_royxat,
        'barcha_hodimlar':hodimlar,
        'shu_oylik_chiqimlar':shu_oylik_chiqimlar,
        "chiqim_turlari":chiqim_turlari,
        'hodimlar_qarz':hodimlar_qarz,
        'kassa':kassa_var
    }

    return render(request, 'kassa.html', content)

def hodimga_qarz(request):
    if request.method == "POST":
        kassa_var = Kassa.objects.first()
        uslub = request.POST['uslub']

        if uslub == 'yangi':

            hodim_id = request.POST['hodim_id']
            qancha_som = request.POST.get('qancha_som')
            qancha_dol = request.POST.get('qancha_dol')
            izox = request.POST.get('izox')
            
            if qancha_som.isdigit() or qancha_dol.isdigit():
                
                if not qancha_dol.isdigit():
                    qancha_dol = 0
                    
                if not qancha_som.isdigit():
                    qancha_som = 0
                  
                if int(qancha_som) > 0 or int(qancha_dol) > 0:
                    qarz = HodimQarz.objects.create(hodim_id=hodim_id, izox=izox)

                    if qancha_som:
                        qarz.qancha_som += int(qancha_som)
                        kassa_var.som -= int(qancha_som)

                    if qancha_dol:
                        qarz.qancha_dol += int(qancha_dol)
                        kassa_var.dollar -= int(qancha_dol)

                    qarz.save()
                    kassa_var.save()
                    
                    messages.info(request, "Qarz berildi!")
                    messages.info(request, f"hodim: {HodimModel.objects.get(id=hodim_id).toliq_ism_ol()}.")
                    messages.info(request, f"So'm: {qancha_som}")
                    messages.info(request, f"$: {qancha_dol}")
                
                else:
                    messages.info(request, "0 miqdorda qarz bermoqchimisiz! ????" )
                
            
            else:
                messages.info(request, "???? Biror pul miqdorini kiritib keyi bosing!")
            
        
        else:

            qarz_id = request.POST['qarz_id']
            hodim_id = request.POST['hodim_id']
            qancha_som = request.POST.get('qancha_som')
            qancha_dol = request.POST.get('qancha_dol')
            izox = request.POST['izox']

            qarz = HodimQarz.objects.get(id=qarz_id)

            if qancha_som:
                qarz.qaytargani_som += int(qancha_som)
                kassa_var.som += int(qancha_som)
            
            if qancha_dol:
                qarz.qaytargani_dol += int(qancha_dol)
                kassa_var.dollar += int(qancha_dol)

            qarz.qaytargandagi_izox = izox
            qarz.save()
            kassa_var.save()
            qarz.qarzni_tekshir()

            messages.info(request, "To'lov qabul qilindi")

            return redirect(f'/hodim-qarzlari/?hodim_id={hodim_id}')

        return redirect('/kassa/')


def hodim_qarzlari(request):
    
    hodim_id = request.GET['hodim_id']
    hodim = HodimModel.objects.get(id=hodim_id)
    qarzlari = hodim.hodimqarz_set.filter(tolandi=False)

    

    return render(request, 'hodim_qarzlari.html', {'hodim':hodim, 'qarzlari':qarzlari})


def chiqim_qilish(request):
    
    """ Kassadan chiqim qiladi """

    if request.method == 'POST':
        
        chiqim_turi = request.POST['chiqim_turi']
        qancha_som = request.POST.get('qancha_som')
        qancha_dol = request.POST.get('qancha_dol')
        qancha_hisob_raqamdan = request.POST.get('qancha_hisob_raqamdan')
        izox = request.POST['izox']

        kassa_var = Kassa.objects.first()

        chiqim = Chiqim.objects.create(qayerga_id=chiqim_turi, izox=izox)

        if qancha_som:
            chiqim.qancha_som = qancha_som
            kassa_var.som -= int(qancha_som)


        if qancha_dol:
            chiqim.qancha_dol = qancha_dol
            kassa_var.dollar -= int(qancha_dol)
        
        if qancha_hisob_raqamdan:
            chiqim.qancha_hisob_raqamdan = qancha_hisob_raqamdan
            kassa_var.hisob_raqam -= int(qancha_hisob_raqamdan)

        chiqim.save()
        kassa_var.save()

        return redirect('/kassa/')


def oylik_tolash(request):
    if request.method == "POST":
        
        hodim_id = request.POST['hodim_id']
        kassa_var = Kassa.objects.first()
        hodim = HodimModel.objects.get(id=hodim_id)

        OylikTolov.objects.create(hodim_id=hodim_id, pul=hodim.oylik)

        kassa_var.som -= hodim.oylik
        kassa_var.save()

        return redirect('/kassa/')



#998997707572 len = 12
def checkPhone(phone):
    try:
        int(phone)
        return (True, phone) if len(phone) >= 12 else (False, None)
    except:
        return False, None
#for fio and qarz som
def sms_text_replace(sms_text, customer):
    try:
        format_som = '{:,}'.format(int(customer.som))
        sms_texts = str(sms_text).format(name = customer.fio, som = format_som)
    except Exception as e:
        print(e)
    
    return sms_texts
#for fio
def sms_text_replaces(sms_text, customer):
    try:
        sms_texts = str(sms_text).format(name = customer.fio)
    except Exception as e:
        print(e)
    
    return sms_texts

#sms sender  if date today  
def schedular_sms_send():
    try:
        success_send_count = 0
        error_send_count = 0
        text = settings.DEADLINE_SMS
        vaqt = datetime.now().date()
        debtors = Debtor.objects.filter(debt_return__day=vaqt.day, debt_return__month=vaqt.month)

        for debtor in debtors:
            sms_text = sms_text_replaces(text, debtor)
            can, phone = checkPhone(debtor.phone1)
            if can:
                sendSmsOneContact(debtor.phone1, sms_text)
                success_send_count += 1
            else:
                error_send_count += 1
    except Exception as e:
        print(e)   
        
        
# old deptors 
def schedular_sms_send_olds():
    try:
        success_send_count = 0
        error_send_count = 0
        text = settings.OLD_DEADLINE_SMS
        vaqt = datetime.now().date()
        
        debtors = Debtor.objects.filter(debt_return__day__lt=vaqt.day, debt_return__month__lte=vaqt.month)

        for debtor in debtors:
            sms_text = sms_text_replaces(text, debtor)
            can, phone = checkPhone(debtor.phone1)
            if can:
                result = sendSmsOneContact(debtor.phone1, sms_text)
                success_send_count += 1
            else:
                error_send_count += 1
    except Exception as e:
        print(e)   

from datetime import timedelta  
# send 3days agos deptors 
def schedular_sms_send_alert():
    try:
        success_send_count = 0
        error_send_count = 0
        text = settings.THREE_DAY_AGO_SMS
        # 3kun oldingi kunlar
        thire_day_future = datetime.today() + timedelta(days=3)
        thire_day_future_date = thire_day_future.date()
        debtors = Debtor.objects.filter(debt_return__day=thire_day_future_date.day, debt_return__month=thire_day_future_date.month, som__gt = 0 , dollar__gt = 0)

        for debtor in debtors:
            sms_text = sms_text_replace(text, debtor)
            can, phone = checkPhone(debtor.phone1)
            if can:
                sendSmsOneContact(debtor.phone1, sms_text)
                success_send_count += 1
            else:
                error_send_count += 1
    except Exception as e:
        print(e)
