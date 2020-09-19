from django.db import models
from django.contrib.auth import get_user_model
from multiselectfield import MultiSelectField

User = get_user_model()

TAGS_CHOICES = (('breakfast', 'Завтрак'), ('lunch', 'Обед'), ('dinner', 'Ужин'))


class Ingredient(models.Model):
    title = models.CharField(max_length=200)
    units = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class IngredientAmount(models.Model):
    amount = models.IntegerField()
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incredient',
    )
    recipe = models.ForeignKey('Recipe', on_delete=models.SET_NULL, null=True)


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipe_author'
    )
    image = models.ImageField(
        upload_to='image/',
        default='default.jpg',
        blank=True,
        null=True,
        verbose_name='Выбрать файл',
    )
    ingredient = models.ManyToManyField(
        Ingredient, through=IngredientAmount, blank=True
    )
    pub_date = models.DateTimeField('date published', auto_now_add=True)
    tags = MultiSelectField(choices=TAGS_CHOICES)
    text = models.TextField()
    time = models.DurationField(verbose_name='Время приготовления')
    title = models.CharField(max_length=200, verbose_name='Название рецепта')

    def __str__(self):
        return self.title


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_favorite'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_favorite'
    )  


class Follow(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    

class ShopList(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='recipe_shoplist'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='user_shoplist'
    )
