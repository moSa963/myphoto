from posts.models import Post, PostImage, PostLike
from PIL import Image
from io import BytesIO

def getMediaRoot() ->str:
    return 'media/test'
    
def createImage() -> BytesIO:
    image = Image.new('RGB', (100, 100), color = 'red')
    image_io = BytesIO()
    image.save(image_io, format='JPEG')
    image_io.seek(0)
    
    return image_io
    
def addImageToPost(post: Post) -> PostImage:
    image = PostImage(post=post)
    image_io = createImage()
    
    image.image.save("test.jpg", image_io)
    image.save()
    
    return image
    
def createPost(user, title, private=False) -> Post:
    post = Post.objects.create(user=user, title=title, private=private)

    addImageToPost(post)
    
    return post

def like_post(user, post):
    
    like = PostLike.objects.create(
        user=user,
        post=post
    )
    
    return like