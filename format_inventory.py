import os
import urllib.request
import cv2
import pandas as pd
import math
import shutil
from PIL import Image


def safe_get(value, default=""):
    return str(value) if pd.notna(value) else default


def max_return_0(max, v):
    return 0 if v > max else v


def to_a4(*images):
    rows = [cv2.hconcat(images[i:i + 2]) for i in range(0, 6, 2)]
    return cv2.vconcat(rows)


def grid_img(x, df, template_img):
    if x == 0:
        return template_img.copy()

    row = df.iloc[x - 1]
    img = template_img.copy()

    text_params = [
        (safe_get(row['PART NO.']), (376, 301), 3.7),
        (safe_get(row['PART NAME']), (376, 544), 2.7),
        (safe_get(row["Q'TY"]), (376, 787), 3.7),
        (safe_get(row["NAME"]), (376, 1031), 3.7),
        (safe_get(row["ITEM"]), (1031, 151), 3.7)
    ]

    for text, position, scale in text_params:
        cv2.putText(img, text, position, 1, scale, (0, 0, 0), 2, cv2.LINE_AA)

    return img


def images_to_pdf(image_folder, output_pdf):
    images = sorted([file for file in os.listdir(image_folder) if file.endswith('.jpg')])
    with Image.open(os.path.join(image_folder, images[0])) as first_image:
        first_image.save(
            output_pdf,
            save_all=True,
            append_images=[Image.open(os.path.join(image_folder, image)).convert('RGB') for image in images[1:]]
        )


def download_file(url, filename):
    print(f'Downloading {filename}')
    proxy_handler = urllib.request.ProxyHandler({
        'http': 'http://150.61.8.70:10080',
        'https': 'http://150.61.8.70:10080'
    })
    opener = urllib.request.build_opener(proxy_handler)
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, filename)


def main():
    if 'format_inventory.csv' not in os.listdir():
        data = {
            'ITEM': [62, 63],
            'PART NO.': ['QC2-xxxx', 'VC9-xxxx'],
            'PART NAME': ['FABRIC SHEET CARD M82', 'AL CAPACITOR'],
            "Q'TY": [2, 2],
            'NAME': ['Mr.A', 'Mr.B']
        }
        pd.DataFrame(data).to_csv('format_inventory.csv', index=False)
        print("Created format_inventory.csv. Please fill it with your data and run the script again.")
        return

    if "for A4.jpg" not in os.listdir():
        download_file(
            "https://raw.githubusercontent.com/hexs/format-inventory/main/for%20A4.jpg",
            "for A4.jpg"
        )

    if os.path.exists('page'):
        shutil.rmtree('page')
    os.mkdir('page')

    try:
        df = pd.read_csv('format_inventory.csv', encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv('format_inventory.csv', encoding='ISO-8859-1')

    len_df = len(df)
    page_count = math.ceil(len_df / 6)

    print(df)
    print(f'Total rows: {len_df}')
    print(f'Total pages: {page_count}')

    template_img = cv2.imread('for A4.jpg')

    for i in range(1, page_count + 1):
        series = [max_return_0(len_df, page_count * j + i) for j in [1, 0, 3, 2, 5, 4]]
        print(f'Page {i}: {series}')

        ia4 = to_a4(*[grid_img(x, df, template_img) for x in series])
        cv2.imwrite(f'page/{i:03}.jpg', ia4)

    images_to_pdf("page", "output.pdf")
    print("PDF generated successfully: output.pdf")


if __name__ == '__main__':
    main()
