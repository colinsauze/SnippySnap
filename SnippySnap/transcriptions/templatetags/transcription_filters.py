from django import template


register = template.Library()

@register.filter(name='get_title_case')
def get_title_case(str):
    return str.title().replace('_', ' ')

@register.filter(name='get_authentication_html')
def get_authentication_html(username, next):
    if username:
        return 'logged in as ' + username + '<br/><a href="/logout?next=/transcriptions">logout</a>'
    else:
        return '<a href="/login?next=' + next + '">login</a>'

@register.filter(name='get_range')
def get_range(value):
    return range(value+1)[1:]

@register.filter(name='get_offset')
def get_offset(i, page_size):
    return (i-1)*page_size

@register.filter(name='get_row_class')
def get_row_class(value):
    if value%2 == 1:
        return 'odd'
    return ''

# @register.filter(name='get_data_value')
# def get_data_value(data, key_data):
#     try:
#         key = key_data['id']
#     except:
#         key = key_data
#
#     key_list = key.split('__')
#     t = data
#     for k in key_list:
#         t = getattr(t, k)
#     value = t
#     if value is None:
#         value = ''
#     return value
#

#
# @register.filter(name='get_id_field')
# def get_id_field(field):
#     try:
#         id = field['id']
#     except:
#         id = field
#     return id
#
# @register.filter(name='get_display_field')
# def get_display_field(field):
#     try:
#         label = field['label']
#     except:
#         try:
#             label = field.title()
#         except:
#             label = field['id'].title()
#     return label
#
# @register.filter(name='get_search_field')
# def get_search_field(field):
#     try:
#         search = field['search']
#     except:
#         try:
#             search = field['id']
#         except:
#             search = field
#     return search
#
# @register.filter(name='reverse_concat')
# def reverse_concat(arg1, arg2):
#     """concatenate arg1 & arg2"""
#     return str(arg2) + str(arg1)
#
