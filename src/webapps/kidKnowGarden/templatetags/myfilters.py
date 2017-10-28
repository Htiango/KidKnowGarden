from django import template

register = template.Library()


@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})


@register.filter(name='add_class_placeholder')
def add_class_placeholder(value, arg):
    return value.as_widget(attrs={'class': arg, 'placeholder': value.label})


@register.filter(name='add_class_placeholder_divide')
def add_class_placeholder_divide(value, arg):
    args = arg.split('||')
    arg1 = args[0]
    arg2 = args[1]
    return value.as_widget(attrs={'class': arg1, 'placeholder': arg2})


@register.filter(name='lookup')
def lookup(value, key):
    print('------------------------------' + str(value.get(key, [])))
    return value.get(key, [])
