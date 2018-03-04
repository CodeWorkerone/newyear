from celery import Celery
from django.core.mail import send_mail
from django.conf import settings
from goods.models import GoodsSKU, Goods, GoodsCategory, IndexGoodsBanner, IndexPromotionBanner,IndexCategoryGoodsBanner
from django.template import loader
import os

# 创建celery运行对象

app = Celery('celery_tasks.tasks', broker='redis://192.168.236.128:6379/5')

@app.task
def send_active_email(to_email, user_name, token):
    """发送激活邮件"""

    subject = "天天生鲜用户激活"  # 标题
    body = ""  # 文本邮件体
    sender = settings.EMAIL_FROM  # 发件人
    receiver = [to_email]  # 接收人
    html_body = '<h1>尊敬的用户 %s, 感谢您注册天天生鲜！</h1>' \
                '<br/><p>请点击此链接激活您的帐号<a href="http://127.0.0.1:8000/users/active/%s">' \
                'http://127.0.0.1:8000/users/active/%s</a></p>' % (user_name, token, token)
    send_mail(subject, body, sender, receiver, html_message=html_body)

@app.task
def generate_static_index_html():
    categorys = GoodsCategory.objects.all()
    banners = IndexGoodsBanner.objects.all().order_by('index')
    promotion_banners = IndexPromotionBanner.objects.all().order_by('index')

    for category in categorys:

        title_banners = IndexCategoryGoodsBanner.objects.filter(category = category, display_type= 0).order_by('index')
        category.title_banner = title_banners

        img_banners = IndexCategoryGoodsBanner.objects.filter(category = category, display_type= 1).order_by('index')
        category.img_banner = img_banners

    cart_num = 0
    context = {
        'categorys': categorys,
        'banners': banners,
        'promotion_banners': promotion_banners,
        'cart_num': cart_num
    }

    template = loader.get_template('static_index.html')
    html_data = template.render(context)

    file_path = os.path.join(settings.STATICFILES_DIRS[0], 'index.html')

    with open(file_path, 'w') as file:
        file.write(html_data)

