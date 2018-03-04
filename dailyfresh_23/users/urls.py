from django.conf.urls import url
# from users.views import register
from users.views import Register, ActiveView,LoginView, LoginoutView, AddressView, UserinfoView

urlpatterns = [
    # url(r'^register/$', register, name='register')
    url(r'^register/$', Register.as_view(), name='register'),
    url(r'^active/(?P<token>.+)$', ActiveView.as_view(), name='active'),
    url(r'^login/$',LoginView.as_view(), name='login'),
    url(r'^logout/$', LoginoutView.as_view(), name='logout'),
    url(r'^address/$', AddressView.as_view(), name='address'),
    url(r'^userinfo/$', UserinfoView.as_view(), name='userinfo')
]