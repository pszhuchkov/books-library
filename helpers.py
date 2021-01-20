import argparse


BOOK_URL = 'https://tululu.org/b{}/'
DOWNLOAD_TXT_URL = 'https://tululu.org/txt.php?id={}'
BOOKS_DIRNAME = 'books'
IMAGES_DIRNAME = 'images'
COLLECTION_URL = 'https://tululu.org/l55/'


def get_parsed_arguments():
    parser = argparse.ArgumentParser(
        description='Программа скачивает книги с сайта tululu.org.'
    )
    parser.add_argument('start_id', nargs='?', type=int, default=0)
    parser.add_argument('end_id', nargs='?', type=int, default=0)
    parser.add_argument('--start_page', help='стартовая страница',
                        type=int, default=1)
    parser.add_argument('--end_page', help='конечная страница', type=int)
    parser.add_argument('--books_dirname', type=str, default=BOOKS_DIRNAME,
                        help='название каталога с книгами')
    parser.add_argument('--images_dirname', type=str, default=IMAGES_DIRNAME,
                        help='название каталога с изображениями')
    parser.add_argument('--dest_dir', type=str, default='.',
                        help='каталог для сохраняемых файлов')
    parser.add_argument('--skip_img', action='store_true',
                        default=False, help='не сохранять изображения')
    parser.add_argument('--skip_txt', action='store_true',
                        default=False, help='не сохранять текстовые файлы')
    parser.add_argument('--json_path', type=str,
                        help='путь к json-файлу с результатами')
    parser.add_argument('--collection_url', type=str, default=COLLECTION_URL,
                        help='адрес web-страницы с коллекцией')
    return parser.parse_args()
