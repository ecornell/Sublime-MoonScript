import sublime, sublime_plugin

import subprocess, re, os, threading, tempfile, datetime, uuid
from subprocess import Popen, PIPE


try:
    STARTUP_INFO = subprocess.STARTUPINFO()
    STARTUP_INFO.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    STARTUP_INFO.wShowWindow = subprocess.SW_HIDE
except (AttributeError):
    STARTUP_INFO = None

AC_OPTS = sublime.INHIBIT_WORD_COMPLETIONS | sublime.INHIBIT_EXPLICIT_COMPLETIONS       

# from subprocess import check_output


class MoonScriptAutocomplete(sublime_plugin.EventListener):

    sugs = []

    def on_query_completions(self, view, prefix, locations):

        pos = locations[0]
        scopes = view.scope_name(pos).split()

        if 'source.moonscript' not in scopes :
            return []
       

        args = ['moonc', '-T','/Users/eli/dev/projects/WordPile/src/test.moon']
        out, err, _ = self.runcmd(args)


        if len(out) == 0:
            return []

        # print 'out->' + out

        out = re.sub("\n", ",", out)
        out = re.sub("\}", "]", out)
        out = re.sub("\{", "[", out)
        out = re.sub("\[\d+\]", "", out)
        out = re.sub('"""', '"\'"', out)
        
        tree = eval(out[:-1])

        # print 'tree->' + str(tree)

        self.sugs = []

        
        # for n in tree:
        self.parse( tree, 1 )

        return list(set(self.sugs))
        # return [ ('test','test') ]


    def addSug(self, s, t):

        self.sugs.append( ('~%s\t%s' % (str(s), str(t) ) , str(s) ) )


    def parse(self, a, depth):

        # print ('-' * depth) + ' ' + str(a) 

        if isinstance( a[0], list ): 
            for p in a:
                self.parse( p, depth + 1)

        else:

            cmd = a[0]

            print 'cmd->' + str(cmd) + ' ' + str(a) 

            if cmd == 'assign':

                for b in a[1]:

                    if isinstance( b, list ):
                        self.addSug( b[1] , '@ ' + cmd )

                    else:
                        self.addSug( str(b), cmd )
            
                if isinstance( a[2][0], list):
                    self.parse( a[2], depth + 1)

            elif cmd == 'class':

                nm = a[1]

                self.addSug( nm, cmd )

                self.parse( a[3], depth + 1)

            elif cmd == 'props':

                nm = a[1][0]

                ty = a[1][1][0]

                if ty == 'fndef':

                    self.addSug( nm, ty )  

                else:

                    self.addSug( nm, cmd )

                self.parse( a[1][1], depth + 1)

            elif cmd == 'table':

                for b in a[1]:

                    if isinstance( b[0], list ):
                        self.addSug( b[0][1] , '@ ' + cmd )

                    else:
                        self.addSug( str(b[0]), cmd )

                    self.parse( b[1], depth + 1)


            elif cmd == 'self':

                True 

            elif cmd == 'string':

                True 

            elif cmd == 'number':

                True 

            elif cmd == 'fndef':

                self.parse( a[4], depth + 1)

            elif cmd == 'case':

                self.parse( a[2], depth + 1)

            elif cmd == 'colon':

                self.parse( a[2], depth + 1)

            elif cmd == 'chain':

                for b in a[2:]:

                    self.parse( b, depth + 1)

            elif cmd == 'switch':

                self.parse( a[2], depth + 1)

            elif cmd == 'if':

                self.parse( a[2], depth + 1)

            elif cmd == 'import':

                self.parse( a[2], depth + 1)

            elif cmd == 'true' or cmd == 'false' or cmd == 'nil':

                True

            elif cmd == 'export':

                True

            elif cmd == 'dot':

                True

            elif cmd == 'call':

                True

            else:
                print 'cmd not parsed - %s - %s' % (cmd, str(a) )





    def runcmd(self, args, input=None, stdout=PIPE, stderr=PIPE, shell=False):

        out = ""
        err = ""
        exc = None

        #old_env = os.environ.copy()
        #os.environ.update(env())
        try:
            p = Popen(args, stdout=stdout, stderr=stderr, stdin=PIPE,
                startupinfo=STARTUP_INFO, shell=shell)
            if isinstance(input, unicode):
                input = input.encode('utf-8')
            out, err = p.communicate(input=input)
            out = out.decode('utf-8') if out else ''
            err = err.decode('utf-8') if err else ''
        except (Exception) as e:
            # err = u'Error while running %s: %s' % (args[0], e)
            print e
            exc = e
        #os.environ.update(old_env)
        return (out, err, exc)




        




