from django.conf.urls import url
from orders.views import PlaceOrdereView
urlpatterns = [
    url(r'^place$', PlaceOrdereView.as_view(), name='place')
]