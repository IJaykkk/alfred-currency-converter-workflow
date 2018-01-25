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

    # parse the first arg
    try:
        if args[0] == 'add' or args[0] == 'del':
            return
        else:
            base = args[0].upper()
    except:
        return wait(m="cur [currency type] [amount]")

    # parse the second arg
    try:
        if base in wf.settings['defaults']['rate']:
            amount = float(args[1])
        else:
            return wait(m="Please enter valid currency like 'usd'")
    except:
        return wait(m='Please enter the amount')

    cur_types, rate = wf.settings['defaults']['cur_types'], wf.settings['defaults']['rate']

    amount = '{0}'.format(amount).rstrip('0').rstrip('.')

    # produce items
    for cur in cur_types:
        if base == cur and len(cur_types) > 1: continue

        ratio = rate[cur] / rate[base]
        ratio = '{0:.4f}'.format(ratio).rstrip('0').rstrip('.')

        total = float(amount) * float(ratio)
        total = '{0:.4f}'.format(total).rstrip('0').rstrip('.')

        title = '{0} {1}'.format(total, cur)
        subtitle = '{0} : {1} = 1.0 : {2}'.format(base, cur, ratio)
        icon = './assets/flags/{0}.png'.format(cur)

        wf.add_item(title=title,
                valid=True,
                subtitle=subtitle,
                copytext=total,
                arg=total,
                icon=icon)

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
