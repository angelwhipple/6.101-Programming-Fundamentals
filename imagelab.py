#!/usr/bin/env python3

import math
from PIL import Image


def get_pixel(image, x, y, boundary_behavior = 'None'):
    width, height = image['width'], image['height']
    if x in range(width) and y in range(height):
        return image['pixels'][y*image['width']+x]
    else:
        x1, y1 = x, y
        if boundary_behavior == 'zero':
           return 0
        elif boundary_behavior == 'extend':
            if x >= width:
                x1 = width-1
            elif x < 0:
                x1 = 0
            else:
                x1 = x
            if y >= height:
                y1 = height-1
            elif y < 0:
                y1 = 0
            else:
                y1 = y
        elif boundary_behavior == 'wrap': 
            if x >= width:
                x1 = x-width
            elif x < 0:
                x1 = width+x
            else:
                x1 = x1
            if y >= height:
                y1 = y-height
            elif y < 0:
                y1 = height+y
            else:
                y1 = y1
        else:
            return None
        return image['pixels'][y1*image['width']+x1]

def set_pixel(image, x, y, c):
    image['pixels'][y*image['width']+x] = c
    
def apply_per_pixel(image, func):
    result = { 'height': image['height'], 
              'width': image['width'], 
              'pixels': [0]*len(image['pixels']) }
    
    for y in range((image['height'])):
        for x in range((image['width'])):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)
    return result

def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c)

def create_matrix(image, deg, x, y, boundary_behavior):
    """
    Constructs nxn matrix, n = degree of correlation kernel, centered at x, y. 
    Fills matrix with values from original input image, unless index is out of 
    scope; then get_pixel is applied with chosen boundary_behavior
    
    Does not mutate input image, and returns pixel matrix as a list of ints.

    """
    # Defining step as max dist away from center
    pix, i, step = [0]*(deg**2), 0, deg//2
    # Moving vertically from center
    for h in range(y-step, y+step+1):
        # Moving horizontally from center
        for w in range(x-step, x+step+1):
            pix[i] = get_pixel(image, w, h, boundary_behavior)
            i += 1
    return pix   
    
def create_box(n):
    kernel = [0]*(n**2)
    for i in range(len(kernel)):
        kernel[i] = 1/len(kernel)
    return kernel

def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings 'zero', 'extend', or 'wrap',
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of 'zero', 'extend', or 'wrap', return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with 'height', 'width', and 'pixels' keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    KERNEL REPRESENTATION: list of floats where each index = a kernel weight
    """
    result = { 'height': image['height'], 
              'width': image['width'], 
              'pixels':[0]*len(image['pixels']) }
    # kernel side length
    deg = int(math.sqrt(len(kernel)))
    
    for y in range(image['height']):
        for x in range(image['width']):
            matrix = create_matrix(image, deg, x, y, boundary_behavior)
            # Store weighted pixel value as sum of a list comprehension
            val = sum(weight*pix for weight, pix in list(zip(kernel, matrix)))
            set_pixel(result, x, y, val)
    return result

def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    for i in range(len(image['pixels'])):
        image['pixels'][i] = round(image['pixels'][i])
        if image['pixels'][i] > 255:
            image['pixels'][i] = 255
        if image['pixels'][i] < 0:
            image['pixels'][i] = 0
    return image

def edges(image):
    """
    Return a new image where each pixel the result of square rooting sum of 
    squares of the corresponding pixels in each of two new images, generated 
    by correlating the input image with two distinct kernels. 

    Does not mutate input image, but creates a separate structure to 
    represent the sharpened output.
    """
    output = { 
        'height': image['height'],
        'width': image['width'],
        'pixels': [0]*len(image['pixels'])
        }
    kx, ky = [-1, 0, 1, -2, 0, 2, -1, 0, 1], [-1, -2, -1, 0, 0, 0, 1, 2, 1]
    imx, imy = correlate(image, kx, 'extend'), correlate(image, ky, 'extend')
    for i in range(len(output['pixels'])):
        output['pixels'][i] = round(math.sqrt(imx['pixels'][i]**2+imy['pixels'][i]**2))
    return round_and_clip_image(output)
    
# FILTERS

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    kernel = create_box(n)

    # then compute the correlation of the input image with that kernel
    result = correlate(image, kernel, 'extend')

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    return round_and_clip_image(result)

def sharpened(image, n):
    """
    Return a new image representing the result of substracting a blurred version 
    of image from a scaled version of the original image.

    Does not mutate input image, but creates a separate structure to 
    represent the sharpened output.
    """
    blurry, sharp = blurred(image, n), { 
        'height': image['height'],
        'width': image['width'],
        'pixels': [0]*len(image['pixels'])
        }
    for i in range(len(image['pixels'])):
        sharp['pixels'][i] = 2*image['pixels'][i] - blurry['pixels'][i]
    return round_and_clip_image(sharp)


# VARIOUS FILTERS


def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def color(im):
        rgb = []
        for i in range(3):
            c = { 'height': im['height'],
               'width': im['width'],
               'pixels': [ im['pixels'][n][i] for n in range(len(im['pixels'])) ]
            }
            filtered = filt(c)
            rgb.append(filtered['pixels'])
        res = { 'height': im['height'],
              'width': im['width'],
              'pixels': [ (r, g, b) for r, g, b in list(zip(rgb[0], rgb[1], rgb[2])) ]
        }
        return res
    return color


def make_blur_filter(n):
    kernel = create_box(n)
    def blur(im):
        res = correlate(im, kernel, 'extend')
        return round_and_clip_image(res)
    return blur


def make_sharpen_filter(n):
    def sharp(im):
        blurred, sharpened = make_blur_filter(n)(im), { 
            'height': im['height'],
            'width': im['width'],
            'pixels': [0]*len(im['pixels'])
            }
        for i in range(len(im['pixels'])):
            sharpened['pixels'][i] = 2*im['pixels'][i] - blurred['pixels'][i]
        return round_and_clip_image(sharpened)
    return sharp

def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def cascade(im):
        out = im
        for f in filters:
            out = f(out)
        return out
    return cascade


# SEAM CARVING

# Main Seam Carving Implementation


def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image. Returns a new image.
    """
    res, n = { 'height': image['height'],
           'width': image['width'],
           'pixels': image['pixels'].copy() }, 0
    while n < ncols:
        grey = greyscale_image_from_color_image(res)
        energy = compute_energy(grey)
        cum_energy = cumulative_energy_map(energy)
        seam = minimum_energy_seam(cum_energy)
        res = image_without_seam(res, seam)
        n += 1
    return res


