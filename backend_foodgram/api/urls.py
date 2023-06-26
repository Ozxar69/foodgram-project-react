from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.users import CustomUserViewSet
from .views.recipes import RecipeViewSet,IngredientViewSet, TagViewSet

router = DefaultRouter()
router.register(r'users', CustomUserViewSet)
router.register(r'recipes', RecipeViewSet)
router.register(r'ingredients',IngredientViewSet)
router.register(r'tags', TagViewSet)
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
