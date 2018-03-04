from django.shortcuts import render, redirect
from django.views.generic import View
from goods.models import GoodsSKU, Goods, GoodsCategory, IndexGoodsBanner, IndexPromotionBanner,IndexCategoryGoodsBanner
from django.core.cache import cache
from django_redis import get_redis_connection
from django.core.urlresolvers import reverse
from django.core.paginator import Page, Paginator
# Create your views here.


class IndexView(View):

    def get(self,request):
        context = cache.get('index_page_data')

        if context is None:
            categorys = GoodsCategory.objects.all()
            banners = IndexGoodsBanner.objects.all().order_by('index')
            promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

            for category in categorys:
                title_banners = IndexCategoryGoodsBanner.objects.filter(category = category, display_type=0).order_by('index')
                category.title_banners = title_banners

                image_banners = IndexCategoryGoodsBanner.objects.filter(category = category, display_type=1).order_by('index')
                category.image_banners = image_banners

            context = {
                'categorys':categorys,
                'banners': banners,
                'promotion_banners': promotion_banners,
            }
            cache.set('index_page_data', context, 3600)
        cart_num = 0
        # context['cart_num'] = cart_num
        if request.user.is_authenticated():
            redis_conn = get_redis_connection('default')
            user_id = request.user.id
            user_dict = redis_conn.hgetall('cart_%s'%user_id)

            for value in user_dict.values():
                cart_num += int(value)

        context.update(cart_num = cart_num)
        return render(request,'index.html',context)


# 设置缓存：cache.set('key', 内容, 有效期)
# 读取缓存：cache.get('key')


class DetailView(View):

    def get(self,request, sku_id):
        context = cache.get('datail_sku_id')

        if context is None:

            try:

                sku = GoodsSKU.objects.get(id=sku_id)
            except:
                return redirect(reverse('goods:detail'))

            categorys = GoodsCategory.objects.all()
            sku_orders = sku.ordergoods_set.all().order_by('-create_time')[:30]

            if sku_orders:
                for sku_order in sku_orders:
                    sku_order.ctime = sku_order.create_time.strftime('%Y-%m-%d %H:%M:%S')
                    sku_order.username = sku_order.order.username
            else:
                sku_orders = []

            new_skus = GoodsSKU.objects.all().order_by('-create_time')[:2]
            other_skus = sku.goods.goodssku_set.exclude(id=sku_id)

            context = {
                "categorys": categorys,
                "sku": sku,
                "orders": sku_orders,
                "new_skus": new_skus,
                "other_skus": other_skus
            }

            cache.set('detail_%s'%sku_id,context, 3600)

        cart_num = 0
        if request.user.is_authenticated():
            redis_conn = get_redis_connection('default')
            user_id = request.user.id
            user_dict = redis_conn.hgetall('cart_%s' % user_id)

            for value in user_dict.values():
                cart_num += int(value)

            redis_conn.lrem('history_%s' % user_id, 0, sku_id)
            redis_conn.lpush('history_%s' % user_id, sku_id)
            redis_conn.ltrim('history_%s' % user_id, 0, 4)

        context.update({"cart_num": cart_num})
        return render(request, 'detail.html', context)


class ListView(View):

    def get(self, request, category_id, page_num):
        sort = request.GET.get('sort', 'default')

        try:
            category = GoodsCategory.objects.get(id = category_id)
        except:
            return redirect(reverse('goods:index'))

        categorys = GoodsCategory.objects.all()

        new_skus = GoodsSKU.objects.filter(category = category).order_by('-create_time')[:2]

        if sort == 'price':
            skus = GoodsSKU.objects.filter(category = category).order_by('price')

        elif sort == 'hot':
            skus = GoodsSKU.objects.filter(category = category).order_by('-price')

        else:
            skus = GoodsSKU.objects.filter(category = category)
            sort = 'default'

        page_num = int(page_num)

        paginator = Paginator(skus, 2)

        try:
            page_skus = paginator.page(page_num)

        except:
            page_skus = paginator.page(1)

        page_list = paginator.page_range

        cart_num = 0

        if request.user.is_authenticated():

            user_id = request.user.id

            redis_conn = get_redis_connection('default')

            cart_dict = redis_conn.hgetall('cart_%s'% user_id)
            for val in cart_dict.values():

                cart_num += int(val)

        context = {
            "category": category,
            'categorys': categorys,
            'new_skus': new_skus,
            'skus': skus,
            'sort': sort,
            'page_num': page_num,
            'page_skus': page_skus,
            'page_list': page_list,
            'cart_num': cart_num
        }
        return render(request, 'list.html', context)