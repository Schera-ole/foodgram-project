import datetime as dt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_http_methods
from django.urls import reverse
import json

from .models import Ingredient, IngredientAmount, Favorite, Follow, Recipe, ShopList, User 
from .forms import RecipeForm


def index(request):
    recipe_list = []
    if 'filters' in request.GET:
        filters = request.GET.getlist('filters')
        for f in filters:
            recipe_list_one_filter = list(Recipe.objects.filter(tags__contains=f))
            recipe_list=list(set(recipe_list)|set(recipe_list_one_filter))
    else:
        recipe_list = Recipe.objects.prefetch_related('author').order_by('-pub_date').all()
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

        if bool(ingredient) is False:
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
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    user_sl = get_object_or_404(User, username=request.user.username)
    recipe_sl = Recipe.objects.get(pk = body['id'])
    already_sl = ShopList.objects.filter(user=user_sl, recipe=recipe_sl).exists()
    if not already_sl:
        ShopList.objects.create(user=user_sl, recipe=recipe_sl)
        return JsonResponse({'success': True}, safe=False)
    return JsonResponse({'success': False}, safe=False)


@login_required
def del_shoplist(request, recipe_id):
    user_sl = get_object_or_404(User, username=request.user.username)
    recipe_sl = get_object_or_404(Recipe, pk=recipe_id)
    already_sl = ShopList.objects.filter(user=user_sl, recipe=recipe_sl).exists()
    if already_sl:
        ShopList.objects.get(user=user_sl, recipe=recipe_sl).delete()
        return redirect('shoplist')
    return redirect('shoplist')


@login_required
def get_shoplist(request):
    filename = 'shoplist.txt'
    content = ''
    users_recipe = ShopList.objects.filter(user=request.user)
    for recipe in users_recipe:
        amount = get_object_or_404(IngredientAmount, recipe=recipe.recipe)
        content = content + f'{amount.ingredient.title} {amount.amount} {amount.ingredient.units}\n'
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename={filename}'
    return response


def profile(request, username):
    user_profile = get_object_or_404(User, username=username)
    recipe_list = []
    if 'filters' in request.GET:
        filters = request.GET.getlist('filters')
        for f in filters:
            recipe_list_one_filter = list(
                Recipe.objects.filter(author = user_profile).filter(tags__contains=f)
                )
            recipe_list=list(set(recipe_list)|set(recipe_list_one_filter))
    else:
        recipe_list = Recipe.objects.filter(author = user_profile).prefetch_related('author').order_by('-pub_date')
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
    if 'filters' in request.GET:
        filters = request.GET.getlist('filters')
        for f in filters:
            recipe_favorite_one_filter = list(
                Favorite.objects.filter(user=request.user).filter(recipe__tags__contains=f)
                )
            recipe_favorite=list(set(recipe_favorite)|set(recipe_favorite_one_filter))
    else:
        recipe_favorite = Favorite.objects.filter(user=request.user)

    for i in reversed(recipe_favorite):
        recipe_list.append(i.recipe)
    
    paginator = Paginator(recipe_list, 6)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'favorite.html', {'page':page, 'paginator':paginator})


@require_http_methods(['POST'])
@login_required
def add_favorite(request):
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    user_favorite = get_object_or_404(User, username=request.user.username)
    recipe_favorite = Recipe.objects.get(pk = body['id'])
    already_favorites = Favorite.objects.filter(user=user_favorite, recipe=recipe_favorite).exists()
    if not already_favorites:
        Favorite.objects.create(user=user_favorite, recipe=recipe_favorite)
        return JsonResponse({'success': True}, safe=False)
    return JsonResponse({'success': False}, safe=False)


@require_http_methods(['DELETE'])
@login_required
def del_favorite(request, recipe_id):
    user_favorite = get_object_or_404(User, username=request.user.username)
    recipe_favorite = Recipe.objects.get(pk=recipe_id)
    already_favorites = Favorite.objects.filter(user=user_favorite, recipe=recipe_favorite).exists()
    if already_favorites:
        Favorite.objects.filter(user=user_favorite, recipe=recipe_favorite).delete()
        return JsonResponse({'success': True}, safe=False)
    return JsonResponse({'success': False}, safe=False)


@login_required
def follow(request):
    author_recipes = {}
    counter = {}
    follow = Follow.objects.filter(user=request.user)
    for i in follow:
        author_recipes[i.author] = Recipe.objects.filter(author=i.author)
        counter[i.author.username] = Recipe.objects.filter(author=i.author).count()-3
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
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    following = get_object_or_404(User, pk = body['id'])
    if request.user.username != following.username:
        follower = get_object_or_404(User, username=request.user.username)
        already_follows = Follow.objects.filter(user=follower, author=following).exists()
        if not already_follows:
            Follow.objects.create(user=follower, author=following)
            return JsonResponse({'success': True}, safe=False)
    return JsonResponse({'success': False}, safe=False)


@require_http_methods(['DELETE'])
@login_required
def del_follow(request, author_id):
    follower = get_object_or_404(User, username=request.user.username)
    following = get_object_or_404(User, pk=author_id)
    already_follows = Follow.objects.filter(user=follower, author=following).exists()
    if already_follows:
        Follow.objects.filter(user=follower, author=following).delete()
        return JsonResponse({'success': True}, safe=False)
    return JsonResponse({'success': False}, safe=False)


def get_ingredient(request):
    data = []
    find_ingredient=request.GET.get('query')
    value = Ingredient.objects.filter(title__istartswith=find_ingredient)
    for i in value:
        data.append({'title':i.title, 'dimension':i.units})
    return JsonResponse(data, safe=False)


def recipe_ingredient(request):
    data = {}
    for item in request.POST.items():
        if 'nameIngredient' in item[0]:
            name = item[1]
        if 'valueIngredient' in item[0]:
            value = item[1]
            data[name] = value
    return(data)


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)
