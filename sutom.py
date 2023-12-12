#!/usr/bin/env python3

import argparse
import random


class Sutom:

    len = 0
    fixed_letters = []
    bad_placed = {}
    unknown = []
    bad_letters = {}
    template = ""
    tested_word = ""

    def __init__(self, debug):
        self.debug = debug

    def set_template(self, template):
        self.template = template.upper()
        self.bad_placed = {}
        self.__analyse_template()

    def set_word(self, tested_word):
        self.tested_word = tested_word

    def __analyse_template(self):
        self.unknown = []
        self.fixed_letters = []
        self.len = 0
        for c in self.template:
            self.len += 1
            if c == '-':
                self.fixed_letters.append('.')
                self.unknown.append(self.len - 1)
                try:
                    self.bad_placed[self.tested_word[self.len - 1]].append(self.len - 1)
                except KeyError:
                    self.bad_placed[self.tested_word[self.len - 1]] = [self.len - 1]
            elif c == '.':
                self.fixed_letters.append(c)
                self.unknown.append(self.len - 1)
            else:
                self.fixed_letters.append(c)

        if self.tested_word != "":
            pos = 0
            for c in self.fixed_letters:
                pos += 1
                if c == '.':
                    try:
                        self.bad_letters[pos - 1].append(self.tested_word[pos-1])
                    except KeyError:
                        self.bad_letters[pos - 1] = [self.tested_word[pos-1]]


class Analyzer:
    unused_letters = ""
    debug = False
    remaining_words = []

    def __init__(self, debug=False):
        self.debug = debug

        for line in open("resources/frdic.csv", "r"):
            self.remaining_words.append(line.strip())

    def add_unused(self, unused):
        self.unused_letters += unused.upper()

    def find_words(self, sutom_object):
        newr = []
        for word in self.remaining_words:
            if sutom_object.len == len(word) \
               and self.__test_fixed_letters(sutom_object, word) \
               and self.__test_unused(word) \
               and self.__test_bad_placed(sutom_object, word) \
               and self.__test_bad_letters(sutom_object, word):
                newr.append(word)

        # sort by letter diversity
        newr.sort(reverse=True, key=self.__unique_letters)

        self.remaining_words = newr

    @staticmethod
    def __unique_letters(word):
        return len(list(set([y for y in word])))

    def __test_fixed_letters(self, sutom_object, word):
        ret = True
        for i in range(0, sutom_object.len):
            fixed = sutom_object.fixed_letters[i]
            if (fixed != '.' and fixed != word[i]) or word[i] == ' ':
                ret = False

        if self.debug:
            print("Fixed letters :", word, "==>", ret)

        return ret

    def __test_unused(self, word):
        ret = True

        for c in self.unused_letters:
            try:
                word.index(c)
                ret = False
                break
            except ValueError:
                pass

        if self.debug:
            print("Unused letters :", word, "==>", ret)
        return ret

    def __test_bad_placed(self, sutom_object, word):
        keepword = len(sutom_object.bad_placed.keys()) == 0

        for bp in sutom_object.bad_placed.keys():
            keepletter = False
            for i in sutom_object.unknown:
                if word[i] == bp:
                    keepletter = True

            if keepletter:
                keepword = True
            else:
                if self.debug:
                    print("bad placed :", word)
                return False

        if self.debug:
            print("Bad placed :", word, "==>", keepword)

        return keepword

    def __test_bad_letters(self, sutom_object, word):
        ret = True
        for bl in sutom_object.bad_letters.keys():
            for lettre in sutom_object.bad_letters[bl]:
                if word[bl] == lettre:
                    if self.debug:
                        print("bad letters :", word)
                    ret = False
                    break
            if not ret:
                break

        if self.debug:
            print("Bad letters :", word, "==>", ret)

        return ret


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action='store_true', help='print debug messages to stderr')
    args = parser.parse_args()
    DEBUG = args.debug

    sut = Sutom(DEBUG)
    analyzer = Analyzer(DEBUG)

    first_pass = True

    while len(analyzer.remaining_words) > 1:
        sutom = input("Sutom template string : ")
        sut.set_template(sutom)

        if not first_pass:
            print("Current unused letters :", analyzer.unused_letters)
            unused_letters = input("Add unused letters : ")
            analyzer.add_unused(unused_letters)

        first_pass = False

        if DEBUG:
            print("DEBUG", args.debug)
            print("Template :", sutom.upper())
            print("Unused :", analyzer.unused_letters.upper())

        if DEBUG:
            print("Longueur du mot :", sut.len)
            print("Fixed letters :", sut.fixed_letters)
            print("Bad placed letters :", sut.bad_placed)
            print("Bad letters :", sut.bad_letters)

        analyzer.find_words(sut)

        print("Possible words count :", len(analyzer.remaining_words))

        if len(analyzer.remaining_words) > 0:
            possibles = []
            if len(analyzer.remaining_words) <= 10:
                possibles = analyzer.remaining_words
            else:
                possibles = []
                for nb in range(0, 9):
                    possibles.append(analyzer.remaining_words[nb])

            print("Some possible words :", possibles)

            print("=== TRY : ", possibles[random.randrange(len(possibles))], "===")

            if len(analyzer.remaining_words) > 1:
                try_word = input("Tried word : ").upper()
                sut.set_word(try_word)
        else:
            print("=== ERROR NO MATCHING WORD ===")
