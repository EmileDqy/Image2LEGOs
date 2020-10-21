from PIL import Image as Image_loader
from tkinter import *
import io

def hexToRGB(h):
    return tuple(int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def getColorMap(csvFile):
    colors = {}
    with open(csvFile, 'r') as f:
        lines = f.readlines()
        for i in lines:
            id, name, hex = i.split(",")[:-1]
            colors[int(id)] = (*hexToRGB(hex), name, int(id))
    return colors

def nearest_colour( subjects, query ):
    return min( subjects, key = lambda subject: sum( (s - q) ** 2 for s, q in zip( subject, query ) ) )

def getResizedImage(img, basewidth):
    wpercent = (basewidth/float(img.size[0]))
    hsize = int((float(img.size[1])*float(wpercent)))
    return img.resize((basewidth,hsize), Image_loader.ANTIALIAS)

def create_circle(x, y, r, canvasName, color): #center coordinates, radius
    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    return canvasName.create_oval(x0, y0, x1, y1, fill="#"+rgb_to_hex(color))

def displayLego(img):
    window = Tk()
    r = 6
    w, h = 2*r*img.size[0], 2*r*img.size[1]
    window.geometry(f"{w}x{h}")
    myCanvas = Canvas(window, bg="black")
    myCanvas.pack(fill="both", expand=True)
    for y in range(img.size[1]):
        for x in range(img.size[0]):
            create_circle( x*2*r+r, y*2*r+r, r, myCanvas, img.getpixel((x,y)) )
    window.mainloop()

def getFinalImage(img_resized, lego_color_map):
    img = Image_loader.new( img_resized.mode, img_resized.size)
    pixels = img.load()
    pieces_list = {}
    for y in range(h):
        for x in range(w):
            color = img_resized.getpixel((x,y))
            lego_colors = lego_color_map.values()
            new_color_full = nearest_colour(lego_colors, color)
            new_color = tuple(new_color_full[:-2])
            if new_color_full[-2] not in pieces_list.keys():
                pieces_list[new_color_full[-2]] = [new_color_full[-1], 1]
            else:
                pieces_list[new_color_full[-2]][1] +=  1
            pixels[x, y] = new_color
    
    img.save("./lego.jpg")
    return img, pieces_list

def getParams():
    print("Hello, this program allows you to create a LEGO replica of your image.")
    print("The default width of the LEGO frame is : 3 squares (16x16 each).")
    print("The squares are the frame of the portrait :")
    print("---o---o---")
    print("|  |   |  |")
    print("---o---o---")
    print("|  |   |  |")
    print("---o---o---")
    print("|  |   |  |")
    print("---o---o---")
    print("|  |   |  |")
    print("---o---o---")
    print("<--width-->")
    print("The height is defined by the aspect-ratio of your image.")
    width = int(input("Please enter the number of squares (16x16) you want for your width : "))
    print("Your image has to be in the same folder as the program.")
    image = input("Please, enter the name of your image : ")
    print("Now, we need to give the color palette of the LEGO bricks you want to use.")
    print("By default there are two palettes : 16basics.csv & brownPalette.csv .")
    palette = input("Please, enter the name of you palette : ")
    print("Starting...")
    return width, image, palette


if __name__ == '__main__':
    
    width, image, palette = getParams()

    im = Image_loader.open(image)  
    size = im.size
    aspect_ratio = size[1]/size[0]
    width_base = width
    height_base = round(width_base*aspect_ratio)
    size_plate = 16
    lego_size = (width_base*size_plate, height_base*size_plate)
    
    lego_color_map = getColorMap(f"./colorMaps/{palette}")
    
    img_resized = getResizedImage(im, lego_size[0])
    img_resized = img_resized.resize((width_base*size_plate, height_base*size_plate))
    resized_size = w, h = img_resized.size

    img, pieces_list = getFinalImage(img_resized, lego_color_map)

    realSizeX, realSizeY = round(img.size[0]*0.7874,2), round(img.size[1]*0.7874,2)
    pieces_count = img.size[0]*img.size[1]
    price = pieces_count * 0.06

    try:
        with open("./pieces.csv", "w") as f:
            f.write(f"Real size (cm) :, {realSizeX} x {realSizeY}, soit :,{width_base} x {height_base},plaques de, 16 x 16.\n")
            f.write(f"Legos :, {pieces_count}\n")
            f.write(f"Estimated price :, ${price}\n")
            f.write("Type of bricks :, 1x1 plate round\n")
            f.write("\n")
            f.write("name, id, count\n")
            for key, value in zip(pieces_list.keys(), pieces_list.values()):
                f.write("%s, %s, %s\n" % (key, *value))
    except:
        print("Error : could not write the CSV file because it is already in use.") 

    displayLego(img)