from rest_framework import routers
# from django.urls import include, path

from .views import CustomUserViewSet

router_users = routers.DefaultRouter()
router_users.register('', CustomUserViewSet, basename='users')


def is_route_selected(url_pattern):
    urls = [
        r'$',
        r'\d+/$',
        r'me/$',
        r'set_password/$',
    ]

    for u in urls:
        match = url_pattern.resolve(u)
        if match:
            return False
    return True


selected_user_routes = list(filter(is_route_selected, router_users.urls))
urlpatterns = [] + selected_user_routes
