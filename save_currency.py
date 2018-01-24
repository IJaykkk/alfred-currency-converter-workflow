import sys
from collections import deque
from workflow import Workflow

def main(wf):
    args = wf.args
    cur = args[0]

    # initialize from the setting
    dq = deque(wf.settings['defaults']['cur_types'], maxlen=6)

    try:
        dq.remove(cur)
    except:
        pass

    dq.appendleft(cur)
    wf.settings['defaults']['cur_types'] = list(dq)
    wf.settings.save()

    print('{0} has been add to the list'.format(cur))

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
