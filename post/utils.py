from post.models import Image,  Post

def delete_post_images(post: Post):
    images = Image.objects.filter(post_id=post.id)
    for image in images:
        image.delete_file()
        image.delete()