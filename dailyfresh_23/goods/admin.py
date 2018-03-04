from django.contrib import admin
from goods.models import GoodsCategory,GoodsSKU, Goods, IndexPromotionBanner
from celery_tasks.tasks import generate_static_index_html
from django.core.cache import cache
# Register your models here.


class BaseAdmin(admin.ModelAdmin):

    def delete_model(self, request, obj):
        obj.delete()
        generate_static_index_html.delay()
        cache.delete('index_page_data')

    def save_model(self, request, obj, form, change):
        obj.save()
        generate_static_index_html.delay()
        cache.delete('index_page_data')


class IndexPromotionBannerAdmin(BaseAdmin):
    pass

class GoodsAdmin(BaseAdmin):
    pass

class GoodsCategoryAdmin(BaseAdmin):
    pass

admin.site.register(GoodsCategory, GoodsCategoryAdmin)
admin.site.register(Goods, GoodsAdmin)
admin.site.register(GoodsSKU)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
