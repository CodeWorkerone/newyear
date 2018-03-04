from django.shortcuts import render, redirect
from django.views.generic import View
from django.http import HttpResponse
import re
from users.models import User
from celery_tasks.tasks import send_active_email
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from utils.views import Login_required
from users.models import Address
from django_redis import get_redis_connection
from goods.models import GoodsSKU
import json


class Register(View):
    def get(self, request):
        if request.method == 'GET':
            return render(request, 'register.html')
        else:
            return HttpResponse('这里是注册页面!')

    def post(self, request):
        user_name = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')
        if not all([user_name, password, email, allow]):
            return redirect(reversed('users:register'))
        if not re.match (r"^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email):
            return render(request, 'register.html', {'errmsg':'邮箱格式不正确'})
        if allow != 'on':
            return render(request, 'register.html',{'errmsg': '没有勾选用户协议'})
        try:
            user = User.objects.create_user(user_name, email, password)
        except:
            return render(request, 'register.html', {'errmsg':'用户已认证'})
        user.is_active = False
        user.save()
        token = user.generate_active_token()
        send_active_email.delay(email, user_name, token)
        return redirect(reverse('users:login'))


class ActiveView(View):
    # 邮件激活
    def get(self,request, token):
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            result = serializer.loads(token)
        except:
            return HttpResponse('激活链接已过期')

        user_id = result.get('confirm')
        try:
            user = User.objects.get(id = user_id)
        except:
            return HttpResponse('用户不存在')

        user.is_active = True

        user.save()
        return HttpResponse('已激活')


class LoginView(View):
    def get(self,request):
        return render(request, 'login.html')

    def post(self, request):
        user_name = request.POST.get('username')
        password = request.POST.get('pwd')
        if not all([user_name, password]):
            return redirect(reverse('user:login'))
        user = authenticate(username = user_name, password = password)

        if user is None:
            return render(request, 'login.html', {'errmsg': '用户名或密码错误'})
        if user.is_active is False:
            return render(request, 'login.html',{'errmsg': '不是激活账号'})

        remeber = request.POST.get('remember')
        login(request, user)

        if remeber != 'on':
            request.session.set_expiry(0)
        else:
            request.session.set_expiry(None)

        cart_json = request.COOKIES.get('cart')

        if cart_json is not None:
            cart_dict_cookie = json.loads(cart_json)
        else:
            cart_dict_cookie = {}

        redis_conn = get_redis_connection('default')

        user_id = request.user.id
        cart_dict_redis = redis_conn.hgetall('cart_%s'%user_id)

        for sku_id, count in cart_dict_cookie.items():
            sku_id = sku_id.encode()

            if sku_id in cart_dict_redis:
                origin_count = cart_dict_redis[sku_id]

                count += int(origin_count)

            cart_dict_redis[sku_id] = count

        if cart_dict_redis:

            redis_conn.hmset('cart_%s'%user_id, cart_dict_redis)
        next = request.GET.get('next')
        if next is None:
            response = redirect(reverse('goods:index'))
        else:
            response =  redirect(next)

        response.delete_cookie('cart')

        return response


class LoginoutView(View):
    def get(self, request):
        logout(request)

        return redirect(reverse('users:login'))


class AddressView(Login_required, View):
    def get(self,request):

        user = request.user

        try:
            address = Address.objects.filter(user=user).order_by('-create_time')[0]
        except:
            address = None

        content = {
            'address': address
        }

        return render(request, 'user_center_site.html', content)

    def post(self,request):
        user = request.user
        recv_name = request.POST.get('recv_name')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        recv_mobile = request.POST.get('recv_mobile')

        if all([recv_name, addr, zip_code, recv_mobile]):

            Address.objects.create(
                user = user,
                receiver_name = recv_name,
                detail_addr = addr,
                zip_code = zip_code,
                receiver_mobile = recv_mobile
            )

            user.save()
            return redirect(reverse('users:address'))


class UserinfoView(Login_required, View):

    def get(self, request):
        user = request.user

        try:
            address = user.address_set.latest('create_time')
        except:
            address = None

        redis_connection = get_redis_connection('default')
        sku_ids = redis_connection.lrange('history_%s' % user.id, 0, 4)
        skuList = []

        for sku_id in sku_ids:
            sku = GoodsSKU.objects.get(id=sku_id)
            skuList.append(sku)

        content = {
            'address': address,
            'skuList': skuList
        }

        return render(request, 'user_center_info.html', content)




