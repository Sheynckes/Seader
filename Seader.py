# -*- coding: utf-8 -*-

import os
import tkinter as tk
from tkinter import filedialog
import string
import urllib
from bs4 import BeautifulSoup

YOUDAO = 'http://youdao.com/w/%s/#keyfrom=dict2.top'

class Application(object):
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('Seader')
        self.root.geometry('+800+400')
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.create_frm_tools()
        self.create_frm_txt()
        self.create_frm_words()
        
        self.create_paras()

        self.root.mainloop()

    def create_frm_tools(self):
        self.frm_tools = tk.Frame(self.root)
        self.frm_tools.pack(fill=tk.X)
        self.btn_open = tk.Button(self.frm_tools, text='Open Book', command=self.open_book)
        self.btn_open.pack(padx=10, side=tk.LEFT)
        self.btn_count = tk.Button(self.frm_tools, text='Count Word', command=self.count_word)
        self.btn_count.pack(padx=10, side=tk.LEFT)

    def create_frm_txt(self):
        self.frm_txt = tk.Frame(self.root)
        self.frm_txt.pack(side=tk.LEFT, fill=tk.BOTH)
        self.scrl_novel = tk.Scrollbar(self.frm_txt)
        self.scrl_novel.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_novel = tk.Text(self.frm_txt, height=40, yscrollcommand=self.scrl_novel.set)
        self.txt_novel.pack(side=tk.LEFT, fill=tk.BOTH)
        self.scrl_novel.config(command=self.txt_novel.yview)

    def create_frm_words(self):
        self.frm_words = tk.Frame(self.root, width=30)
        self.frm_words.pack(side=tk.LEFT, fill=tk.Y)

        self.frm_search = tk.Frame(self.frm_words)
        self.frm_search.pack(fill=tk.X)
        self.entry_search = tk.Entry(self.frm_search, width=10, borderwidth=0, background='LightGrey')
        self.entry_search.pack(padx=5, side=tk.LEFT)
        self.label_result = tk.Label(self.frm_search)
        self.label_result.pack(padx=5, side=tk.LEFT)

        self.frm_btns = tk.Frame(self.frm_words)
        self.frm_btns.pack(fill=tk.X)
        self.btn_define = tk.Button(self.frm_btns, text='Define', command=self.define_word)
        self.btn_define.pack(padx=5, side=tk.LEFT)
        self.btn_previous = tk.Button(self.frm_btns, text='Previous', command=self.previous_word, state=tk.DISABLED)
        self.btn_previous.pack(padx=5, side=tk.LEFT)
        self.btn_next = tk.Button(self.frm_btns, text='Next', command=self.next_word)
        self.btn_next.pack(padx=5, side=tk.LEFT)

        self.frm_definition = tk.Frame(self.frm_words)
        self.frm_definition.pack(fill=tk.X)
        self.scrl_definition = tk.Scrollbar(self.frm_definition)
        self.scrl_definition.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_definition = tk.Text(self.frm_definition, width=25, height=20, yscrollcommand=self.scrl_definition.set)
        self.txt_definition.pack(side=tk.LEFT, fill=tk.BOTH)
        self.scrl_definition.config(command=self.txt_definition.yview)

        self.label_count = tk.Label(self.frm_words, text='Word Counts: ', anchor=tk.W, background='Gainsboro')
        self.label_count.pack(fill=tk.X)

        self.frm_count = tk.Frame(self.frm_words)
        self.frm_count.pack(fill=tk.BOTH)
        self.scrl_count = tk.Scrollbar(self.frm_count)
        self.scrl_count.pack(side=tk.RIGHT, fill=tk.Y)
        self.lb_count = tk.Listbox(self.frm_count, height=18, yscrollcommand=self.scrl_count.set)
        self.lb_count.pack(side=tk.LEFT, fill=tk.BOTH)
        self.scrl_count.config(command=self.lb_count.yview)
        self.lb_count.bind('<Double-Button-1>', self.define_word_from_lb)

    def create_paras(self):
        self.idx = 1.0
        self.word_temp = ''
        self.word_num = 0

    def open_book(self):
        filename = filedialog.askopenfile()
        with open(filename.name, 'r') as filetxt:
            self.txt_novel.delete(1.0, tk.END)
            self.txt_novel.insert(tk.END, filetxt.read())
        # self.count_word()

    def not_stop_words(self, word):
        stop_words_file = open("stop_words.txt", "r")
        stop_words_list = stop_words_file.read().split(",")
        stop_words_file.close()

        if not (word in stop_words_list):
            return word

    def word_cleaning(self, word):
        word = word.strip(string.punctuation+"""!?,.'“”-…""")
        if word.isalpha():
            return word.lower()


    def count_word(self):
        txt = self.txt_novel.get(1.0, tk.END)

        self.wc_dict = {}

        for word in txt.split():
            word = self.word_cleaning(word)
            word = self.not_stop_words(word)
            if word in self.wc_dict:
                self.wc_dict[word] += 1
            else:
                self.wc_dict[word] = 1

        word_counts = []
        for word, count in self.wc_dict.items():
            if word:
                word_counts.append({"word": word, "count": count})

        self.word_by_counts = sorted(word_counts, key=lambda d: (d['count'], d['word']), reverse=True)
        
        for d in self.word_by_counts:
            self.lb_count.insert(tk.END, '(%03d) %s' %(d["count"], d["word"]))

    def define_word(self):
        self.txt_definition.delete(1.0, tk.END)

        url = YOUDAO % self.entry_search.get()
        resp = urllib.request.urlopen(url)
        html = resp.read()
        soup = BeautifulSoup(html, 'lxml')

        pronunciation = soup.find('div', attrs={'class': 'baav'}).get_text()
        p_list = pronunciation.split()
        self.txt_definition.insert(tk.END, ' '.join(p_list))

        definition = soup.find('div', attrs={'class': 'trans-container'})
        self.txt_definition.insert(tk.END, os.linesep + definition.ul.get_text())
        
        if definition.p:
            additional = definition.p.get_text()
            a_list = additional.split()
            self.txt_definition.insert(tk.END, os.linesep*2 + ' '.join(a_list))

    def define_word_from_lb(self, btn_obj):
        self.entry_search.delete(0, tk.END)
        self.word_search = self.lb_count.selection_get().split()[-1]
        self.entry_search.insert(tk.END, self.word_search)
        self.define_word()

    def previous_word(self):
        self.word_num -= 1
        self.label_result.config(text='%d of %d' % (self.word_num, self.word_total))

        self.word_start = self.txt_novel.search(' %s ' % self.word_search, self.word_start, backwards=True)
        idx_dot = self.word_start.index('.')
        line = int(self.word_start[0: idx_dot])
        column = int(self.word_start[idx_dot+1: ])
        self.word_end = str(line) + '.' + str(column + self.word_len + 1)
        self.txt_novel.tag_delete('bg')
        self.txt_novel.tag_add('bg', self.word_start, self.word_end)
        self.txt_novel.tag_config('bg', background='yellow')
        self.txt_novel.see(self.word_start)

        if self.word_num == self.word_total - 1:
            self.btn_next.config(state=tk.NORMAL)
        if self.word_num == 1:
            self.btn_previous.config(state=tk.DISABLED)

    def next_word(self):
        self.word_search = self.entry_search.get()
        if self.word_search and (self.word_search != self.word_temp):
            self.word_end = '1.0'
            self.word_num = 0
            self.word_temp = self.word_search
            self.txt_novel.tag_delete('bg')
        elif self.word_search == self.word_temp:
            self.txt_novel.tag_delete('bg')

        self.word_len = len(self.word_search)
        self.word_start = self.txt_novel.search(' %s ' % self.word_search, self.word_end)
        if self.word_start:
            self.word_num += 1
            self.word_total = self.wc_dict[self.word_search]
            self.label_result.config(text='%d of %d' % (self.word_num, self.word_total))

            idx_dot = self.word_start.index('.')
            line = int(self.word_start[0: idx_dot])
            column = int(self.word_start[idx_dot+1: ])
            self.word_end = str(line) + '.' + str(column + self.word_len + 1)
            self.txt_novel.tag_add('bg', self.word_start, self.word_end)
            self.txt_novel.tag_config('bg', background='yellow')
            self.txt_novel.see(self.word_start)

            self.btn_previous.config(state=tk.NORMAL)
            if self.word_num == self.word_total:
                self.btn_next.config(state=tk.DISABLED)
        else:
            self.label_result.config(text='0')

if __name__ == '__main__':
    app = Application()
