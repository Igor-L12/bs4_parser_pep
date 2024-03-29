# Парсер документации Python и PEP
## Описание

Парсер информации о python с **https://docs.python.org/3/** и **https://peps.python.org/**
### Перед использованием

Клонируйте репозиторий к себе на компьютер при помощи команды:
```
git clone git@github.com:Igor-L12/bs4_parser_pep.git
```

### В корневой папке создайте виртуальное окружение и установите зависимости:

```
python -m venv venv
```
```
pip install -r requirements.txt
```
### Перейдите в директорию ./src/ командой cd:

```
cd src/
```
### Запустите файл main.py выбрав необходимый режим работы парсера и аргументы:

```
python main.py [вариант парсера] [аргументы]
```
### Возможные режимы:

- whats-new   
Парсер выводящий список изменений в версиях Python.
```
python main.py whats-new [аргументы]
```
- latest_versions
Парсер выводящий список версий Python и ссылки на их документацию.
```
python main.py latest-versions [аргументы]
```
- download   
Парсер скачивающий zip архив с документацией Python в pdf формате.
```
python main.py download [аргументы]
```
- pep
Парсер выводящий список статусов документов PEP
и количество документов в каждом статусе. 
```
python main.py pep [аргументы]
```
### Аргументы

Есть возможность указывать аргументы для изменения работы программы:   
- -h, --help
Общая информация о командах.
```
python main.py -h
```
- -c, --clear-cache
Очистка кеша перед выполнением парсинга.
```
python main.py [вариант парсера] -c
```
- -o {pretty,file}, --output {pretty,file}   
Дополнительные способы вывода данных   
pretty - выводит данные в командной строке в таблице   
file - сохраняет информацию в формате csv в папке ./results/
```
python main.py [вариант парсера] -o file
```
### Технологии, которые были использованы:
```
Python 3.9, BeautifulSoup4, Document Object Model, PrettyTable
```
### Автор
- [Любаев Игорь](https://github.com/Igor-L12 "GitHub")
