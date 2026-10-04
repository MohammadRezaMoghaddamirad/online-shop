# config/spectacular.py

TAG_MAPPING = [
    ('accounts/profile/', 'Profile'),
    ('accounts/users/',   'Users'),
    ('auth/',             'Auth'),
    ('categories/',       'Categories'),
    ('products/',         'Products'),
    ('carts/',            'Carts'),
    ('coupons/',          'Coupons'),
    ('orders/',           'Orders'),
]


def custom_postprocessing_hook(result, generator, request, public):
    """اضافه کردن tag به هر operation بر اساس مسیر URL"""
    paths = result.get('paths', {})

    matched = 0
    unmatched = []

    for path, methods in paths.items():
        # نرمال‌سازی: حذف اسلش ابتدایی
        normalized = path.lstrip('/')

        tag = None
        for prefix, t in TAG_MAPPING:
            if normalized.startswith(prefix):
                tag = t
                break

        if not tag:
            unmatched.append(path)
            continue

        matched += 1
        for method, operation in methods.items():
            if method in ('get', 'post', 'put', 'patch', 'delete', 'head', 'options'):
                operation['tags'] = [tag]

    print(f"🔥 Matched: {matched} / {len(paths)}")
    if unmatched:
        print(f"⚠️ Unmatched paths ({len(unmatched)}):")
        for p in unmatched:
            print(f"   '{p}'")

    return result