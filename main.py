from flask import Flask, redirect, url_for, render_template,request, abort, flash, session
from bson.objectid import ObjectId
from pymongo import MongoClient
from datetime import datetime
import json
cluster = MongoClient("mongodb+srv://smdoo:Me2sChTXYh49P3Lk@cluster0.ydrdzo1.mongodb.net/?retryWrites=true&w=majority")
db = cluster["software_engineering"]
collection = db["test"]
#초기 코인 정보 db
initialCoin = db["initialCoin"]
#initialCoin.insert_one({"_id": 'IC', "number": 100, "price": 100})
postedCoin = db["postedCoin"]
#거래 history db
history = db["history"]


app = Flask(__name__)
app.config["SECRET_KEY"] = "누구도알수없는보안이진짜최고인암호키"

#메인페이지
@app.route('/')
def index():
    # history에 있는 정보 받아오기
    cursor = db.history.find()
    history_list = []
    graphdata = []
    for document in cursor:
        data = [document["date"], document["Price/coin"]]
        history_list.append(data)
    
    if len(history_list) > 10:
        for i in range(1, 11):
            graphdata.append(history_list[-i])    #최근 데이터 10개를 저장
    else:
        for i in range(len(history_list)):
            graphdata.append(history_list[-(i+1)])  #모든 최근 데이터를 저장
    
    return render_template('main_new.html', graphdata=graphdata)

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
    
    # history에 있는 정보 받아오기
    cursor = db.history.find()
    history_list = []
    graphdata = []
    for document in cursor:
        data = [document["date"], document["Price/coin"]]
        history_list.append(data)
    
    if len(history_list) > 10:
        for i in range(1, 11):
            graphdata.append(history_list[-i])    #최근 데이터 10개를 저장
    else:
        for i in range(len(history_list)):
            graphdata.append(history_list[-(i+1)])  #모든 최근 데이터를 저장
    
    
    return render_template('main_after_login.html', value = username, graphdata=graphdata) 

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

#코인 구매 페이지
@app.route('/buycoin', methods = ['POST', 'GET'])
def buycoin():
    #로그인 유지용 username 저장
    username = session.get('username')
    user_info = collection.find_one({"_id":username})
    coin = user_info["coin"]
    money = user_info["money"]

    #세션에 저장된 유저가 post한 코인 정보 업데이트
    cursor = db.postedCoin.find()
    post_list = []
    post_index = 1
    for document in cursor:
        data = {
            "post_index": post_index,
            "Seller": document["Seller"],
            "Quantity": document["Quantity"],
            "Price": document["Price/coin"],
            "total_price": document["total_price"]
        }
        current_post_id = document["_id"]
        postedCoin.update_one({"_id": current_post_id}, {"$set": { "post_index": post_index } })
        post_index += 1
        post_list.append(data)
    
    #marketplace에 있는 초기 코인 정보 업데이트
    initial_list = initialCoin.find_one({"_id":'IC'})
    initial_number = initial_list['number']
    
    if request.method == 'POST':
        
        #마켓플레이스의 초기 코인을 구매하는 경우
        if 'buy_initial_coin' in request.form:
            initial_buy = int(request.form['initialbuy'])   #구매하고자하는 초기 코인 개수
            if initial_buy <1:
                flash("1개 이상의 코인을 입력해주세요.")
                return redirect(url_for('afterlogin'))
            elif initial_buy > initial_number:
                flash("마켓에 남아있는 코인이 부족합니다.")
                return redirect(url_for('afterlogin'))
            elif money<initial_buy*100:
                flash("잔액이 부족합니다")
                return redirect(url_for('mypage'))
            else:
                money -= initial_buy*100
                initial_number -= initial_buy
                coin += initial_buy
                collection.update_one({"_id": username}, {"$set": { "money": money, "coin":  coin} })
                initialCoin.update_one({"_id": 'IC'},{"$set": { "number": initial_number} })
                flash("{}개의 코인을 정상적으로 구매하셨습니다!".format(initial_buy))
                return redirect(url_for('mypage'))

        # 유저가 post한 코인을 구매하는 경우
        # 1. 게시물 total_price가 보유 금액보다 비싸다면 구매 불가
        # 2. 구매 가능하면 유저 코인 개수와 잔고, seller 코인 개수와 잔고, post 정보 업데이트
        for i in range(1, post_index+1):
            buy_posted_coin_index = 'buy_posted_coin{}'.format(i)
            cancel_posted_coin_index = 'cancel{}'.format(i)
            if buy_posted_coin_index in request.form:  # i번 째 구매 버튼이 눌렸다면
                post_index_to_buy = i  # 클릭한 버튼의 post_index 값
                post_to_buy = postedCoin.find_one({"post_index": post_index_to_buy}) # 구매하고자 하는 post 정보
                quantity_to_buy = post_to_buy["Quantity"]
                total_price_to_buy = post_to_buy["total_price"]
                seller_name_of_post = post_to_buy["Seller"]

                seller_list = collection.find_one({"_id": seller_name_of_post})
                seller_coin = seller_list["coin"]
                seller_money = seller_list["money"]

                if money < total_price_to_buy:
                    flash("잔액이 부족합니다")
                    return redirect(url_for('mypage'))
                else:
                    money -= total_price_to_buy
                    coin += quantity_to_buy  # 구매한 유저의 잔액, 코인 개수 업데이트
                    collection.update_one({"_id": username}, {"$set": {"money": money, "coin":  coin}})

                    seller_money += total_price_to_buy       # 판매한 유저의 잔액 업데이트
                    collection.update_one({"_id": seller_name_of_post}, {"$set": {"money": seller_money}})

                    postedCoin.delete_one({"post_index": post_index_to_buy})  # 거래 완료된 post 삭제
                    now = datetime.now()
                    now_datetime =  "{}/{} {}시 {}분".format(now.month, now.day, now.hour, now.minute)
                    history.insert_one({"Price/coin": post_to_buy["Price/coin"], "Quantity": quantity_to_buy, "date": now_datetime})

                    flash("거래 성공!")
                    return redirect(url_for('mypage'))
            elif cancel_posted_coin_index in request.form:  # i번 째 삭제 버튼이 눌렸다면
                post_index_to_cancel = i  # 클릭한 버튼의 post_index 값
                post_to_cancel = postedCoin.find_one({"post_index": post_index_to_cancel})  # 취소하고자 하는 post 정보
                coin_to_return = post_to_cancel["Quantity"]
                seller_name_of_post = post_to_cancel["Seller"]

                seller_list = collection.find_one({"_id": seller_name_of_post})
                seller_coin = seller_list["coin"]
                seller_coin += coin_to_return
                
                postedCoin.delete_one({"post_index": post_index_to_cancel})  # post 삭제
                collection.update_one({"_id": username}, {"$set": {"coin": seller_coin}}) #유저 정보 업데이트
                flash("게시물이 삭제되었습니다.")
                return redirect(url_for('mypage'))
            
    
    else:
        return render_template('buycoin.html', username=username, initial_number=initial_number, documents=post_list, coin=coin, money=money)

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
