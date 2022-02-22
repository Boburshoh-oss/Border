from rest_framework import routers
from .mobilViewset import *
from .serializers import MCartSerializer

router = routers.DefaultRouter()

router.register('cart', MCartViewset)
router.register('product', ProductFilialViewset)
router.register('banner', BannerViewset)
router.register('order', MOrderViewset)

