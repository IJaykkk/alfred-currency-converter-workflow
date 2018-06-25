import sys
from workflow import Workflow
from manager import Changer

def main(wf):
    changer = Changer(wf)
    changer.execute()
    changer.print_msgs()

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
