# Quotes

Heroku

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
