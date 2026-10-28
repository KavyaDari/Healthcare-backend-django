from rest_framework.routers import DefaultRouter
from .views import PatientViewSet

router = DefaultRouter()
router.register('', PatientViewSet, basename='patients')

urlpatterns = router.urls