from django.conf.urls import url
from goods.views import IndexView, DetailView, ListView


urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^detail/(?P<sku_id>\d+)$', DetailView.as_view(), name='detail'),
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)',ListView.as_view(), name='list')
]