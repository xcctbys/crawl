#coding=utf-8


from cStringIO import StringIO
try:
    from PIL import Image, ImageEnhance
except:
    pass


LEFT_TOP     = 'lt'
LEFT_BOTTOM  = 'lb'
RIGHT_TOP    = 'rt'
RIGHT_BOTTOM = 'rb'
CENTER = "ct"

WIDTH_GRID = 30.0
HIGHT_GRID = 30.0


def mark_layout(im, mark, layout=RIGHT_BOTTOM):
    im_width, im_hight     = im.size[0], im.size[1]
    mark_width, mark_hight = mark.size[0], mark.size[1]

    coordinates = { 
        LEFT_TOP: (int(im_width/WIDTH_GRID),int(im_hight/HIGHT_GRID)),
        LEFT_BOTTOM: (int(im_width/WIDTH_GRID), int(im_hight - mark_hight - im_hight/HIGHT_GRID)),
        RIGHT_TOP: (int(im_width - mark_width - im_width/WIDTH_GRID), int(im_hight/HIGHT_GRID)),
        RIGHT_BOTTOM: (int(im_width - mark_width - im_width/WIDTH_GRID), int(im_hight - mark_hight - im_hight/HIGHT_GRID)),
        CENTER:((im_width-mark_width)/2, (im_hight-mark_hight)/2),
    }
    return coordinates[layout]


def reduce_opacity(mark, opacity):
    assert opacity >= 0 and opacity <= 1
    mark  = mark.convert('RGBA') if mark.mode != 'RGBA' else mark.copy()
    alpha = mark.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    mark.putalpha(alpha)
    return mark


def water_mark(img, mark, opacity=1):
    """give water mark in image
    Args:
        img: from post data, Image object
        mark: water mark image, Image object
    """
    if not mark:
        return img
    
    mark = mark.rotate(15, resample=Image.BICUBIC)
    mark.thumbnail((img.size[0]/4, img.size[1]/4))
    
    if opacity < 1:
        mark = reduce_opacity(mark, opacity)
    
    if img.mode != 'RGBA':
        img = img.convert('RGBA')
        img_format = 'JPEG'
    else:
        img_format = 'PNG'

    layer = Image.new('RGBA', img.size, (0,0,0,0))
    layer.paste(mark, mark_layout(img, mark, CENTER))

    img = Image.composite(layer, img, layer)

    new_img = StringIO()
    img.save(new_img, img_format, quality=100)

    return new_img.getvalue()