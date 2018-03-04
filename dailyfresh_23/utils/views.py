from django.contrib.auth.decorators import login_required


class Login_required(object):

    @classmethod
    def as_view(cls, **initkwargs):

        view = super().as_view(**initkwargs)

        return login_required(view)