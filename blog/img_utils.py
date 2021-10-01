import os
import requests
import shutil
import wget


def download_img_request(image_url, filename):
    # Open the url image, set stream to True, this will return the stream content.
    r = requests.get(image_url, stream=True)

    # Check if the image was retrieved successfully
    if r.status_code == 200:
        # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        r.raw.decode_content = True

        # Open a local file with wb ( write binary ) permission.
        with open(filename, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

        print('Image successfully Downloaded: ', filename)
        return True
    else:
        print('Image could not be retrieved', r.status_code)
        return False


def download_img_wget(img_url, img_path):
    try:
        down_path = wget.download(img_url)
        print('Image Successfully Downloaded: ', down_path)
        shutil.move(down_path, img_path)
    except Exception as err:
        print('download failed: ' + img_url)
        print(err)
        return False

    return True


def download_img(image_url, filename):
    # return download_img_request(image_url, filename)
    return download_img_wget(image_url, filename)


def process_md(md_file):
    md_lines = open(md_file).readlines()
    img_cnt = 0
    print('process ' + md_file)
    download_success = True
    for i, md_line in enumerate(md_lines):
        if md_line.startswith('![') and ('png' in md_line or 'jpg' in md_line):
            print(md_line)
            img_url = md_line.split('](')[1][:-2]
            if img_url.startswith('http'):
                ext = 'png' if 'png' in md_line else 'jpg'
                img_path = md_file.replace('.md', '_%d.%s' % (img_cnt, ext))
                ret = download_img(img_url, img_path)
                if ret:
                    img_name = os.path.basename(img_path)
                    md_lines[i] = '![](%s)' % img_name
                    img_cnt += 1
                else:
                    download_success = False
    with open(md_file, 'w') as fd:
        fd.write(''.join(md_lines))
    return download_success


def check_md_imgs_and_replace_locally_wrapper(blog_dir, failed_mds):
    for file in os.listdir(blog_dir):
        if 'node_modules' == file:
            continue
        file_path = os.path.join(blog_dir, file)
        if os.path.isdir(file_path):
            check_md_imgs_and_replace_locally_wrapper(file_path, failed_mds)
        elif file.endswith('.md'):
            replace_success = process_md(file_path)
            if not replace_success:
                failed_mds.append(file_path)


def check_md_imgs_and_replace_locally(blog_dir):
    failed_mds = []
    check_md_imgs_and_replace_locally_wrapper(blog_dir, failed_mds)
    print('\n'.join(failed_mds))


if __name__ == '__main__':
    check_md_imgs_and_replace_locally('/Users/cwh/Mission/open_source/windy-afternoon')
