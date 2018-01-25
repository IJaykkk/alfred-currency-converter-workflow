import sys
import os
from workflow import Workflow

def main(wf):
    args = wf.args

    # parse the first arg
    op = args[0]

    if op == 'add':
        try:
            cur = args[1]
        except:
            return wait(m="Please give a valid currency type")

        if is_valid_cur(cur):
            cur = cur.upper()
        else:
            return wait(m="{0} isn't a valid currency type".format(cur))

    iterator = [cur] if op == 'add' else wf.settings['defaults']['cur_types']

    for c in iterator:
        title = '{0} {1}'.format(op.capitalize(), c)
        subtitle = 'Press enter to proceed'
        arg = '{0} {1}'.format(op, c)
        icon = './assets/flags/{0}.png'.format(c.lower())

        wf.add_item(title=title, subtitle=subtitle, icon=icon, arg=arg, valid=True)

    wf.send_feedback()

def wait(m):
    wf.add_item(title=m)
    wf.send_feedback()

def is_valid_cur(cur):
    return cur.upper() in wf.settings['defaults']['rate']

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
