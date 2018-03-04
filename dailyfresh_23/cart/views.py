from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse, HttpRequest, JsonResponse
from goods.models import GoodsSKU, GoodsCategory, Goods, GoodsImage
from django_redis import get_redis_connection
import json
# Create your views here.


class AddCartView(View):

    def post(self, request):
        # if not request.user.is_authenticated():
        #     return JsonResponse({'code': 1, 'message': '用户未登录'})

        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')
        if not all([sku_id, count]):

            return JsonResponse({'code': 2, 'message': '参数不完整'})

        try:
            sku = GoodsSKU.objects.get(id= sku_id)
        except:
            return JsonResponse({'code': 3, 'message': '商品不存在'})

        try:
            count = int(count)
        except:
            return JsonResponse({'code': 4, 'message': '数据错误'})

        if count > sku.stock:
            return JsonResponse({'code': 5, 'message': '库存不足'})

        if request.user.is_authenticated():
            user_id = request.user.id
            redis_conn = get_redis_connection('default')

            origin_count = redis_conn.hget('cart_%s' % user_id, sku_id)

            if origin_count is not None:
                count += int(origin_count)

            if count > sku.stock:
                return JsonResponse({'code': 5, 'message': '库存不足'})

            redis_conn.hset('cart_%s'%user_id, sku_id, count)

            cart_num = 0

            cart_dict = redis_conn.hgetall('cart_%s'%user_id)
            for val in cart_dict.values():
                cart_num += int(val)

            return JsonResponse({'code': 0, 'cart_num': cart_num})

        else:
            cart_json = request.COOKIES.get('cart')

            if cart_json is not None:
                cart_dict = json.loads(cart_json)

            else:
                cart_dict = {}

            if sku_id in cart_dict:
                origin_count = cart_dict[sku_id]
                count += origin_count
            if count > sku.stock:

                return JsonResponse({'code': 5, 'massage': '库存不足'})

            cart_dict[sku_id] = count
            cart_num = 0
            for val in cart_dict.values():
                cart_num += val

            cart_str = json.dumps(cart_dict)
            response = JsonResponse({'code':0, 'massage': '添加成功','cart_num': cart_num})
            response.set_cookie('cart', cart_str)
            return response


class BaseCartView(View):

    def get_cart_num(self,request):

        cart_num = 0

        if request.user.is_authenticated():
            redis_conn = get_redis_connection('default')
            user_id = request.user.id
            cart_dict = redis_conn.hgetall('cart_%s'%user_id)

            for val in cart_dict.values():
                cart_num += val
        else:
            cart_num = 0
            cart_json = request.COOKIES.GET('cart')

            if cart_json is not None:

                cart_dict = json.loads(cart_json)

            else:
                cart_dict = {}

        for val in cart_dict.values():
            cart_num += int(val)

        return cart_num


class CartInfoView(BaseCartView):

    def get(self,request):

        if request.user.is_authenticated():

            redis_conn = get_redis_connection('default')

            user_id = request.user.id
            cart_dict = redis_conn.hgetall('cart_%s'%user_id)

        else:

            cart_json = request.COOKIES.get('cart')

            if cart_json is not None:

                cart_dict = json.loads(cart_json)
            else:
                cart_dict = {}

        skus = []
        total_amount = 0
        total_count = 0

        for sku_id, count in cart_dict.items():

            try:
                sku = GoodsSKU.objects.get(id= sku_id)
            except Exception:
                continue

            count = int(count)
            amount = sku.price * count

            sku.amount = amount
            sku.count = count

            skus.append(sku)

            total_count += count
            total_amount += amount

        context = {
            'total_count': total_count,
            'total_amount': total_amount,
            'skus': skus
        }

        return render(request, 'cart.html', context)


class UpdateCartView(View):
    def post(self, request):

        sku_id = request.POST.get('sku_id')
        count = request.POST.get('count')

        if not all([sku_id, count]):
            return JsonResponse({'code': 1, 'massage': '参数不完整'} )
        try:

            sku = GoodsSKU.objects.get(id = sku_id)
        except Exception:
            return JsonResponse({'code':2, 'massage': '商品不存在'})

        try:
            count = int(count)
        except Exception:

            return JsonResponse({'code': 3, 'massage': '数量错误!'})

        if count > sku.stock:
            return JsonResponse({'code': 4, 'massage': '库存不足'})

        if request.user.is_authenticated():
            redis_conn = get_redis_connection('default')
            user_id = request.user.id
            redis_conn.hset('cart_%s'%user_id, sku_id, count)
            return JsonResponse({'code': 0, 'message': '添加购物车成功'})

        else:

            cart_json = request.COOKIES.get('cart')
            if cart_json is not None:

                cart_dict = json.loads(cart_json)
                cart_dict[sku_id] = count
                new_cart_dict = json.dumps(cart_dict)
                response = JsonResponse({'code': 0, 'massage': '添加购物车成功'})
                response.set_cookie('cart', new_cart_dict)

                return response


class DeleteCartView(View):
    def post(self, request):
        sku_id = request.POST.get('sku_id')

        if not sku_id:
            return JsonResponse({'code': 1, 'message': '参数错误'})

        if request.user.is_authenticated():

            redis_conn = get_redis_connection('default')

            user_id = request.user.id
            redis_conn.hdel('cart_%s'%user_id, sku_id)
        else:

            cart_json = request.COOKIES.get('cart')
            if cart_json is not None:
                cart_dict = json.loads(cart_json)
                if sku_id in cart_dict:
                    del cart_dict[sku_id]

                response = JsonResponse({'code': 0, 'message': '删除成功'})
                response.set_cookie('cart',json.dumps(cart_dict))
                return response
        return JsonResponse({'code': 0, 'message': '删除成功'})