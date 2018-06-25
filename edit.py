from workflow import Workflow
from manager import Editor, ArgsManager
import sys

def main(wf):
    editor = Editor(wf)
    am = ArgsManager(wf.args, editor, True)

    if am.status_code == 1:
        msgs = editor.gen_msgs(*(am.gen_args()))
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
