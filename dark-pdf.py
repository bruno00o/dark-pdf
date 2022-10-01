import requests
from PIL import Image
import PIL.ImageOps
import glob
import sys
import fitz
import os
import json
import ftplib

NOTION_KEY = ""
NOTION_DATABASE_ID = ""

FTP_ADRESS = ""
FTP_USER = ""
FTP_PASS = ""
SERVER_URL = ""

# To get better resolution
zoom_x = 4.0  # horizontal zoom
zoom_y = 4.0  # vertical zoom
mat = fitz.Matrix(zoom_x, zoom_y)  # zoom factor 2 in each dimension


def downloadFile(url):
    file_name = url.split("/")[-1]
    file = requests.get(url, stream=True)
    if not os.path.exists("./src"):
        os.mkdir("./src")
    with open("./src/" + file_name, "wb") as f:
        f.write(file.content)
    return f.name


def pdfToImages(pdf):
    glob.glob(pdf)
    doc = fitz.open(pdf)
    if not os.path.exists("./src/render"):
        os.mkdir("./src/render")
    for page in doc:
        pix = page.get_pixmap(matrix=mat)
        output = "./src/render/page-%i.png" % page.number
        pix.save(output)


def invertImage(image):
    img = Image.open(image)
    inverted_image = PIL.ImageOps.invert(img)
    inverted_image.save(image)


def imagesToPdf(images, file_name):
    path = "./src/render/"
    images_list = []
    for image in images:
        image = path + image
        img = Image.open(image)
        img_convert = img.convert("RGB")
        images_list.append(img_convert)
    images_list[0].save(file_name[:-4] + "_dark.pdf",
                        save_all=True, append_images=images_list[1:])


def uploadFile(file):
    session = ftplib.FTP(FTP_ADRESS, FTP_USER, FTP_PASS)
    file = open(file, 'rb')
    file_name = file.name.split("/")[-1]
    session.storbinary('STOR ' + file_name, file)
    file.close()
    session.quit()
    print("File uploaded to server")


def saveToNotion(file_name):
    file_url = SERVER_URL + file_name
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": "Bearer " + NOTION_KEY,
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    data = {
        "parent": {
            "type": "database_id",
            "database_id": NOTION_DATABASE_ID
        },
        "properties": {
            "title": {
                "title": [
                    {
                        "text": {
                            "content": file_name
                        }
                    }
                ]
            },
            "URL": {
                "url": file_url
            }
        }
    }
    r = requests.post(url, headers=headers, data=json.dumps(data))
    if r.status_code == 200:
        print("File saved to Notion")
    else:
        print("Error: " + str(r.status_code))


def main():
    url = input("Enter the url of the pdf: ")
    f = downloadFile(url)
    pdfToImages(f)
    for image in glob.glob("./src/render/*.png"):
        invertImage(image)
    imagesToPdf(os.listdir("./src/render/"), f)
    os.system("rm ./src/render/*.png")
    print("Path: " + os.getcwd() + "/" + f[:-4] + "_dark.pdf")
    uploadFile(f[:-4] + "_dark.pdf")
    file_name = (f[:-4] + "_dark.pdf").split("/")[-1]
    saveToNotion(file_name)


if __name__ == "__main__":
    main()
