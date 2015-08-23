import functools

from django.shortcuts import redirect


def no_login_required(redirect_url):
    def func_wrapper(view):
        @functools.wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.user.is_authenticated:
                return redirect(redirect_url)
            return view(request, *args, **kwargs)
        return wrapped
    return func_wrapper
