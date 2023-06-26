from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework.fields import SerializerMethodField

from users.models import Follow, User
from .recipes import RecipeInfoSerializer


class UserCreateSerializer(UserCreateSerializer):
    """Обработка запросов на создание пользователя."""
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'password',
            'id',
            'first_name',
            'last_name'
        )
        extra_kwargs = {"password": {"write_only": True}}


class UsersSerializer(UserSerializer):
    """Сериализатор для отоборажения информации."""
    is_subscribed = SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'is_subscribed',
            'id',
            'first_name',
            'last_name'
        )

    def get_is_subscribed(self, object):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=user,
            author=object.id
        ).exists()


class FollowSerializer(UserSerializer):
    """Сериализер для функции подписки."""
    recipes = SerializerMethodField(read_only=True)
    recipes_count = SerializerMethodField(read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, object):
        """Возвращает информацию обо всех рецпетах в подписке пользователя."""
        request = self.context.get('request')
        context = {'request': request}
        recipe_limit = request.query_params.get('recipe_limit')
        queryset = object.recipes.all()
        if recipe_limit:
            queryset = queryset[:int(recipe_limit)]
        return RecipeInfoSerializer(queryset, context=context, many=True).data

    def get_recipes_count(self, object):
        return object.recipes.count()
