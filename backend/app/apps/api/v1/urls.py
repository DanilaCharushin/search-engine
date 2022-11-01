from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.trailing_slash = "/?"

urlpatterns = router.urls
