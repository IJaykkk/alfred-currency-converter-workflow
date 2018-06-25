from workflow import Workflow
from manager import Converter, ArgsManager
import sys

def main(wf):
    converter = Converter(wf)
    converter.renew_rate()
    am = ArgsManager(wf.args, converter)

    if am.status_code == 1:
        msgs = converter.gen_msgs(*(am.gen_args()))
        make_items(wf, msgs)
    else:
        msgs = am.gen_msgs()
        make_items(wf, msgs)

    wf.send_feedback()

def make_items(wf, msgs):
    for msg in msgs:
        wf.add_item(**msg)

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
