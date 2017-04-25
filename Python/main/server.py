import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import base64,ocr
from tornado.options import define, options
from selenium import webdriver
import sc_ds
define("port", default=8000, help="run on the given port", type=int)


class Process(tornado.web.RequestHandler):
    def post(self):
        type = self.get_argument('type')
        if type=='image':
            image = self.get_argument('image')
            image=base64.b64decode(image)
            f=open('image.jpg','w')
            f.write(image)
            f.close()
            ocr.myocr('image.jpg')
            f=open('result','r')
            result=f.read()
            result=','.join(result.split('\n')[0:3])
            data={}
            if(result[0]=='1'):
                pass
            elif(result[0]=='2'):
                sc_ds.get_captcha(driver)
                f=open('yzm.png')
            elif(result[0]=='5'):
                pass
            self.write(data)

        elif type=='text':
            text = self.get_argument('text')
            text = text.split(',')
            #print text
            if (text[0] == '1'):
                pass
            elif (text[0] == '2'):
                sc_ds.get_result(driver, text[0], text[1], text[2], text[3])
            elif (text[0] == '5'):
                pass
            self.write('ok')

if __name__ == "__main__":
    driver = webdriver.Chrome()
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", Process)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
