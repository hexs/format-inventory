import os
import urllib.request
import cv2
import pandas as pd
import math
import shutil
from PIL import Image


def max_return_0(max, v):
    return 0 if v > max else v


def to_a4(img1, img2, img3, img4, img5, img6):
    r1 = cv2.hconcat([img1, img2])
    r2 = cv2.hconcat([img3, img4])
    r3 = cv2.hconcat([img5, img6])
    img_a4 = cv2.vconcat([r1, r2, r3])
    return img_a4


def grid_img(x):
    x = x - 1
    img = cv2.imread('for A4.jpg')
    if x == -1:
        return img

    part_no = df.loc[x, 'PART NO.']
    part_name = df.loc[x, 'PART NAME']
    qty = df.loc[x, "Q'TY"]
    name_of_counting = df.loc[x, "NAME"]
    item = df.loc[x, "ITEM"]

    img = cv2.putText(img, part_no, (376, 301), 1, 3.7, (0, 0, 0), 3)
    img = cv2.putText(img, part_name, (376, 544), 1, 3.0, (0, 0, 0), 3)
    img = cv2.putText(img, f'{qty}', (376, 787), 1, 3.7, (0, 0, 0), 3)
    img = cv2.putText(img, f'{name_of_counting}', (376, 1031), 1, 3.7, (0, 0, 0), 3)
    img = cv2.putText(img, f'{item}', (1031, 151), 1, 3.7, (0, 0, 0), 3)

    return img


def images_to_pdf(image_folder, output_pdf):
    images = [file for file in os.listdir(image_folder) if file.endswith(('jpg'))]
    images.sort()

    first_image = Image.open(os.path.join(image_folder, images[0]))

    image_objects = []
    for image in images[1:]:
        img = Image.open(os.path.join(image_folder, image))
        if img.mode != 'RGB':
            img = img.convert('RGB')
        image_objects.append(img)

    first_image.save(output_pdf, save_all=True, append_images=image_objects)


if __name__ == '__main__':
    list_dir = os.listdir()

    if 'format_inventory.csv' not in list_dir:
        data = {
            'ITEM': [62, 63],
            'PART NO.': ['QC2-xxxx', 'VC9-xxxx'],
            'PART NAME': ['FABRIC SHEET CARD M82', 'AL CAPACITOR'],
            "Q'TY": [2, 2],
            'NAME': ['Mr.A', 'Mr.B']
        }
        df = pd.DataFrame(data)

        df.to_csv('format_inventory.csv', index=False)
        exit()
    import urllib.request

    if "for A4.jpg" not in list_dir:
        print('download for A4.jpg')
        url = "https://raw.githubusercontent.com/hexs/format-inventory/main/for%20A4.jpg"
        filename = "for A4.jpg"
        proxy_handler = urllib.request.ProxyHandler({
            'http': 'http://150.61.8.70:10080',
            'https': 'http://150.61.8.70:10080'
        })
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, filename)

    if 'page' in list_dir:
        shutil.rmtree(os.path.join('page'))
    os.mkdir('page')

    df = pd.read_csv('format_inventory.csv')
    len_df = len(df)
    page = math.ceil(len(df) / 6)

    print(df)
    print(f'len_df = {len_df}')
    print(f'page = {page}')

    for i in range(1, page + 1):
        series = [
            max_return_0(len_df, page * 1 + i), max_return_0(len_df, page * 0 + i),
            max_return_0(len_df, page * 3 + i), max_return_0(len_df, page * 2 + i),
            max_return_0(len_df, page * 5 + i), max_return_0(len_df, page * 4 + i)
        ]
        print(f'page {i} {series}')

        ia4 = to_a4(
            grid_img(max_return_0(len_df, page * 1 + i)), grid_img(max_return_0(len_df, page * 0 + i)),
            grid_img(max_return_0(len_df, page * 3 + i)), grid_img(max_return_0(len_df, page * 2 + i)),
            grid_img(max_return_0(len_df, page * 5 + i)), grid_img(max_return_0(len_df, page * 4 + i))
        )
        cv2.imwrite(f'page/{i:03}.jpg', ia4)

    images_to_pdf("page", "output.pdf")
