from .models import ShopList, TAGS_CHOICES


def all_tags(request):
    all_tags = TAGS_CHOICES
    return {
        'all_tags': all_tags
    }
    

def shop_counter(request):
    #Вывод каунтера списка покупок
    if request.user.is_authenticated:
        shop_counter = ShopList.objects.filter(user=request.user).count()
    else:
        shop_counter = 0    
    return {'shop_counter': shop_counter}
