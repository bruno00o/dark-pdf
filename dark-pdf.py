import PyPDF2
import requests
from PIL import Image
import PIL.ImageOps
import glob, sys, fitz
import os

# To get better resolution
zoom_x = 2.0  # horizontal zoom
zoom_y = 2.0  # vertical zoom
mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension

def downloadFile(url):
    file = requests.get(url, stream=True)
    with open("./src/file.pdf", "wb") as f:
        f.write(file.content)
    return f.name

def pdfToImages(pdf):
    glob.glob(pdf)
    doc = fitz.open(pdf)
    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        output = "./src/render/page-%i.png" % page.number
        pix.save(output)

def invertImage(image):
    img = Image.open(image)
    inverted_image = PIL.ImageOps.invert(img)
    inverted_image.save(image)

def imagesToPdf(images):
    path = "./src/render/"
    images_list = []
    for image in images:
        image = path + image
        img = Image.open(image)
        img_convert = img.convert("RGB")
        images_list.append(img_convert)
    images_list[0].save("./src/output.pdf", save_all=True, append_images=images_list[1:])

def main():
    url = ""
    f = downloadFile(url)
    pdfToImages(f)
    for image in glob.glob("./src/render/*.png"):
        invertImage(image)
    imagesToPdf(os.listdir("./src/render/"))
    os.system("rm ./src/render/*.png")

if __name__ == "__main__":
    main()