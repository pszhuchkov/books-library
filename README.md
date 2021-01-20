## Парсер книг с сайта tululu.org

Программа предназначена для загрузки книг в формате *.txt* с сайта https://tululu.org.

### О скриптах
`parse_tululu.py` - выполняет сохранение всех *доступных* текстовых файлов книг и
их обложек в указанном диапазоне идентификаторов книг (позиционные аргументы).  
`parse_tululu_category.py` - выполняет сохранение всех *доступных* текстовых файлов книг и их обложек 
для определенной коллекции (по умолчанию — [фантастика](https://tululu.org/l55/)) в указанном диапазоне страниц 
(аргументы `--start_page` и `--start_page`).  
`helpers.py` - вспомогательный скрипт.  
`constants.py` - содержит переменные с постоянными значениями (конфигурационный файл).  

### Как установить
Для работы программы должен быть установлен Python 3.  
Для установки зависимостей запустить команду:
```console
pip install -r requirements.txt
```

### Аргументы
`parse_tululu.py`  
При запуске программы требуется указать 2 позиционных аргумента:`start_id` и `end_id`. 
Программа скачивает все *доступные* книги в указанном диапазоне идентификаторов книг.    
`start_id` - начальный идентификатор диапазона книг на сайте (по умолчанию 0);  
`end_id` - конечный идентификатор диапазона книг на сайте (по умолчанию 0);

Пример запуска программы:
```console
python parse_tululu.py 20 30
```
В данном примере будут загружены все *доступные* книги с идентификаторами с 20 по 30 включительно.


`parse_tululu_category.py`  
При запуске программы требуется указать 2 именованных аргумента: `--start_page` и `--end_page`.
Программа скачивает все *доступные* книги в указанном диапазоне идентификаторов страниц.
Без указания параметров будут сохранены все книги, находящиеся на первой странице.  
`--start_page` - начальный идентификатор диапазона страниц коллекции (по умолчанию 1);  
`--end_page` - конечный идентификатор диапазона страниц коллекции;

Примеры запуска программы:
```console
python parse_tululu.py --start_page 10 --end_page 20
```
В данном примере будут загружены все *доступные* книги, находящийся на страницах с 
идентификаторами с 1 по 5 включительно.  
```console
python parse_tululu.py --end_page 7
```
В данном примере будут загружены все *доступные* книги, находящийся на страницах с 
идентификаторами с 1 по 7 включительно.  
```console
python parse_tululu.py --start_page 10
```
В данном примере будут загружены все *доступные* книги, находящийся на страницах с 
идентификаторами с 10 по *последнюю* включительно.  

#### Общие аргументы  
`--books_dirname` - наименование каталога для текстовых файлов книг (по умолчанию `books`)   
`--images_dirname` - наименование каталога для обложек книг (по умолчанию `images`)  
`--dest_dir` - путь к каталогу, в который будут сохраняться все файлы  
`--skip_img` - не скачивать обложки книг  
`--skip_txt` - не скачивать текстовые файлы книг    
`--json_path` - путь к файлу с результатами  
`--collection_url` - ссылка на страницу коллекции (по умолчанию [фантастика](https://tululu.org/l55/))  



### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).