import sys
from collections import deque
from workflow import Workflow

def main(wf):
    args = wf.args

    # parse args
    op = args[0]
    cur = args[1]

    # initialize from the setting
    dq = deque(wf.settings['defaults']['cur_types'], maxlen=6)

    try:
        dq.remove(cur)
    except:
        pass

    if op == 'add': dq.appendleft(cur)

    wf.settings['defaults']['cur_types'] = list(dq)
    wf.settings.save()

    if op == 'add':
        print('{0} has been added to the list'.format(cur))
    else:
        print('{0} has been deleted from the list'.format(cur))

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
