import sys
import json
from workflow import Workflow, web

def main(wf):
    # set api
    api_url = "https://tw.rter.info/capi.php"

    # retrieve live currency rate from api
    r = web.get(url=api_url)
    r.raise_for_status()
    resp = r.text
    data = json.loads(resp)

    arg = wf.args[0]
    n = to_number(wf.args[0])

    if isinstance(n, int) or isinstance(n, float):
        total = n * data['USDTWD']['Exrate']
        wf.add_item(title=str(total))
        wf.send_feedback()
    else:
        wf.add_item('Please enter a valid format')
        wf.send_feedback()

def to_number(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
