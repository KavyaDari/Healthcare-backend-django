from rest_framework.routers import DefaultRouter
from .views import MappingViewSet

router = DefaultRouter()
router.register('', MappingViewSet, basename='mappings')

urlpatterns = router.urls