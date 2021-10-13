"""
    Prints a string of text onto an image file.

    It puts it in a little box over there on the lower right corner.

    TODO: change the code that finds color for text.
    Sometimes it's not contrasty enough.
"""
import os
import cv2
from PIL import Image, ImageFont, ImageDraw
import numpy as np

fonts = 'C:/Windows/Fonts/'
font = ImageFont.truetype(fonts + 'arial.ttf', 16)


def get_colors(filename):
    """
        Find the dominant color in the image and use that for the background.
        Then find a complementary color and use that as the text color.
    """
    image = cv2.imread(filename)
    pixels = np.float32(image.reshape(-1, 3))
    n_colors = 5
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)
    #print(counts)
    dominant = palette[np.argmax(counts)]

    # Note BGR -> RGB
    box_color = (int(dominant[2]), int(dominant[1]), int(dominant[0]))
    text_color = (int(255-dominant[2]), int(255-dominant[1]), int(255-dominant[0]))

    return (box_color, text_color)


def get_target(file, extn, output_folder):
    """ Find an unused output file name. """
    outfile = os.path.join(output_folder, file + extn)
    n = 1
    while os.path.exists(outfile):
        outfile = os.path.join(output_folder, file + "(%s)" % n + extn)
        n += 1
    return outfile


def watermark(input_name, output_folder, textmark):
    """ 
        Print the string in "textmark" onto a copy of input_image. 
        Writes the new image to "output_folder".
        The name of the output file will be the same unless there's already a file there
        in which case it does the numbered suffix thing (eg "myfile.jpg" -> "myfile(3).jpg")
    """
    (path, filename) = os.path.split(input_name)
    (file, extn) = os.path.splitext(filename)

    base = Image.open(input_name) # .convert('RGBA')
    xmax, ymax = base.size

    # find text image size
    # Remember output box is rotated 90 degrees
    bbox = font.getbbox(textmark)
    txt_xmax = min(bbox[2] + 4, ymax)
    txt_ymax = min(20, xmax)

# Use only the text area to find
# a suitable background color 
# but I like when it looks at the whole image... can't decide.
    use_bbox = True
    if use_bbox:
        tmpfile = os.path.join(output_folder, file + '.TEMP' + extn)

        titlebar = base.crop((xmax - txt_ymax,ymax - txt_xmax, xmax,ymax))
        titlebar.save(tmpfile)
        (box_color, text_color) = get_colors(tmpfile)
        os.unlink(tmpfile)
    else:
        (box_color, text_color) = get_colors(input_name)

    dest = (xmax-txt_ymax, ymax-txt_xmax)
    txt = Image.new("RGB", [txt_xmax,txt_ymax])
    d = ImageDraw.Draw(txt)

    # make a filled rectangle in the correct colors
    d.rectangle([0,0, txt_xmax,txt_ymax], fill=box_color, outline=None, width=1)
    d.text((2,0), text=textmark, fill=text_color, font=font)

    twisted = txt.transpose(Image.ROTATE_90)

    # At this point I could getsize the font bbox and crop it out
    # but I like the way a solid bar looks.

    base.paste(twisted, box=dest)

    # Don't overwrite an existing file.
    outfile = get_target(file, extn, output_folder)
    base.convert('RGB').save(outfile)
    return outfile


if __name__ == "__main__":

    # This is unit test code
    #
    # It pulls all images from your Enterprise Portal and watermarks them
    # It pulls all images from your "pictures" folder and watermarks them
    # It makes copies into C:\TEMP so the originals are undisturbed.

    # NOTE I only need arcgis for the unit test, but
    # there is a bug in arcgis that causes it to screw up datetime
    # # if you switch these two lines.
    from arcgis.gis import GIS
    from datetime import datetime
    from config import Config

    def download_images():
        """ Iterate the Portal for images.
            Download each into workspace. 
            Note that there is no way to set the workspace in the API.
            Yield a filename. """
        # Pull from Portal
        portal = GIS(Config.ARCGIS_URL + '/portal', Config.ARCGIS_USER, Config.ARCGIS_PASSWORD)
        print("Logged in as " + str(portal.properties.user.username))
        imageList = portal.content.search(query="", item_type="Image")
        for item in imageList:
            #print(item.title, item.owner, item.ownerFolder)
            image_item = portal.content.get(item.id)
            imgfile = image_item.get_data()
            yield(imgfile)

    # Collect the information we'll put in a comment string.
    cwd,scriptname = os.path.split(__file__)
    datestamp = datetime.now().strftime("%Y%m%d %H%M")
    textmark = 'updated ' + datestamp + ' by ' + scriptname
    scratch_workspace = "C:\\TEMP"

    for imgfile in download_images():
        try:
            outfile = watermark(imgfile, scratch_workspace, textmark)
            print(outfile)
        except Exception as e:
            print("Failed!", e)

    # Pull from your Pictures folder
    srcdir = os.path.join(os.environ.get('USERPROFILE'), "Pictures")
    for item in os.listdir(srcdir):
        print(item)
        imgfile = os.path.join(srcdir, item)

        try:
            # Possibly test to see if the image is an animated GIF
            # or really tiny
            # but not necessary as
            # we just catch these as exceptions here.
#            base = Image.open(input_name)
#            xmax, ymax = base.size
#            if ymax < 20: return
#            if base.is_animated:
#                return
            outfile = watermark(imgfile, scratch_workspace, textmark)
            print(outfile)
        except Exception as e:
            print("Failed!", e)

# That's all!
