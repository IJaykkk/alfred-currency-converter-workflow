from workflow import web
from datetime import datetime, timedelta
from collections import deque
import re
import json


class ArgsManager:
    """
    status_code
    0: pending
    1: success
    10: no base, keep waiting
    11: no matched base
    12: based ignored (no error message)
    13: invalid amount
    20: no currency (add)
    21: no matched currency
    """

    response = {
            10: { "title": "To Convert a Currency", "subtitle": "cur [currency] [amount]" },
            11: { "title": "To Convert a Currency", "subtitle": "Please enter a valid currency abbreviation like 'usd'" },
            13: { "title": "To Convert a Currency", "subtitle": "Please enter a valid amount like '100'" },
            20: { "title": "To Add a Currency", "subtitle": "cur add [currency]" },
            21: { "title": "To Add a Currency", "subtitle": "Please enter a valid abbreivation like 'usd'" }
        }

    def __init__(self, args, setting, toEdit=False):
        self.args = args
        self.setting = setting
        self.status_code = 0
        self._msgs = []
        self._parse(toEdit)

    def _parse(self, toEdit):
        if not toEdit:
            self._parse_base()
            self._parse_amount()
        else:
            self._parse_cur()

        if self.status_code == 0: self.status_code = 1

    # for editting
    def _parse_cur(self):
        op = self.args[0]

        if op == "add":
            try:
                cur = self.args[1].lower()
            except:
                self.status_code = 20
                self._msgs.append( self.response[self.status_code] )
                return

            curs = self.setting.bases()
            cur = re.sub("[^a-z]", "", cur)
            matches = None if not cur else filter(lambda x: bool( re.match("^{0}".format(cur), x) ), curs)

            if not matches:
                self.status_code = 21
                self._msgs.append( self.response[self.status_code] )
                return
        elif op == "del":
            self.args.append(None)

    def _parse_base(self):
        try:
            base = self.args[0]

            if base == 'add' or base == 'del':
                self.status_code = 12
                return
        except:
            self.status_code = 10
            self._msgs.append(self.response[self.status_code])
            return

        bases = self.setting.bases()

        if base not in bases:
            self.status_code = 11
            self._msgs.append( self.response[self.status_code] )
            return

    def _parse_amount(self):
        if self.status_code != 0: return

        try:
            amount = float(self.args[1])
        except:
            self.status_code = 13
            self._msgs.append(self.response[self.status_code])
            return

    def gen_msgs(self):
        """
        :rtype: List[Hash]
        """
        return self._msgs

    def gen_args(self):
        if self.status_code != 1: raise Exception("Wrong operation!")

        return [self.args[0], self.args[1]]


class APIWrapper:
    def __init__(self, url):
        self.url = url
        self.msg = ""
        self.status_code = 200
        self.rt_msg = ""

    def access(self):
        r = web.get(url=self.url)

        try:
            r.raise_for_status()
        except:
            self.msg = "Internal Error"
            self.status_code = r.status_code
            self.rt_msg = r.reason

            print(self.status_code, self.msg, self.rt_msg)
            return

        return json.loads(r.text)


class RateManager:
    def __init__(self):
        url = 'https://tw.rter.info/capi.php'
        self.aw = APIWrapper(url)

    def retrieve(self):
        raw_data = self.aw.access()
        rates = {re.sub('USD(?<!USD$)', '', k).lower(): v['Exrate'] for k, v in raw_data.items()}
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        return (rates, timestamp)


class Setting(object):
    def __init__(self, wf):
        self.wf = wf
        self.rm = RateManager()

    def bases(self):
        return self.wf.settings['defaults']['rates'].keys()

    def rates(self):
        return self.wf.settings['defaults']['rates']

    def curs(self):
        return self.wf.settings['defaults']['curs']


class Converter(Setting):
    def __init__(self, wf):
        super(Converter, self).__init__(wf)

        if 'defaults' not in self.wf.settings:
            self.wf.settings['defaults'] = {}
            self.wf.settings['defaults']['curs'] = ['twd']
            self.wf.settings.save()

    def renew_rate(self):
        if self._isexpired():
            rates, timestamp = self.rm.retrieve()
            self.wf.settings['defaults']['rates'] = rates
            self.wf.settings['defaults']['timestamp'] = timestamp
            self.wf.settings.save()


    def gen_msgs(self, base, amount):
        result = []
        curs = self.curs()
        rates = self.rates()

        for cur in curs:
            if cur == base and len(curs) > 1: continue

            ratio = rates[cur] / rates[base]
            ratio = '{0:.4f}'.format(ratio).rstrip('0').rstrip('.')

            total = float(amount) * float(ratio)
            total = '{0:.4f}'.format(total).rstrip('0').rstrip('.')

            title = '{0} {1}'.format(total, cur.upper())
            subtitle = '{0} : {1} = 1.0 : {2}'.format(base.upper(), cur.upper(), ratio)
            icon = './assets/flags/{0}.png'.format(cur)

            result.append({
                "title": title,
                "subtitle": subtitle,
                "copytext": total,
                "arg": total,
                "icon": icon,
                "valid": True
                })

        return result

    def _isexpired(self):
        present = datetime.now()

        last_time = self.wf.settings['defaults'].get('timestamp', None) or "2000-01-01 12:00:00"
        last_time = datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S')

        return (present - last_time) >= timedelta(days=1)


class Editor(Setting):
    def __init__(self, wf):
        super(Editor, self).__init__(wf)

    def gen_msgs(self, *args):
        result = []
        op = args[0]

        if op == "add":
            cur = args[1]
            cur = re.sub("[^a-z]", "", cur)
            matches = filter(lambda x: bool( re.match("^{0}".format(cur), x) ), self.bases())
        else:
            matches = self.curs()

        d = { "add": "Add", "del": "Delete"}

        for match in matches:
            title = "To {0} {1}".format(d[op], match.upper())
            subtitle = "Press enter to proceed"
            arg = "{0} {1}".format(op, match)
            icon = './assets/flags/{0}.png'.format(match)

            result.append({
                "title": title,
                "subtitle": subtitle,
                "arg": arg,
                "icon": icon,
                "valid": True
                })

        return result


class Changer(Setting):
    def __init__(self, wf):
        super(Changer, self).__init__(wf)
        self.op = wf.args[0]
        self.cur = wf.args[1]

    def print_msgs(self):
        if self.op == 'add':
            v = 'added'
            pos = 'to'
        else:
            v = 'deleted'
            pos = 'from'

        print('{0} has been {1} {2} the list'.format(self.cur.upper(), v, pos))

    def execute(self):
        queue = deque(self.curs(), maxlen=6)

        try: queue.remove(self.cur)
        except: pass

        if self.op == 'add':
            queue.appendleft(self.cur)
        else:
            if not queue: queue.appendleft('twd')

        self.wf.settings['defaults']['curs'] = list(queue)
        self.wf.settings.save()
