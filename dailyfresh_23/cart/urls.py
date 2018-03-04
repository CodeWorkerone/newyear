from django.conf.urls import url

from cart.views import AddCartView, BaseCartView, CartInfoView, UpdateCartView, DeleteCartView

urlpatterns = [
    url(r'^add$', AddCartView.as_view(), name='add'),
    url(r'^cartinfo$', CartInfoView.as_view(), name='cartinfo'),
    url(r'^update$', UpdateCartView.as_view(), name='date'),
    url(r'^delete$', DeleteCartView.as_view(), name='delete')

]