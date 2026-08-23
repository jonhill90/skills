from utils.slugify import to_slug


def post_url(post):
    return f"/posts/{to_slug(post['title'])}"
