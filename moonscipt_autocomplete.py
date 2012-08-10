import sublime, sublime_plugin

import moonscript_common as ms

import subprocess, re, os, threading, tempfile, datetime, uuid
from subprocess import Popen, PIPE



AC_OPTS = sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS   

PAT_PARSE = re.compile(
    r'(?P<g1>{)|'
    r'(?P<g2>})|'
    r'(?P<g3>\[\d+\])|'
    r'(?P<g4>""")|'
    r'(?P<g5>\n)'
    )   

def pat_parse_repl( match ):
    value = ''
    if match.group('g1'):
        value = '['
    elif match.group('g2'):
        value = ']'
    elif match.group('g3'):
        value = ''
    elif match.group('g4'):
        value = '"\'"'
    elif match.group('g5'):
        value = ','
    return value 

def uniq(list):
    seen = set()
    return [value for value in list if value not in seen and not seen.add(value)]


class MoonScriptAutocomplete(sublime_plugin.EventListener):

    sugs = []


    def on_query_completions(self, view, prefix, locations):

        pos = locations[0]
        scopes = view.scope_name(pos).split()

        if ('source.moonscript' not in scopes): # or (ms.setting('ms_complete_enabled', False) is not True):
            return []
       
        cmd = ms.setting('moonc_cmd', 'moonc')

        args = [cmd, '-T', '/Users/eli/dev/projects/WordPile/src/test.moon']
        out, err, _ = ms.runcmd(args)

        if len(out) == 0:
            return []

        # print 'out->' + out

        out = PAT_PARSE.sub(pat_parse_repl, out)

        # print 'out->' + out

        tree = eval(out[:-1])

        # print 'tree->' + str(tree)

        self.sugs = []
        
        self.parse( tree, 1 )

        return (uniq(self.sugs), AC_OPTS)





    def addSug(self, s, t):

        self.sugs.append( ('~%s\t%s' % (str(s), str(t) ) , str(s) ) )


    def parse(self, a, depth):

        # print ('-' * depth) + ' ' + str(a) 

        if isinstance( a[0], list ): 
            for p in a:
                self.parse( p, depth + 1)

        else:

            # print 'cmd->' + str(cmd) + ' ' + str(a) 

            if  not isinstance( a, list ):
                return True
            
            cmd = a[0]

            if cmd == 'assign':

                for b in a[1]:

                    if isinstance( b, list ):

                        if b[0] == 'self':
                            self.addSug( b[1] , '@ ' + cmd )

                    else:
                        self.addSug( str(b), cmd )
            
                if isinstance( a[2][0], list):
                    self.parse( a[2], depth + 1)

            elif cmd == 'call':

                True

            elif cmd == 'class':

                nm = a[1]

                self.addSug( nm, cmd )

                self.parse( a[3], depth + 1)


            elif cmd == 'case':

                self.parse( a[2], depth + 1)

            elif cmd == 'colon':

                self.parse( a[2], depth + 1)

            elif cmd == 'chain':

                for b in a[2:]:

                    self.parse( b, depth + 1)

            elif cmd == 'dot':

                True

            elif cmd == 'exp':

                if isinstance( a[1], list ):

                    self.parse( a[1], depth + 1)

            elif cmd == 'explist':

                if isinstance( a[1], list ):

                    self.parse( a[1], depth + 1)

            elif cmd == 'export':

                True

            elif cmd == 'false':

                True

            elif cmd == 'for':

                self.parse( a[2], depth + 1)

            elif cmd == 'fndef':

                self.parse( a[4], depth + 1)

            elif cmd == 'foreach':

                self.parse( a[3], depth + 1)

            elif cmd == 'if':

                self.parse( a[2], depth + 1)

            elif cmd == 'import':

                self.parse( a[2], depth + 1)

            elif cmd == 'index':

                True

            elif cmd == 'length':

                True

            elif cmd == 'minus':

                True

            elif cmd == 'nil':

                True

            elif cmd == 'not':

                self.parse( a[1], depth + 1)

            elif cmd == 'number':

                True 

            elif cmd == 'parens':

                self.parse( a[1], depth + 1)

            elif cmd == 'props':

                nm = a[1][0]

                ty = a[1][1][0]

                if ty == 'fndef':

                    parms = a[1][1][1]

                    if len(parms) > 0:
                        nm = nm + '( ' + ', '.join(str(x[0]) for x in parms) + ' )'
                    else:
                        nm = nm + '!'

                    self.addSug( nm, ty )  

                else:

                    self.addSug( nm, cmd )

                self.parse( a[1][1], depth + 1)                

            elif cmd == 'return':

                if isinstance( a[1], list ):
                    self.parse( a[1], depth + 1)

            elif cmd == 'self':

                True 

            elif cmd == 'string':

                True 

            elif cmd == 'table':

                for b in a[1]:
                    if len(b) == 1:
                        self.parse( b[0], depth + 1)
                    else:
                        if isinstance( b[0], list ):
                            self.addSug( b[0][1] , '@ ' + cmd )
                        else:
                            self.addSug( str(b[0]), cmd )
                        self.parse( b[1], depth + 1)

            elif cmd == 'switch':

                self.parse( a[2], depth + 1)

            elif cmd == 'update':

                True

            elif cmd == 'with':

                self.parse( a[2], depth + 1)

            elif cmd == 'while':

                self.parse( a[1], depth + 1)

            elif cmd == 'true':

                True




            else:
                print 'cmd not parsed - %s - %s' % (cmd, str(a) )


