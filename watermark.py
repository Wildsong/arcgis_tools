"""
    Prints a string of text onto a photograph.

"""
import cv2
import numpy as np
import math

def watermark(input_name, output_name, text, color=(0,0,0, 0)):
    """ 
        Print the string in "text" onto a copy of input_image. 
        Writes the new image to "output_name" and returns an image object.
    """
    image = cv2.imread(input_name)

    # Scale the thumbnail up, 
    # write on it, 
    # shrink it back down.

    # https://docs.opencv.org/master/d6/d6e/group__imgproc__draw.html
    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 2.2
    thickness = 5
    lineType = cv2.LINE_8
    bottomLeftOrigin = False
    original_shape = image.shape
    origin = (15, 720 - 20)

    image = cv2.resize(image, (1280,720))

    """
    I'd like to find the dominant color in the image and use that for the background
    Then I'd like to find the complementary color in HSV space and use that as the text color

        pixels = np.float32(image.reshape(-1, 3))

        n_colors = 5
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
        flags = cv2.KMEANS_RANDOM_CENTERS

        _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
        _, counts = np.unique(labels, return_counts=True)
        print(counts)


        dominant = palette[np.argmax(counts)]

        d1 = cv2.hsv(dominant)
        d = math.min(d1,180-d1) # correct distance if cross 0deg . full circle at 180 because of Hue scaling
        c = cv2.bgr(d)
    """
    c = (255,255,255,255)

    # Put the text on a contrasting rectangle so it's visible (and so it erases any previous string)
    image_rect = cv2.rectangle(image, (0,719), (925,720-80), color=(int(c[0]),int(c[1]),int(c[2])), thickness=-1)
    image_txt = cv2.putText(image_rect, text, origin, font, fontScale, color, thickness, lineType, bottomLeftOrigin)

    # Shrink back to the original size.
    final = cv2.resize(image_txt, (original_shape[1], original_shape[0]))
    cv2.imwrite(output_name, final)

    return final


if __name__ == "__main__":
    import os
    from datetime import datetime

    # Collect the information we'll put in a comment string.
    cwd,name = os.path.split(__file__)

    datestamp = datetime.now().strftime("%H:%M %m/%d/%y")
    mark = 'updated ' + datestamp

    inputfile = "thumbnail.jpg"
    assert os.path.exists(inputfile)

    img = watermark(inputfile, "thumbnail_marked.jpg", mark)

    cv2.imshow("Text Image", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# That's all!
