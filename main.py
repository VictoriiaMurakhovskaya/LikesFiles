from tkinter import Tk, StringVar, LabelFrame, Entry, Button, Frame, LEFT, TOP
import configparser
import os
from tkinter import filedialog as fd
from tkinter import messagebox as mb
import asyncio
import aiohttp
import json

configname = 'config.cfg'


def choose_file(flag):
    global files
    try:
        files[flag].set(fd.askopenfilename(defaultextension='.txt',
                                           filetypes=[('Text files', '*.txt')]) if flag == 0 else fd.askdirectory())
    except:
        mb.showerror(title='Error', message='Incorrect choice')


def on_closing(w):
    global files
    config = configparser.ConfigParser()
    config.add_section("Files")
    config.set("Files", "inputfile", files[0].get())
    config.set("Files", "outputdir", files[1].get())

    with open('config.cfg', "w") as config_file:
        config.write(config_file)
    w.destroy()


def on_load():
    global files
    if os.path.exists('config.cfg'):
        config = configparser.ConfigParser()
        config.read('config.cfg')
        files[0].set(config.get("Files", "inputfile"))
        files[1].set(config.get("Files", "outputdir"))


async def getdata(client, name):
    req_body = 'http://147.78.65.148:3000/stat?v=' + name
    async with client.get(req_body) as response:
        assert response.status == 200
        return name, await response.text(encoding='utf-8')


async def main_loop(endings, filesdict=None):
    # запросы/запись в асинхронном режиме
    loop = asyncio.get_running_loop()
    async with aiohttp.ClientSession(loop=loop) as client:
        method_list = [getdata(client, item) for item in endings]
        gathered_tasks = await asyncio.gather(*method_list)
        for item in gathered_tasks:
            data = json.loads(item[1])
            if data:
                for subitem in ['views', 'likes', 'dislikes']:
                    filesdict[(item[0], subitem)].write(data[subitem])


def launch():
    endings = []
    # чтение окончаний url
    with open(files[0].get()) as f:
        for line in f:
            endings.append(line.strip())
    # создание дерева директорий
    if not os.path.exists(files[1].get()):
        os.mkdir(files[1].get())
    for item in endings:
        if not os.path.exists(files[1].get() + '/' + item):
            os.mkdir(files[1].get() + '/' + item)
    # создание словаря файлов
    filedict = {}
    for item in endings:
        for subitem in ['views', 'likes', 'dislikes']:
            filedict.update({(item, subitem): open(files[1].get() + '/' + item + '/' + subitem + '.txt', 'w')})

    asyncio.run(main_loop(endings, filesdict=filedict))


def ui():
    global files
    window = Tk()
    window.geometry('290x190')
    files = [StringVar(window), StringVar(window)]
    inframe = LabelFrame(text='Файл ссылок')
    outframe = LabelFrame(text='Папка вывода')
    Entry(inframe, textvariable=files[0], width=35).pack(side=LEFT, padx=(10, 5), pady=10)
    Button(inframe, text='...', command=lambda x=0: choose_file(x)).pack(side=LEFT, padx=(0, 10))
    Entry(outframe, textvariable=files[1], width=35).pack(side=LEFT, padx=(10, 5), pady=10)
    Button(outframe, text='...', command=lambda x=1: choose_file(x)).pack(side=LEFT, padx=(0, 10))
    inframe.pack(side=TOP, padx=10, pady=10)
    outframe.pack(side=TOP, padx=10, pady=10)
    Button(window, text='Запустить', command=launch).pack(side=TOP, padx=10, pady=(0, 10))
    window.protocol("WM_DELETE_WINDOW", lambda f=window: on_closing(f))
    on_load()
    window.mainloop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ui()
