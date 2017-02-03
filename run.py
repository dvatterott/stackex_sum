#!/usr/bin/env python

from Web_App import app
app.run(debug = True,use_reloader=False, host="0.0.0.0",port=5000)
#app.run(debug = True)
