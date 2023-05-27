from flask import Flask, redirect, url_for, render_template,request, abort, flash, session
from pymongo import MongoClient
cluster = MongoClient("mongodb+srv://hysol:lab6120!@cluster0.saxyuac.mongodb.net/?retryWrites=true&w=majority")
db = cluster["software_engineering"]
collection = db["test"]

app = Flask(__name__)
app.config["SECRET_KEY"] = "누구도알수없는보안이진짜최고인암호키"

#메인페이지
@app.route('/')
def index():
    return render_template('main_new.html')

#로그인
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        if collection.find_one({"_id":request.form['id']}):
            id = request.form['id']
            id_list = collection.find_one({"_id":id})
            if request.form['pw'] == id_list['password']:
                session['username'] = id
                flash('You have logged in successfully as {}'.format(id))
                return redirect(url_for('afterlogin'))
            else:
                flash("올바르지 않은 비밀번호입니다!")
                return render_template('login_new.html')
        else:
            flash("존재하지 않는 아이디입니다! 회원가입 창으로 이동합니다.")
            return render_template('signup_new.html') 
    else:
        return render_template('login_new.html')  

# 회원가입 
@app.route('/signup',methods = ['POST', 'GET'])
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
            return render_template('signup_new.html')
        
         # 이미 존재하는 id인지 확인
        existing_user = collection.find_one({"_id": id})
        if existing_user:
            flash("이미 존재하는 id입니다.")
            return redirect(url_for('login'))  
        
        collection.insert_one({"_id": id, "pw": password, "name": username, "coin" : 0, "money" : 0})
        flash("회원가입해주셔서 감사합니다! 로그인 창으로 이동합니다.")
        return redirect(url_for('login'))   
    else :
        return render_template('signup_new.html')


@app.route('/afterlogin', methods=['GET','POST'])
def afterlogin():
    username = session['username']
    if request.method == 'POST':
        username = session['username']
        
    else:
        return render_template('main_after_login.html', value = username) 

@app.route('/mypage')
def mypage():
    username = session['username']
    user_info = collection.find_one({"_id":username})
    coin = user_info["coin"]
    money = user_info["money"]
    
    if request.method == 'POST':
        username = session['username']
        
    else:
        return render_template('mypage.html', username=username, coin = coin, money = money) 
    
@app.route('/buycoin')
def buycoin():
    if request.method == 'POST':
        username = session['username']
    else:
        return render_template('main_after_login.html') 

@app.route('/sellcoin')
def sellcoin():
    if request.method == 'POST':
        username = session['username']
    else:
        return render_template('main_after_login.html') 

@app.route('/add_money', methods=['GET','POST'])
def add_money():
    username = session['username']
    user_info = collection.find_one({"_id":username})
    coin = user_info["coin"]
    money = user_info["money"]
    
    if request.method == 'POST' :
        add_money = int(request.form['addmoney'])
        if add_money<1:
            flash("1원보다 적은 금액은 입금할 수 없습니다!")
            return redirect(url_for('add_money')) 
        else:
            money += add_money
            collection.update_one({"_id": username}, {"$set": { "money": money } })
            flash("{}원이 정상적으로 입금되었습니다!".format(add_money))
            return redirect(url_for('mypage')) 
            
    else:
        return render_template('add_money.html', username=username, coin = coin, money = money)
    

@app.route('/withdraw', methods=['GET','POST'])
def withdraw():
    username = session['username']
    user_info = collection.find_one({"_id":username})
    coin = user_info["coin"]
    money = user_info["money"]
    
    if request.method == 'POST' :
        withdraw = int(request.form['withdraw'])
        if withdraw<1:
            flash("1원보다 적은 금액은 출금할 수 없습니다!")
            return redirect(url_for('withdraw')) 
        elif money<withdraw:
            flash("계좌 잔액보다 많은 금액은 출금할 수 없습니다!")
            return redirect(url_for('withdraw')) 
        
        else:
            money -= withdraw
            collection.update_one({"_id": username}, {"$set": { "money": money } })
            flash("{}원이 정상적으로 출금되었습니다!".format(withdraw))
            return redirect(url_for('mypage')) 
            
    else:
        return render_template('withdraw.html', username=username, coin = coin, money = money)
  


# @app.route('/success')
# def success():
#     return 'You have logged in successfully'
#     return render_te

#회원전용기능 알림 메세지
@app.route('/loginfirst')
def loginfirst():
    flash('로그인 후에 이용할 수 있는 기능입니다!')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug = True)
