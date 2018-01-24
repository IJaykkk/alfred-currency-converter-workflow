import sys
from workflow import Workflow

def main(wf):
    args = wf.args

    try:
        cur = args[0]
    except:
        return wait(m="Please give a valid currency type")

    if is_valid_cur(cur):
        cur = cur.upper()
    else:
        return wait(m="{0} isn't a valid currency type".format(cur))

    wf.add_item(
            title="Add {0} to the list of currency exchange".format(cur),
            valid=True,
            subtitle='Press enter to proceed',
            arg=cur)
    wf.send_feedback()

def wait(m):
    wf.add_item(title=m)
    wf.send_feedback()

def is_valid_cur(cur):
    return cur.upper() in wf.settings['defaults']['rate']

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
