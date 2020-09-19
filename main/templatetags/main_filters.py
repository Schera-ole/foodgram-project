from django import template
from main.models import Favorite, ShopList

register = template.Library()


@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter(name='get_filter_values')
def get_filter_values(value):
    return value.getlist('filters')


@register.filter(name='get_filter_link')
def get_filter_link(request, tag):
    new_request = request.GET.copy()

    if tag[0] in request.GET.getlist('filters'):
        filters = new_request.getlist('filters')
        filters.remove(tag[0])
        new_request.setlist('filters',filters)
    else:
        new_request.appendlist('filters', tag[0])

    return new_request.urlencode()
    

@register.filter(name='star_filter')
def star_filter(recipe, user):
    return Favorite.objects.filter(user=user, recipe=recipe).exists()


@register.filter(name='shop_filter')
def shop_filter(recipe, user):
    return ShopList.objects.filter(user=user, recipe=recipe).exists()
    