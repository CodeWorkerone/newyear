from django.shortcuts import render, redirect
from utils.views import Login_required
from django.views.generic import View
from django_redis import get_redis_connection
from goods.models import GoodsSKU
from django.core.urlresolvers import reverse
from users.models import Address
# Create your views here.


class PlaceOrdereView(Login_required, View):
    def post(self, request):

        sku_ids = request.POST.getlist('sku_ids')
        count = request.POST.get('count')

        if not sku_ids:
            return redirect(reverse('cart: cartinfo'))

        skus = []
        total_count = 0
        total_amount = 0
        trans_cost = 10
        total_sku_amount = 0

        if count is None:

            redis_conn = get_redis_connection('default')

            user_id = request.user.id
            cart_dict = redis_conn.hgetall('cart_%s'%user_id)

            for sku_id in sku_ids:
                try:
                    sku = GoodsSKU.objects.get(id=sku_id)
                    print(sku)
                except Exception:
                    return redirect(reverse('cart:cartinfo'))

                sku_count = cart_dict[sku_id.encode()]
                sku_count = int(sku_count)
                print(sku)
                print(sku_count)
                amount = sku_count * sku.price
                print(sku.price)
                sku.count = sku_count
                sku.amount = amount

                skus.append(sku)

                total_amount += amount

                total_amount += sku_count

        else:
            for sku_id in sku_ids:
                try:
                    sku = GoodsSKU.objects.get(id=sku_id)
                except GoodsSKU.DoesNotExist:
                    # 重定向到购物车
                    return redirect(reverse('cart:info'))

                try:

                    sku_count = int(count)

                except Exception:
                    return redirect(reverse('goods:detail', args=sku_id))

                if sku_count > sku.stock:
                    return redirect(reverse('goods:detail', args=sku_id))

                amount = sku_count * sku.price
                sku.amount = amount
                sku.count = sku_count
                skus.append(sku)

                total_amount += amount
                total_count += sku_count

        total_amount = total_amount + trans_cost

        try:

            address = Address.objects.get(user = request.user)
        except Exception:
            address = None

        context = {
            'skus': skus,
            'total_count': total_count,
            'total_sku_amount': total_sku_amount,
            'trans_cost': trans_cost,
            'total_amount': total_amount,
            'address': address
        }

        return render(request, 'place_order.html', context)



