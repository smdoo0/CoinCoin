from flask import Flask, redirect, url_for, render_template,request, abort, flash, session
from pymongo import MongoClient
cluster = MongoClient("mongodb+srv://smdoo:Me2sChTXYh49P3Lk@cluster0.ydrdzo1.mongodb.net/?retryWrites=true&w=majority")
db = cluster["software_engineering"]
collection = db["test"]

app = Flask(__name__)
app.config["SECRET_KEY"] = "누구도알수없는보안이진짜최고인암호키"

#메인페이지
@app.route('/')
def index():
    return render_template('main_new.html')

#login_new
@app.route('/login_new')
def login_new():
    return render_template('login_new.html')

#거래소
@app.route('/market')
def market():
    return render_template('market.html')

#마이페이지
@app.route('/mypage')
def mypage():
    return render_template('mypage.html')

#로그인 후 메인 페이지
@app.route('/main_after_login')
def main_after_login():
    return render_template('main_after_login.html')

#로그인
@app.route('/login_new', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        if collection.find_one({"_id":request.form['id']}):
            id = request.form['id']
            id_list = collection.find_one({"_id":id})
            if request.form['password'] == id_list['password']:
                session['id'] = id
                flash('You have logged in successfully as {}'.format(id))
                return render_template('main_after_login.html') 
            else:
                flash("올바르지 않은 비밀번호입니다!")
                return render_template('login_new.html')
        else:
            flash("존재하지 않는 아이디입니다! 회원가입 창으로 이동합니다.")
            return render_template('signup.html')
    else:
        return render_template('login_new.html')  

# 회원가입
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        # 폼 데이터에서 필드 값 추출
        username = request.form['username']
        id = request.form['id']
        password = request.form['password']
        password_confirm = request.form['password_confirm']
        
        # 비밀번호 확인
        if password != password_confirm:
            flash("비밀번호가 일치하지 않습니다.")
            return render_template('signup.html')
        
        # 이미 존재하는 id인지 확인
        existing_user = collection.find_one({"_id": id})
        if existing_user:
            flash("이미 존재하는 id입니다.")
            return render_template('signup.html')

        # MongoDB에 데이터 삽입
        collection.insert_one({"_id": id, "pw": password, "name": username})

        return redirect('/')  # 회원가입 후 메인 페이지로 리디렉션

    return render_template('signup.html')


#로그인 성공 메세지
@app.route('/success')
def success():
    return 'You have logged in successfully'
    return render_template('signup.html') 
#회원전용기능 알림 메세지
@app.route('/loginfirst')
def loginfirst():
    flash('로그인 후에 이용할 수 있는 기능입니다!')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug = True)