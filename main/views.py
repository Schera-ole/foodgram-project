import datetime as dt
import json
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Sum
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods
from django.urls import reverse


from .extra import get_Q_objects_f, get_Q_objects_r, recipe_ingredient
from .forms import RecipeForm
from .models import Ingredient, IngredientAmount, Favorite, Follow, Recipe, ShopList, User 


def index(request):
    recipe_list = []
    recipe_tmp = Recipe.objects.prefetch_related('author')
    if 'filters' in request.GET:
        filters = request.GET.getlist('filters')
        q_objects = get_Q_objects_r(filters)
        recipe_list = recipe_tmp.filter(q_objects)
    else:
        recipe_list = recipe_tmp.all()
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'page':page, 'paginator':paginator})


def recipe(request, username, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    return render(
        request,
        'singlePage.html',
        {'recipe': recipe},
    )

    
@login_required
def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST or None, files=request.FILES or None)
        ingredient = recipe_ingredient(request)

        if not bool(ingredient):
            form.add_error(None, 'Добавьте ингредиенты')

        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()

            for item in ingredient:
                IngredientAmount.objects.create(
                    recipe=recipe,
                    ingredient=Ingredient.objects.filter(title=item).all()[0],
                    amount=ingredient[item]
                )
        
            return redirect('index')
    else:
        form = RecipeForm(request.POST or None, files=request.FILES or None)
    return render(request, 'formRecipe.html', context={'form':form})


@login_required
def del_recipe(request, username, recipe_id):
    recipe=get_object_or_404(Recipe, pk=recipe_id)
    if request.user != recipe.author:
        return redirect(
            reverse('recipe', kwargs={'username': username, 'recipe_id': recipe_id})
        )
    recipe.delete()
    return redirect('index')


@login_required
def edit_recipe(request, username, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    if request.user != recipe.author:
        return redirect(
            reverse('recipe', kwargs={'username': username, 'recipe_id': recipe_id})
        )
    if request.method == 'POST':
        form = RecipeForm(
            request.POST or None, files=request.FILES or None, instance=recipe
            )
        ingredient = recipe_ingredient(request)

        if bool(ingredient):
            IngredientAmount.objects.filter(recipe__pk=recipe_id).delete()

        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            for item in ingredient:
                IngredientAmount.objects.create(
                    recipe=recipe,
                    ingredient=Ingredient.objects.filter(title=item).all()[0],
                    amount=ingredient[item]
                )
        return redirect('index')
    else:
        form = RecipeForm(
            request.POST or None, files=request.FILES or None, instance=recipe
            )
    return render(
            request, 'formChangeRecipe.html', context={'form':form, 'recipe':recipe}
            )


@login_required
def shoplist(request):
    recipe_sl = ShopList.objects.filter(user=request.user)
    return render(request, 'shopList.html', {'recipes':recipe_sl})


@require_http_methods(['POST'])
@login_required
def add_shoplist(request):
    body = json.loads(request.body)
    user_sl = get_object_or_404(User, username=request.user)
    recipe_sl = get_object_or_404(Recipe, pk = body['id'])
    ShopList.objects.get_or_create(user=user_sl, recipe=recipe_sl)
    return JsonResponse({'success': True}, safe=False)


@login_required
def del_shoplist(request, recipe_id):
    user_sl = get_object_or_404(User, username=request.user)
    recipe_sl = get_object_or_404(Recipe, pk=recipe_id)
    ShopList.objects.filter(user=user_sl, recipe=recipe_sl).delete()
    return redirect('shoplist')


@login_required
def get_shoplist(request):
    amount_dict = {}
    filename = 'shoplist.txt'
    content = ''
    users_recipe = ShopList.objects.filter(user=request.user)
    recipe = [recipe.recipe for recipe in users_recipe]
    amount = (
        IngredientAmount.objects.filter(recipe__in=recipe)
        .values("ingredient__title", "ingredient__dimension")
        .annotate(Sum("amount"))
    )
    for a in amount:
        title, dimension, amount_sum = a.values()
        content = content + f'{title} {amount_sum} {dimension}\n'
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    recipe_list = []
    recipe_tmp = Recipe.objects.filter(author=user_profile).prefetch_related('author')
    if 'filters' in request.GET:
        filters = request.GET.getlist('filters')
        q_objects = get_Q_objects_r(filters)
        recipe_list = recipe_tmp.filter(q_objects)
    else:
        recipe_list = recipe_tmp
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 
        'authorRecipe.html', {
            'page':page, 
            'paginator':paginator, 
            'author':user_profile
            }
        )


@login_required
def favorite(request):
    recipe_list = []
    recipe_favorite = []

    '''
    Отдельная фун-я т.к. тут запрос фильтруется по значению тега рецепта
    '''

    recipe_tmp = Favorite.objects.filter(user=request.user)
    if 'filters' in request.GET:
        filters = request.GET.getlist('filters')
        q_objects = get_Q_objects_f(filters)
        recipe_favorite= recipe_tmp.filter(q_objects)
    else:
        recipe_favorite = recipe_tmp

    '''
    До этого у нас объекты из таблицы Favorite, после - рецепты
    '''
    recipe_list = [i.recipe for i in recipe_favorite]

    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'favorite.html', {'page':page, 'paginator':paginator})


@require_http_methods(['POST'])
@login_required
def add_favorite(request):
    body = json.loads(request.body)
    user_favorite = get_object_or_404(User, username=request.user)
    recipe_favorite = get_object_or_404(Recipe, pk = body['id'])
    Favorite.objects.get_or_create(user=user_favorite, recipe=recipe_favorite)
    return JsonResponse({'success': True}, safe=False)


@require_http_methods(['DELETE'])
@login_required
def del_favorite(request, recipe_id):
    user_favorite = get_object_or_404(User, username=request.user)
    recipe_favorite = get_object_or_404(Recipe, pk=recipe_id)
    Favorite.objects.filter(user=user_favorite, recipe=recipe_favorite).delete()
    return JsonResponse({'success': True}, safe=False)


@login_required
def follow(request):
    author_recipes = {}
    counter = {}
    follow = Follow.objects.filter(user=request.user)
    for i in follow:
        recipe = Recipe.objects.filter(author=i.author)
        author_recipes[i.author] = recipe
        counter[i.author.username] = recipe.count()-3
        if counter[i.author.username] < 0:
            counter[i.author.username]= 0
    author_recipes = tuple(author_recipes.items())
    paginator = Paginator(author_recipes, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request, 
        'myFollow.html', {
            'page':page, 
            'paginator':paginator, 
            'counter':counter
            }
        )


@require_http_methods(['POST'])
@login_required
def add_follow(request):
    body = json.loads(request.body)
    following = get_object_or_404(User, pk = body['id'])
    if request.user != following:
        follower = get_object_or_404(User, username=request.user)
        Follow.objects.get_or_create(user=follower, author=following)
    return JsonResponse({'success': True}, safe=False)


@require_http_methods(['DELETE'])
@login_required
def del_follow(request, author_id):
    follower = get_object_or_404(User, username=request.user)
    following = get_object_or_404(User, pk=author_id)
    Follow.objects.filter(user=follower, author=following).delete()
    return JsonResponse({'success': True}, safe=False)


def get_ingredient(request):
    find_ingredient=request.GET.get('query')
    data = list(Ingredient.objects.filter(title__istartswith=find_ingredient).values('title', 'dimension'))
    return JsonResponse(data, safe=False)


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)
