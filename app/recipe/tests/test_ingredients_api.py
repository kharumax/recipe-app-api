from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient,Recipe

from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse("recipe:ingredient-list")


class PublicIngredientApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test ing can be retrieved auth user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@londonappdev.com",
            "password123"
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        Ingredient.objects.create(user=self.user,name="Kale")
        Ingredient.objects.create(user=self.user, name="Salt")

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients,many=True)
        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,serializer.data)

    def test_ingredients_limited_to_user(self):
        user2 = get_user_model().objects.create_user(
            "other@londonappdev.com",
            "password123"
        )
        Ingredient.objects.create(user=user2, name="Vinegar")
        ingredient = Ingredient.objects.create(user=self.user, name="Tumeric")

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(len(res.data),1)
        self.assertEqual(res.data[0]["name"],ingredient.name)

    def test_create_ingredient_successful(self):
        payload = {"name":"Cabbage"}
        res = self.client.post(INGREDIENT_URL,payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload["name"]
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        payload = {"name":""}
        res = self.client.post(INGREDIENT_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        ing1 = Ingredient.objects.create(user=self.user, name="Breakfast")
        ing2 = Ingredient.objects.create(user=self.user, name="Lunch")

        recipe = Recipe.objects.create(
            title="Egg toast",
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        recipe.ingredients.add(ing1)

        res = self.client.get(INGREDIENT_URL, {"assigned_only": 1})

        serializer1 = IngredientSerializer(ing1)
        serializer2 = IngredientSerializer(ing2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        ing = Ingredient.objects.create(user=self.user, name="Breakfast")
        Ingredient.objects.create(user=self.user, name="Lunch")
        recipe1 = Recipe.objects.create(
            title="Egg toast",
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        recipe1.ingredients.add(ing)
        recipe2 = Recipe.objects.create(
            title="Tomato toast",
            time_minutes=10,
            price=5.00,
            user=self.user
        )
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENT_URL, {"assigned_only": 1})

        self.assertEqual(len(res.data), 1)



