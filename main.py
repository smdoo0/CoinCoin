from flask import Flask, redirect, url_for, render_template,request, abort, flash, session
from bson.objectid import ObjectId
from pymongo import MongoClient
cluster = MongoClient("mongodb+srv://smdoo:Me2sChTXYh49P3Lk@cluster0.ydrdzo1.mongodb.net/?retryWrites=true&w=majority")
db = cluster["software_engineering"]
collection = db["test"]
#초기 코인 정보 db
initialCoin = db["initialCoin"]
#initialCoin.insert_one({"_id": 'initialCoin', "number": 100, "price": 100})
postedCoin = db["postedCoin"]
#거래 history db
history = db["history"]


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
            if request.form['password'] == id_list['pw']:
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
    
@app.route('/buycoin_initial', methods=['GET','POST'])
def buycoin_initial():
    #로그인 유지용 username 저장
    username = session.get('username')
    user_info = collection.find_one({"_id":username})
    coin = user_info["coin"]
    money = user_info["money"]
    
    #세션에 저장된 유저가 post한 코인 정보 업데이트
    initial_list = initialCoin.find_one({"_id":'initialCoin'})
    cursor = postedCoin.find()
    post_list = []
    for post in cursor:
        post_list.append(post)  #post_list 에는 postedCoin db에 있는 딕셔너리들 저장
        
    session["initial_number"] = initial_list['number']
    session["initial_price"] = initial_list['price']
    initial_number = session["initial_number"]   #초기 코인 남은 개수
    initial_price = session["initial_price"]     #초기 코인 개당 가격
    initial_number = initial_list['number']
    render_template('buycoin.html', username=username, initial_number=initial_list['number'], coin = coin, money = money, post_list=post_list)
    
    if request.method == 'POST':
        
        initial_buy = int(request.form['initialbuy'])
        if initial_buy <1:
            flash("1개보다 적은 수의 코인은 구매할 수 없습니다!")
            return redirect(url_for('buycoin_initial')) 
        
        elif money<initial_buy*100:
            flash("계좌 잔액이 부족합니다!")
            return redirect(url_for('buycoin_initial')) 
        
        else:
            money -= initial_buy*100
            initial_number -= initial_buy
            coin += initial_buy
            collection.update_one({"_id": username}, {"$set": { "money": money, "coin":  coin} })
            initialCoin.update_one({"_id": 'initialCoin'},{"$set": { "number": initial_number} })
            flash("{}개의 코인을 정상적으로 구매하셨습니다!".format(initial_buy))
            
            #세션에 저장된 유저가 post한 코인 정보 업데이트
            initial_list = initialCoin.find_one({"_id":'initialCoin'})
            cursor = postedCoin.find()
            post_list = []
            for post in cursor:
                post_list.append(post)  #post_list 에는 postedCoin db에 있는 딕셔너리들 저장
            
            return render_template('buycoin.html', username=username, initial_number=initial_list['number'], coin = coin, money = money, post_list=post_list)
            
    else:
        return render_template('buycoin.html', username=username, initial_number=initial_list['number'], coin = coin, money = money, post_list=post_list)


@app.route('/buycoin_post', methods=['GET','POST'])
def buycoin_post():
    #로그인 유지용 username 저장
    username = session.get('username')
    user_info = collection.find_one({"_id":username})
    coin = user_info["coin"]
    money = user_info["money"]
    
    #세션에 저장된 유저가 post한 코인 정보 업데이트
    initial_list = initialCoin.find_one({"_id":'initialCoin'})
    cursor = postedCoin.find()
    post_list = []
    for post in cursor:
        post_list.append(post)  #post_list 에는 postedCoin db에 있는 딕셔너리들 저장
        
    session["initial_number"] = initial_list['number']
    session["initial_price"] = initial_list['price']
    initial_number = session["initial_number"]   #초기 코인 남은 개수
    initial_price = session["initial_price"]     #초기 코인 개당 가격
    initial_number = initial_list['number']
    render_template('buycoin.html', username=username, initial_number=initial_list['number'], coin = coin, money = money, post_list=post_list)
    
    if request.method == 'POST':
        
        buypostId = request.form['buypostid']
        buypost_list = postedCoin.find_one({'_id':ObjectId(buypostId)})
    
        price = int(buypost_list['Price/coin'])
        quant = int(buypost_list['Quantity'])
        Seller = buypost_list['Seller']
        Seller_info = collection.find_one({"_id":Seller})
        seller_money = Seller_info['money']
        seller_coin = Seller_info['coin']
        
        
        if money<price*quant:
            flash("계좌 잔액이 부족합니다!")
            return redirect(url_for('buycoin_initial')) 
        
        else:
            money -= price*quant
            coin = coin+quant
            collection.update_one({"_id": username}, {"$set": { "money": money, "coin":  coin} })
            collection.update_one({"_id": Seller}, {"$set": { "money": seller_money+price*quant} })
            postedCoin.delete_one({'_id':ObjectId(buypostId)})
            history.insert_one({"price/coin": price, "quantity": quant})
            
            flash("{}개의 코인을 정상적으로 구매하셨습니다!".format(quant))
            return redirect(url_for('buycoin_initial')) 
            
    
    else:
        return redirect(url_for('buycoin_initial')) 



#코인 판매 페이지(post)
@app.route('/sellcoin', methods = ['POST', 'GET'])
def sellcoin():
    #로그인 유지용 username 저장
    username = session.get('username')
    user_list = collection.find_one({"_id":username}) # 현재 로그인 된 유저의 정보
    user_coins = user_list['coin']                # 유저의 보유 코인 개수
    user_money = user_list['money']               # 유저의 잔액
    if request.method == 'POST':
        number = int(request.form.get('number'))  #판매할 코인 개수
        price = int(request.form.get('price'))   #판매할 코인의 개당 가격

        if user_coins < number:
            flash("판매하려는 코인 개수가 보유 수량보다 많습니다.")
            return render_template('sellcoin.html', username=username, user_coins=user_coins, user_money=user_money)
        
        # postedCoin db에 정보 저장
        total_price = number * price
        coin_info = {"Seller": username, "Quantity": number, "Price/coin": price, "total_price": total_price}
        postedCoin.insert_one(coin_info)
        user_coins -= number
        collection.update_one({"_id": username}, {"$set": {"coin":  user_coins} })
        flash("정상적으로 post 되었습니다!")
        return render_template('sellcoin.html', username=username, user_coins=user_coins, user_money=user_money)
    else:
        return render_template('sellcoin.html', username=username, user_coins=user_coins, user_money=user_money)

#입금
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
    

#출금
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
  
  
@app.route('/coinstate')
def coinstate():
    
    return render_template('coinstate.html')


#회원전용기능 알림 메세지
@app.route('/loginfirst')
def loginfirst():
    flash('로그인 후에 이용할 수 있는 기능입니다!')
    return redirect(url_for('login'))

#로그아웃
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('로그아웃 되었습니다.')
    return redirect('/')


if __name__ == '__main__':
    app.run(debug = True)
