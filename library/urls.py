from django.urls import path, include
from rest_framework.routers import DefaultRouter
from library.views import LibraryViewSet

router = DefaultRouter()
router.register(r'library', LibraryViewSet, basename='library')

urlpatterns = [
    path('', include(router.urls)),
]
