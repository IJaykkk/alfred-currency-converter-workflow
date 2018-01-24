import sys
import json
import re
from datetime import datetime, timedelta
from workflow import Workflow, web

def main(wf):
    args = wf.args

    # defaults about cur_types, rate, timestamp
    set_defaults()

    # renew currency exchange rate
    renew_rate()

    try:
        base = args[0].upper()
    except:
        return wait(m="cur [currency type] [amount]")

    try:
        if base in wf.settings['defaults']['rate']:
            amount = float(args[1])
        else:
            return wait(m="Please enter valid currency like 'usd'")
    except:
        return wait(m='Please enter the amount')

    cur_types, rate = wf.settings['defaults']['cur_types'], wf.settings['defaults']['rate']

    # produce results
    amount = '{0}'.format(amount).rstrip('0').rstrip('.')

    for cur in cur_types:
        if base == cur and len(cur_types) > 1: continue

        total = float(amount) * rate[cur] / rate[base]
        total = '{0:.4f}'.format(total).rstrip('0').rstrip('.')
        title = '{0} {1} = {2} {3}'.format(amount, base, total, cur)

        wf.add_item(title=title,
                valid=True,
                subtitle='Press enter to copy to clipboard',
                copytext=total, arg=total)

    wf.send_feedback()

def set_defaults():
    if not 'defaults' in wf.settings:
        wf.settings['defaults'] = {
                'cur_types': ['TWD'],
                'rate': get_rate(),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    return

def renew_rate():
    present = datetime.now()
    last_renew_time = datetime.strptime(wf.settings['defaults']['timestamp'], '%Y-%m-%d %H:%M:%S')

    if present - last_renew_time >= timedelta(days=1):
        wf.settings['defaults']['rate'] = get_rate()
        wf.settings['defaults']['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        wf.settings.save()

    return

def wait(m):
    wf.add_item(title=m)
    wf.send_feedback()

def get_rate():
    # set api
    api_url = 'https://tw.rter.info/capi.php'

    # retrieve live currency rate from api
    r = web.get(url=api_url)
    r.raise_for_status()
    resp = r.text
    data = json.loads(resp)

    # clear up data
    rate = {k: v['Exrate'] for k, v in data.items()}
    rate = {re.sub('^USD', '', k): v for k, v in rate.items() if k != "USD"}

    return rate

if __name__ == '__main__':
    wf = Workflow()
    sys.exit(wf.run(main))
