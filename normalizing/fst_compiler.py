#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Provides methods for FST stringcompile


"""

import pynini as pn
import pywrapfst as fst

class FST_Compiler:

    def __init__(self, utf8_symbols, word_symbols):
        self.utf8_symbols = utf8_symbols
        self.word_symbols = word_symbols
        self.attr_div = '|'


    def fst_stringcompile(self, text):
        """
        Compiles a string into a Pynini format FST, converting the characters of 'text' into their utf8 integer
        representation.

        :param text:
        :return: an FST in Pynini format
        """

        input_fst = self.get_basic_fst(text)
        # conversion to Pynini format necessary for the access of Pynini FST methods
        pynini_fst = pn.Fst.from_pywrapfst(input_fst)

        return pynini_fst


    def fst_stringcompile_token(self, token):
        """
        Compiles the content of the semiotic class of 'token' into an FST in Pynini format.

        Example: Token has semiotic class 'cardinal' with the content '5':
        The labels of the resulting FST (with utf8 integer representation of the characters):

        99:99 - 97:97 - 114:114 - 100:100 - 105:105 - 110:110 - 97:97 - 108:108 - 124:124 - 0:0 -
        105:105 - 110:110 - 116:116 - 101:101 - 103:103 - 101:101 - 114:114 - 58:58 - 0:0 - 53:53 - 0:0 - 124:124: 0:0

        [c - a - r - d -i - n - a - l - | - ' ' - i - n - t - e - g - e - r - : - ' ' - 5 - ' ' - | - ' ']


        :param token:
        :return:
        """

        if not token.semiotic_class:
            # logger warn or error?
            print('Token ' + str(token) + ' does not have a semiotic class!')
            return

        semiotic_class = token.semiotic_class.name + self.attr_div
        label_fst = self.get_basic_fst(semiotic_class)

        for attr in token.semiotic_class.grammar_attributes():
            attr_str = ' '.join(attr) + ' ' + self.attr_div + ' '
            attr_fst = self.get_basic_fst(attr_str, unknown_to_zero=True)
            # only one attr for now, need to combine the attr fsts when there are more attributes, like in 'money'

        pn_label = pn.Fst.from_pywrapfst(label_fst)
        pn_attr = pn.Fst.from_pywrapfst(attr_fst)
        input_fst = pn.Fst.concat(pn_label, pn_attr)
        pynini_fst = pn.Fst.from_pywrapfst(input_fst)

        return pynini_fst


    def get_basic_fst(self, text, unknown_to_zero=False):
        """
        Compiles a string into an OpenFST format FST, converting the characters of 'text' into their
        utf8 integer representation.
        The space character is not included in the utf8 symbol table and is per default converted into '0x0020'.
        If unknown_to_zero is set to True, unknown chars will be converted to zero.

        :param text: the string to compile into an FST
        :param unknown_to_zero: False per default
        :return: an OpenFST format FST representing 'text'
        """

        compiler = fst.Compiler()
        state_counter = 0
        for c in text:
            uni = self.utf8_symbols.find(c)
            if uni == -1:
                if unknown_to_zero:
                    uni = 0
                else:
                    # do we need this? can we always insert zero for unknown?
                    conv = '0x%04x' % ord(c)
                    uni = self.utf8_symbols.find(conv)
            from_state = state_counter
            to_state = state_counter + 1
            entry = "{} {} {} {}\n".format(from_state, to_state, uni, uni)
            compiler.write(entry)
            state_counter += 1

        compiler.write("{}\n\n".format(state_counter))

        input_fst = compiler.compile()
        return input_fst

    def get_basic_word_fst(self, text_arr):

        compiler = fst.Compiler()
        state_counter = 0
        next_state = 0
        for arr in text_arr:
            # single word, single expansion
            if len(arr) == 1:
                for w in arr:
                    uni = self.word_symbols.find(w)
                    if uni == -1:
                        conv = '<unk>'
                        uni = self.word_symbols.find(conv)
                    from_state = state_counter
                    if next_state != 0:
                        to_state = next_state
                        state_counter = next_state - 1
                        next_state = 0
                    else:
                        to_state = state_counter + 1
                    entry = "{} {} {} {}\n".format(from_state, to_state, uni, uni)
                    compiler.write(entry)
                    state_counter += 1

            # multiple verbalization possibilities
            # we are working char by char, so store the state_counter, such that
            # all possibilities have the same from_state
            else:
                from_state = state_counter
                to_state = state_counter + 1
                for i, elem in enumerate(arr):
                    uni = self.word_symbols.find(elem)
                    if uni == -1:
                        conv = '<unk>'
                        uni = self.word_symbols.find(conv)
                    entry = "{} {} {} {}\n".format(from_state, to_state, uni, uni)
                    compiler.write(entry)
                    state_counter += 1

                next_state = to_state + 1
                state_counter = to_state

        compiler.write("{}\n\n".format(state_counter))

        input_fst = compiler.compile()
        return input_fst

    def fst_stringcompile_words(self, text_arr):
        input_fst = self.get_basic_word_fst(text_arr)
        pynini_fst = pn.Fst.from_pywrapfst(input_fst)

        return pynini_fst


    def extract_verbalization(self, verbalized_fst):
        transitions = self.extract_transitions_graph(verbalized_fst)
        paths = self.find_all_paths(transitions, 0, verbalized_fst.num_states())
        verbalizations = self.extract_words_from_paths(paths, transitions)
        return verbalizations

    def extract_transitions_graph(self, inp_fst):
        transitions = {}
        self.set_transitions_from_state(inp_fst, inp_fst.start(), transitions)
        for i in range(inp_fst.start(), inp_fst.num_states() - 1):
            if i == inp_fst.start():
                continue
            self.set_transitions_from_state(inp_fst, i, transitions)

        return transitions

    def set_transitions_from_state(self, inp_fst, start, trans_dict):
        if start < 0:
            # somehow an empty fst got here
            return
        arc_it = inp_fst.arcs(start)
        while not arc_it.done():
            val = arc_it.value()
            next_state = val.nextstate
            label = self.utf8_symbols.find(val.olabel).decode('utf-8')
            if start in trans_dict:
                trans_dict[start].append((next_state, label))
            else:
                trans_dict[start] = [(next_state, label)]
            arc_it.next()

    def find_all_paths(self, graph, start, end, path=[]):
        """
        Finds all paths through 'graph'.
        See: https://www.python.org/doc/essays/graphs/

        :param graph:
        :param start:
        :param end:
        :param path:
        :return:
        """
        path = path + [start]
        if start == end:
            return [path]
        if start not in graph:
            return[path]
        paths = []
        for node in graph[start]:
            if node[0] not in path and node[0] != 0:
                newpaths = self.find_all_paths(graph, node[0], end, path)
                for newpath in newpaths:
                    paths.append(newpath)

        return paths

    @staticmethod
    def extract_words_from_paths(paths, transitions):
        words = []
        for path in paths:
            w = ''
            for i, elem in enumerate(path):
                if i < len(path) - 1:
                    label_arr = transitions[elem]
                    for tup in label_arr:
                        if tup[0] == path[i + 1]:
                            if tup[1] == '0x0020':
                                w = w + ' '
                            else:
                                w = w + tup[1]

            words.append(w)

        return words