# Optional Helper Functions for Seam Carving


def greyscale_image_from_color_image(image): 
    """
    Given a color image, computes and returns a corresponding greyscale image.
    Returns a greyscale image (represented as a dictionary).
    """
    def convert(pix):
        res = []
        for p in pix:
            res.append(round(0.299*p[0] + 0.587*p[1] + 0.114*p[2]))
        return res
    grey = { 'height': image['height'],
            'width': image['width'],
            'pixels': convert(image['pixels'])
        }
    return grey
    

def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)


# Helper function 
def get_adj_pixels(i, width, energies):
    """
    Given an index i and an array of pixel energies, finds pixels top 
    adjacent to pixel at index i within the array.

    Returns a dict of two lists, one with pixel energies & one with indices.
    """
    pixels, indices = [], []
    # cases for edge of energy array
    if i % width == 0:
        pixels.extend([energies[i-width], energies[i-width+1]])
        indices.extend([(i-width), (i-width+1)])
    elif (i+1) % width == 0:
        pixels.extend([energies[i-width-1], energies[i-width]])
        indices.extend([(i-width-1), (i-width)])
    else:
        pixels.extend([energies[i-width-1], energies[i-width], \
                       energies[i-width+1]])
        indices.extend([(i-width-1), (i-width), (i-width+1)])
    return { 'pixels': pixels,
         'indices': indices
        }


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy
    function), computes a "cumulative energy map" as described in the lab 2
    writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    res = { 'height': energy['height'],
            'width': energy['width'],
            'pixels': energy['pixels']
            }
    width, energies = res['width'], res['pixels']
    # start from row 2, pixel energy at index i + min of adj pixel energies
    for i in range(width, len(res['pixels'])):
            res['pixels'][i] = res['pixels'][i] + min(get_adj_pixels(i, width, energies)['pixels'])
    return res
        

def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    seam, rows, start, end = [], cem['height'], len(cem['pixels'])-cem['width'], len(cem['pixels'])
    low = start
    for i in range(start, end):
        if cem['pixels'][i] < cem['pixels'][low]:
            low = i
    seam.append(low)
    for j in range(rows-1):
        adj = get_adj_pixels(seam[-1], cem['width'], cem['pixels'])
        next_low = min(adj['pixels'])
        seam.append(cem['pixels'].index(next_low, adj['indices'][0]))
    return seam
    


def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    # new width = (original width - 1), path/column removal
    res = { 'height': image['height'],
           'width': image['width']-1,
           'pixels': image['pixels']
        }
    # seam = list of large -> small indices, can use .pop()
    for i in seam:
        res['pixels'].pop(i)
    return res


# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img = img.convert("RGB")  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {"height": h, "width": w, "pixels": pixels}


def save_color_image(image, filename, mode="PNG"):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode="RGB", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError("Unsupported image mode: %r" % img.mode)
        w, h = img.size
        return {"height": h, "width": w, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    # cat, invert_color = load_color_image('test_images/cat.png'), color_filter_from_greyscale_filter(inverted)
    # inverted_cat = save_color_image(invert_color(cat), 'inverted_cat.png')
    
    # python = load_color_image('test_images/python.png')
    # blur_color = color_filter_from_greyscale_filter(make_blur_filter(9))
    # blurry_python = save_color_image(blur_color(python), 'blurry_python.png')
    
    # sparrowchick = load_color_image('test_images/sparrowchick.png')
    # sharpen_color = color_filter_from_greyscale_filter(make_sharpen_filter(7))
    # sharp_sparrowchick = save_color_image(sharpen_color(sparrowchick), 'sharp_sparrowchick.png')
    
    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])
    # frog = load_color_image('test_images/frog.png')
    # cascade_frog = save_color_image(filt(frog), 'cascade_frog.png')
    
    # pattern = load_color_image('test_images/pattern.png')
    # grey_pattern = greyscale_image_from_color_image(pattern)
    # pattern_energy = compute_energy(grey_pattern)
    # save_greyscale_image(pattern_energy, 'pattern_energy.png')
    # cum_energy_map = cumulative_energy_map(pattern_energy)
    # save_color_image(cum_energy_map, 'cum_energy_map.png')
    # seam = minimum_energy_seam(cum_energy_map)
    # result_pattern = image_without_seam(pattern, seam)
    # save_color_image(result_pattern, 'result_pattern.png')
    
    twocats = load_color_image('test_images/twocats.png')
    seamed_twocats = save_color_image(seam_carving(twocats, 100), 'seamed_twocats.png')
    
    
    
