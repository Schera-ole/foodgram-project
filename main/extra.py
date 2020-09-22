from django.db.models import Q


def recipe_ingredient(request):
    data = {}
    for item in request.POST.items():
        if 'nameIngredient' in item[0]:
            name = item[1]
        if 'valueIngredient' in item[0]:
            value = item[1]
            data[name] = value
    return(data)


def get_Q_objects_r(filter_tags):
    q_objects = Q()
    for f in filter_tags:
        q_objects |= Q(tags__contains=f)
    return q_objects


def get_Q_objects_f(filter_tags):
    q_objects = Q()
    for f in filter_tags:
        q_objects |= Q(recipe__tags__contains=f)
    return q_objects
    