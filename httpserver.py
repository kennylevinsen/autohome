import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
    	page = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
<meta content="yes" name="apple-mobile-web-app-capable" />
<meta content="text/html; charset=utf-8" http-equiv="Content-Type" />
<meta content="minimum-scale=1.0, width=device-width, maximum-scale=0.6667, user-scalable=no" name="viewport" />
<link href="static/css/style.css" rel="stylesheet" media="screen" type="text/css" />
<script src="static/javascript/functions.js" type="text/javascript"></script>
<title>Title of your page</title>
<meta content="keyword1,keyword2,keyword3" name="keywords" />
<meta content="Description of your page" name="description" />
</head>

<body>

<div id="topbar">
</div>
<div id="content">
</div>
<div id="footer">
	<!-- Support iWebKit by sending us traffic; please keep this footer on your page, consider it a thank you for my work :-) -->
	<a class="noeffect" href="http://snippetspace.com">iPhone site powered by iWebKit</a></div>

</body>

</html>

    	"""
        self.write(page)

application = tornado.web.Application([
	(r'/static/(.*)', tornado.web.StaticFileHandler, {'path': 'static_http'}),
	(r'/', MainHandler)
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
