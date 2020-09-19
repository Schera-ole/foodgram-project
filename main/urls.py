from django.urls import include, path
from . import views

urlpatterns = [
    path('new-recipe/', views.add_recipe, name='add_recipe'),
    path('my-favorite/', views.favorite, name='favorite'),
    path('my-follow/', views.follow, name='follow'),
    path('shop-list/', views.shoplist, name='shoplist'),

    path('<username>/', views.profile, name='profile'),
    path('<username>/<int:recipe_id>/', views.recipe, name='recipe'),
    path('<username>/<int:recipe_id>/edit/', views.edit_recipe, name='edit_recipe'),
    path('<username>/<int:recipe_id>/delete/', views.del_recipe, name='del_recipe'), 

    path('api/ingredients/', views.get_ingredient, name='get_ingredient'),
    path('api/favorites/', views.add_favorite, name='add_favorite'),
    path('api/favorites/<int:recipe_id>', views.del_favorite, name='del_favorite'),
    path('api/follow/', views.add_follow, name='add_follow'),
    path('api/follow/<int:author_id>', views.del_follow, name='del_follow'),
    path('api/purchases/', views.add_shoplist, name='add_shoplist'),
    path('api/purchases/getshoplist', views.get_shoplist, name='get_shoplist'),
    path('api/purchases/<int:recipe_id>', views.del_shoplist, name='del_shoplist'),

    path('', views.index, name='index'),
]
