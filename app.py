from flask import Flask, request, Response
from bs4 import BeautifulSoup
import json
import moment
import re
import asyncio
import pyppeteer
import nest_asyncio

nest_asyncio.apply()

pyppeteer.DEBUG = False
headless = True
# headless = False
args = [
    '--window-size=1024,768',
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--ignore-certificate-errors',
    '--disable-dev-shm-usage',
    '--single-process'
]

loop = asyncio.get_event_loop()
app = Flask(__name__)

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'
}


async def get_csv(url):
    browser = await pyppeteer.launch(headless=headless, ignoreHTTPSErrors=True, args=args, handleSIGINT=False,
                                     handleSIGTERM=False, handleSIGHUP=False)
    page = await browser.newPage()
    page.setDefaultNavigationTimeout(60000)
    await page.setViewport(dict(width=1024, height=768))
    await page.setUserAgent(headers['user-agent'])
    await page.goto(url)
    await page.waitForSelector('.pane-legend-title__container')
    content = await page.content()
    await page.close()
    await browser.close()
    return content


@app.route("/")
def index():
    return Response('{"status":"ok"}')


@app.route("/quotes")
def quotes():
    try:
        url = request.args.get('url')
        if url:
            url = request.args.get('url')
            content = loop.run_until_complete(get_csv(url))
            soup = BeautifulSoup(content, 'lxml')

            ind_titles = soup.findAll(attrs={"class": "pane-legend-line"})
            _ind_titles = []
            _ind_values = []
            for ind in ind_titles:
                name = ind.find(attrs={"class": "pane-legend-title__description"})
                values = ind.findAll(attrs={"class": "pane-legend-item-value-wrap"})
                _loc_values = []
                for val in values:
                    _loc_values.append(val.get_text())
                _ind_values.append(' '.join(list(map(str, _loc_values))))
                _ind_titles.append(name.get_text())

            json_string = soup.find(attrs={"class": "js-chart-view"})['data-options']
            parsed_string = json.loads(json_string)
            parsed_string = json.loads(parsed_string['content'])['panes']

            main = None
            indicators = []

            for item in parsed_string:
                for item2 in item['sources']:
                    if item2['type'] == 'MainSeries':
                        main = item2
                    elif item2['type'] == 'Study':
                        indicators.append(item2)
            title = 'Untitled'
            r = '\nno data\n'
            if main:
                title = soup.find(attrs={"class": "pane-legend-title__container"}).get_text()
                d = main['bars']['data']
                columns = ['time', 'open', 'high', 'low', 'close', 'vol', '%', 'id', 'timestamp']

                if (len(indicators)):
                    for i in indicators:
                        _name = i['metaInfo']['shortDescription']
                        for _n in range(len(i['data']['data'][0]['value'])):
                            _s = 1
                            for _i in i['data']['data']:
                                if _i['value'][_n] != 0 and _i['value'][_n] != 1:
                                    _s = 0
                                    break
                            if _s == 1:
                                for _i in i['data']['data']:
                                    _i['value'].pop(_n)
                                break

                        for name in _ind_titles:
                            s = 1
                            if not re.match('^' + str(_name), name):
                                s = 0
                            if 'source' in i['state']['inputs'] and not re.search(str(i['state']['inputs']['source']),
                                                                                  name):
                                s = 0
                            if 'length' in i['state']['inputs'] and not re.search(str(i['state']['inputs']['length']),
                                                                                  name):
                                s = 0
                            if 'increment' in i['state']['inputs'] and not re.search(
                                    str(i['state']['inputs']['increment']),
                                    name):
                                s = 0
                            if 'max value' in i['state']['inputs'] and not re.search(
                                    str(i['state']['inputs']['max value']),
                                    name):
                                s = 0
                            if 'start' in i['state']['inputs'] and not re.search(
                                    str(i['state']['inputs']['start']),
                                    name):
                                s = 0
                            for n in range(12):
                                if 'in_' + str(n) in i['state']['inputs'] and not re.search(
                                        str(i['state']['inputs']['in_' + str(n)]),
                                        name):
                                    s = 0

                            if s:
                                _name = name
                                break

                        count_columns = len(i['data']['data'][0]['value']) - 1

                        for number in range(count_columns):
                            columns.append('"' + _name + '"')

                # r = '"' + title + '"' + (',' * (len(columns) - 1)) + '\n'
                # r += ','.join(columns) + '\n'
                r = ','.join(columns) + '\n'

                i = 0
                close = None
                for item in d:
                    item['value'] = item['value'][0:6]
                    data_ind = []
                    procent = None
                    for item2 in indicators:
                        for item3 in item2['data']['data']:
                            if item['value'][0] == item3['value'][0]:
                                item3['value'] = list(map(str, item3['value']))
                                item3['value'].pop(0)
                                data_ind.append(','.join(item3['value']))
                                break
                    if close:
                        procent = round((item['value'][-2] - close) / (close / 100), 2)
                    close = item['value'][-2]
                    r += ','.join(list(map(str, item['value']))) + ',' + str(procent) + ',' + str(
                        i) + ',' + moment.unix(
                        item['value'][0] * 1000, utc=True).format("YYYY-MM-DD HH:mm:ss") + ',' + ','.join(
                        data_ind) + '\n'
                    i += 1
            title = re.sub(r'[^\w\d&]+', '_', title.strip()).strip()
            print(title)
            return Response(r, mimetype="text/csv",
                            headers={"Content-disposition": "attachment; filename=" + title + ".csv"})
        return '{"error":"no url parameter"}'
    except Exception as e:
        return '{"error":"' + str(e) + '"}'


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False, port=5000)
