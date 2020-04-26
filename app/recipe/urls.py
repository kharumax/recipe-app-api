from django.urls import path,include
from rest_framework.routers import DefaultRouter

from recipe import views

router = DefaultRouter()
# ViewSet（オブジェクトの集合）に対し、動的かつ適切なURLを返す
# ex) api/recipe/1 => recipe obj id:1
# ViewSetの中で色々な処理を行う
router.register("tags",views.TagViewSet)

app_name = "recipe"
urlpatterns = [
    path('',include(router.urls)),
]


