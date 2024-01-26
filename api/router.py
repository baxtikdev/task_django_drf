from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

# app_name = "api"
# router.register(r"product", ProductAPIView, basename='product')

urlpatterns = router.urls
