#coding=utf-8
from werkzeug.utils import secure_filename
from flask import Flask,render_template,jsonify,request
import time,os,base64,ocr,sc_gs

app = Flask(__name__)
UPLOAD_FOLDER='static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
basedir = os.path.abspath(os.path.dirname(__file__))
ALLOWED_EXTENSIONS = set(['txt','png','jpg','xls','JPG','PNG','xlsx','gif','GIF'])

# 用于判断文件后缀
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

# 用于测试上传，稍后用到
@app.route('/test/upload')
def upload_test():
    return render_template('index.html')

# 上传文件
@app.route('/api/upload',methods=['POST'],strict_slashes=False)
def api_upload():
    file_dir=os.path.join(basedir,app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    f=request.files['myfile']  # 从表单的file字段获取文件，myfile为该表单的name值
    if f and allowed_file(f.filename):  # 判断是否是允许上传的文件类型
        fname=secure_filename(f.filename)
        print fname
        ext = fname.rsplit('.',1)[1]  # 获取文件后缀
        unix_time = int(time.time())
        new_filename=str(unix_time)+'.'+ext  # 修改了上传的文件名
        path=os.path.join(file_dir,new_filename)
        f.save(path)  #保存文件到upload目录
        ocr.myocr(path)               #识别发票
        f=open('result','r')
        text=f.read()
        fpdm,fphm=text.split('\n')[0:2]
        token = base64.b64encode(new_filename)
        print token
        #return jsonify({"errno":0,"errmsg":"上传成功","token":token})
        return render_template('temp.html',fpdm=fpdm,fphm=fphm,path=os.path.join("/static/upload",new_filename))
    else:
        return render_template('index.html')

@app.route('/api/search',methods=['POST'],strict_slashes=False)
def api_search():
    form=request.form
    print form
    fpdm=form['fpdm']
    fphm=form['fphm']
    sc_gs.search(fpdm,fphm)
    return render_template('result.html',fpdm=fpdm,fphm=fphm)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')
