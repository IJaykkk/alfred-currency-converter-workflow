import sys
from workflow import Workflow

def main(wf):
    args = wf.args

    # parse the first arg
    try:
        cur = args[0]
    except:
        return wait(m="Please give a valid currency type")

    op = args[1]

    # check if the currency type is valid
    if is_valid_cur(cur):
        cur = cur.upper()
    else:
        return wait(m="{0} isn't a valid currency type".format(cur))

    if op == 'add':
        title = '{0} {1} to the list'.format(op.capitalize(), cur)
    else:
        title = '{0} {1} from the list'.format(op.capitalize(), cur)

    # produce an item
    wf.add_item(
            title=title,
            valid=True,
            subtitle='Press enter to proceed',
            arg='{0} {1}'.format(op, cur))
    wf.send_feedback()

def wait(m):
    wf.add_item(title=m)
    wf.send_feedback()

def is_valid_cur(cur):
    return cur.upper() in wf.settings['defaults']['rate']

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
