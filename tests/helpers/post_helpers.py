from posts.models import Post, PostImage
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
    
def createPost(user, title) -> Post:
    post = Post.objects.create(user=user, title=title, private=False)

    addImageToPost(post)
    
    return post