from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import router


frontend_router = DefaultRouter()


for prefix, viewset, basename in router.registry:
    frontend_router.register(prefix, viewset, basename=basename)

urlpatterns = [
    path('', include(frontend_router.urls)),
]



