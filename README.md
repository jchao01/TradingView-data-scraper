# TradingView Chart Data Extractor

## Video Tutorial

How-to screen recording: https://d.pr/v/VGCDNf

The resulting file from the tutorial above: https://d.pr/f/bnQ75v

Ensure that you zoom/pan such that the oldest date you desire is visible on TradingView before publishing the chart. Too many indicators or too low a time resolution will increase the data points and potentially overload the free server. Avoid this by hosting/running the script on your local machine or scraping multiple times with fewer indicators and manually combine the CSV afterwards.

## Usage

Simply append the URL of a chart/idea published on TradingView to the link below. This is not the URL of a security's chart, but the URL for a user-published chart: https://tradingview-data.herokuapp.com/quotes?url=

i.e. for this chart: https://www.tradingview.com/chart/SPY/vjYfwgMu-SPY-Export-Test/

You'd use: https://tradingview-data.herokuapp.com/quotes?url=https://www.tradingview.com/chart/SPY/vjYfwgMu-SPY-Export-Test/

## Install
  ```
  pip3 install virtualenv
  python3 -m venv .
  source bin/activate
  pip3 install -r requirements.txt
  git init
  heroku create
  heroku git:remote -a projectname
  heroku stack:set heroku-16
  heroku buildpacks:add https://github.com/jontewks/puppeteer-heroku-buildpack.git
  heroku buildpacks:add heroku/python
  git add .
  git commit -am 'fix'
  git push heroku master
  ```
