

def form_autofocus(field):
    def wrapper(cls):
        original_init = cls.__init__

        def __init__(self, *args, **kwargs):
            original_init(self, *args, **kwargs)
            self.fields[field].widget.attrs['autofocus'] = 'autofocus'

        cls.__init__ = __init__
        return cls

    return wrapper
