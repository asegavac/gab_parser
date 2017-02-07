# -----------------------------------------------------------------------------
#
# Copyright (C) 2001-2015,
# David M. Beazley (Dabeaz LLC)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# * Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
# * Neither the name of the David Beazley or Dabeaz LLC may be used to
#   endorse or promote products derived from this software without
#  specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# -----------------------------------------------------------------------------

import re


class TokenizerError(Exception):
    """
    Exception thrown when invalid token encountered and no default error
    handler is defined.
    """

    def __init__(self, message, s):
        super().__init__(message)
        self.text = s


class TokenizerToken(object):
    """
    Token class.  This class is used to represent the tokens produced.
    """

    def __init__(self, token_type, value, pos, context={}):
        self.token_type = token_type
        self.value = value
        self.pos = pos
        self.context = context

    def __str__(self):
        return '<TokenizerToken type="%s" value="%r" pos="%d">' % (
            self.token_type, self.value, self.pos)

    def __repr__(self):
        return str(self)


class State(object):
    """
    """

    def __init__(self, name, tokens, inclusive=False,
                 ignore='', error_function=None, reflags=0):
        self.name = name
        self.tokens = tokens
        self.inclusive = inclusive
        self.ignore = ignore
        self.error_function = error_function
        self.reflags = reflags
        self._regex = None

    @property
    def regex(self):
        if self._regex is not None:
            return self._regex
        self._regex = self._form_master_re(
            [token.full_regex() for token in self.tokens])
        return self._regex

    def _form_master_re(self, relist):
        """
        This function takes a list of all of the regex components and attempts
        to form the master regular expression.  Given limitations in the
        Python re module, it may be necessary to break the master regex into
        separate expressions.
        """
        if not relist:
            return []
        regex = '|'.join(relist)
        try:
            regex = re.compile(regex, re.VERBOSE | self.reflags)

            # Build the index to function map for the matching engine
            indexfunc = [None] * (max(regex.groupindex.values()) + 1)

            for f, i in regex.groupindex.items():
                try:
                    token = next(token
                                 for token in self.tokens
                                 if token.name == f)
                    if token.value_function:
                        indexfunc[i] = (token.value_function, f)
                    else:
                        if token.ignore:
                            indexfunc[i] = (None, None)
                        else:
                            indexfunc[i] = (None, f)
                except StopIteration:
                    pass

            return [(regex, indexfunc)]
        except Exception as e:
            m = int(len(relist) / 2)
            if m == 0:
                m = 1
            llist = self._form_master_re(relist[:m])
            rlist = self._form_master_re(relist[m:])
            return (llist + rlist)

    def __repr__(self):
        return (
            '<State name="{}" inclusive={} ignore="{}" error_function="{}">'
            .format(self.name,
                    self.inclusive,
                    self.ignore,
                    self.error_function))


class Token(object):
    def __init__(self, name, regex, value_function=None, ignore=False):
        self.name = name
        self.regex = regex
        self.value_function = value_function
        self.ignore = ignore

    def full_regex(self):
        return '(?P<%s>%s)' % (self.name, self.regex)

    def __repr__(self):
        return(
            '<Token name="{}" regex="{}" value_function="{}" self.ignore={}>'
            .format(self.name,
                    self.regex,
                    self.value_funcion.__name__,
                    self.ignore))


class Tokenizer:
    """
    Base Tokenizer class
    """

    def __init__(self, states):
        self.states = states
        self._statestack = None    # Stack of states
        self.data = None           # Actual input data (as a string)
        self.pos = 0               # Current position in input text
        self.len = 0               # Length of the input text
        self.context = None

    def _get_active_states(self):
        """
        Return top states on the stack, stop if an
        exclusive state is found or if all states
        included.
        """
        states = []
        for state in reversed(self._statestack):
            states.append(state)
            if not state.inclusive:
                break
        return states

    @property
    def re(self):
        """
        Master regular expression. This is a list of
        tuples (re, findex) where re is a compiled
        regular expression and findex is a list
        mapping regex group numbers to rules.
        Comes for all states in the stack.
        """
        re = []
        for state in self._get_active_states():
            re += state.regex
        return re

    @property
    def ignore(self):
        """
        Return the list of ignored characters.
        This list comes from all states in the stack.
        """
        ignore = ''
        for state in self._get_active_states():
            ignore += state.ignore
        return ignore

    @property
    def error_function(self):
        """
        Return error fuction for the current state.
        If current state has no error function, it
        recurses down the stack.
        """
        for state in self._get_active_states():
            if state.error_function is not None:
                return state.error_function
        return None

    def _lookup_state(self, state_name):
        try:
            return next(
                state for state in self.states if state.name == state_name)
        except StopIteration:
            raise ValueError('Undefined state: {}'.format(state_name))

    def input(self, s, context={}, state_name=None):
        """
        Push a new string into the tokenizer.
        Resets all state, and will set the state stack
        to the first state if no state name is specified.
        """
        self._statestack = (
            [self.states[0]]
            if state_name is None
            else self._lookup_state(state_name))
        self.data = s
        self.pos = 0
        self.len = len(s)
        self.context = context

    def set_state(self, state_name):
        """
        Replaces current state stack with `state_name`.
        """
        self._statestack = [self._lookup_state(state_name)]

    def push_state(self, state_name):
        """
        Push `state_name` to the end of the state stack.
        """
        self._statestack.append(self._lookup_state(state_name))

    def pop_state(self):
        """
        Remove the last state off of the state stack.
        """
        self._statestack.pop()

    def skip(self, n):
        """
        Skip ahead n characters.
        """
        self.pos += n

    def token(self):
        """
        Return the next token from the Tokenizer,
        return None if no more tokens.
        """
        # Make local copies of frequently referenced attributes
        pos = self.pos
        data = self.data

        while pos < self.len:
            # This code provides some short-circuit code for
            # whitespace, tabs, and other ignored characters
            if data[pos] in self.ignore:
                pos += 1
                continue

            # Look for a regular expression match
            for regex, indexfunc in self.re:
                m = regex.match(data, pos)
                if not m:
                    continue

                # Create a token for return
                func, token_type = indexfunc[m.lastindex]
                token = TokenizerToken(token_type, m.group(), pos)

                if not func:
                    # If no token type was set, it's an ignored token
                    if token.token_type:
                        self.pos = m.end()
                        return token
                    else:
                        pos = m.end()
                        break

                pos = m.end()

                # If token is processed by a function, call it
                self.pos = pos

                value = func(token, self)
                if isinstance(value, TokenizerToken):
                    new_token = value
                elif value is None:
                    # This is here in case user has updated pos.
                    pos = self.pos
                    break
                else:
                    new_token = token
                    new_token.value = value

                return new_token
            else:

                # No match. Call t_error() if defined.
                if self.error_function:
                    token = TokenizerToken('error', self.data[pos:], pos)
                    self.pos = pos
                    new_token = self.error_function(token, self)
                    if pos == self.pos:
                        # Error method didn't change text position at all.
                        # This is an error.
                        raise TokenizerError(
                            "Scanning error. Illegal character '%s'"
                            % (data[pos]), data[pos:])
                    pos = self.pos
                    if not new_token:
                        continue
                    return new_token

                self.pos = pos
                raise TokenizerError(
                    "Illegal character '%s' at index %d"
                    % (data[pos], pos), data[pos:])

        self.pos = pos + 1
        return None

    def __iter__(self):
        """
        Return the tokenizer as an iterator
        """
        return self

    def __next__(self):
        """
        Allow the tokenizer to be used as an iterator.
        """
        t = self.token()
        if t is None:
            raise StopIteration
        return t
