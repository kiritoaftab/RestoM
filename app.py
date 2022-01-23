# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///resto.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
db= SQLAlchemy(app)

#global variables
bill= 0
noi={}
serr=False

# Schema
class Register(db.Model):
    name= db.Column(db.String(20),nullable=False)
    email=db.Column(db.String(20),primary_key=True)
    phone=db.Column(db.Integer,nullable=False)
    company=db.Column(db.String(20),nullable=False)
    branch = db.Column(db.String(20), nullable=False)
    password=db.Column(db.String(20),nullable=False)

    def __repr__(self) -> str:
        return f"{self.email} - {self.company} - {self.branch}"

#Schema
class Menu(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    item = db.Column(db.String(20), nullable=False)
    category=db.Column(db.String(20),nullable=False)
    desc = db.Column(db.String(200), nullable=False)
    prize=db.Column(db.Integer,nullable=False)
    cid=db.Column(db.Integer,nullable=False)
    def __repr__(self) -> str:
        return f"{self.sno} - {self.item} - {self.prize}-{self.cid}"

#Schema
class Company(db.Model):
    cid=db.Column(db.Integer,primary_key=True)
    company=db.Column(db.String(20),nullable=False)
    branch=db.Column(db.String(20),nullable=False)

#Schema
class Customer(db.Model):
    custid=db.Column(db.Integer,primary_key=True)
    cname=db.Column(db.String(20),nullable=False)
    company = db.Column(db.String(20), nullable=False)
    branch = db.Column(db.String(20), nullable=False)

#Schema
class Orders(db.Model):
    oid=db.Column(db.Integer,primary_key=True)
    custid=db.Column(db.Integer,nullable=False)
    item=db.Column(db.String(20),nullable=False)
    noi=db.Column(db.Integer,nullable=False)
    sno=db.Column(db.Integer,nullable=False)
    cid=db.Column(db.Integer,nullable=False)
    def __repr__(self) -> str:
        return f"{self.oid} - {self.item} - {self.noi}-{self.sno}"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/main/<company>",methods=['GET','POST'])
def maain(company):
    # return f"I am {company} Page"
    comobj = Company.query.filter_by(company=company).first()
    cid=comobj.cid
    if request.method =="POST":
        item=request.form['item']
        category=request.form['category']
        desc=request.form['desc']
        prize=request.form['prize']
        menobj=Menu(item=item,category=category,desc=desc,prize=prize,cid=cid)
        db.session.add(menobj)
        db.session.commit()
    allmenus = Menu.query.filter_by(cid=cid).all()
    print(allmenus)
    return render_template("company.html",company=company,allmenus=allmenus,cid=cid)


@app.route("/main/<company>/delete/<int:sno>")
def delete(sno,company):
    todel=Menu.query.filter_by(sno=sno).first()
    db.session.delete(todel)
    db.session.commit()
    return redirect("/main/"+company)

@app.route("/main/<company>/update/<int:sno>",methods=['GET',"POST"])
def update(sno,company):
    if request.method=="POST":
        # Getting details from FORM
        if request.method == "POST":
            item = request.form['item']
            category = request.form['category']
            desc = request.form['desc']
            prize= request.form['prize']
            # Insert Operation
            toupd = Menu.query.filter_by(sno=sno).first()
            toupd.item=item
            toupd.category = category
            toupd.desc=desc
            toupd.prize=prize
            db.session.add(toupd)
            db.session.commit()
            return redirect("/main/"+company)
        # end of insert
    toupd = Menu.query.filter_by(sno=sno).first()

    return render_template('update.html',toupd=toupd,company=company)


@app.route("/admin", methods=['GET','POST'])
def adminlog():
    validuser = False
    incorrectpassword = False
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        try:
            regobj = Register.query.filter_by(email=email).first()

            if regobj.password == password:
                validuser = True
                print('Valid User')
            else:
                incorrectpassword=True
                print('Incorrect Password')
        except:
            validuser=False
            print('Invalid User')
    if validuser:
        regobj = Register.query.filter_by(email=email).first()
        name=regobj.name
        company=regobj.company
        branch=regobj.branch

        return redirect("/main/"+ company)
    return render_template("admin.html",validuser=validuser,incorrectpassword=incorrectpassword)

@app.route("/customer",methods=["GET","POST"])
def customerlog():
    if request.method =="POST":
        cname=request.form['cname']
        company=request.form['company']
        branch=request.form['branch']
        cusobj=Customer(cname=cname,company=company,branch=branch)
        db.session.add(cusobj)
        db.session.commit()
        custid = str(cusobj.custid)
        return redirect("/customer/menu/"+custid)

    return render_template("customer.html")

@app.route("/customer/menu/<int:custid>")
def menu(custid):
    noitem=False
    custobj = Customer.query.filter_by(custid=custid).first()
    branch=custobj.branch
    company=custobj.company

    comobj=Company.query.filter_by(company=company,branch=branch).first()
    cid=comobj.cid
    print(comobj)

    menobj=Menu.query.filter_by(cid=cid).all()
    category=[]
    for items in menobj:
        if items.category  not in category:
            category.append(items.category)
    print(menobj)
    print(category)

    try:
        ordobj=Orders.query.filter_by(custid=custid).all()
    except:
        noitem=True
    print(ordobj)
    return render_template("menu.html",branch=branch,company=company,menobj=menobj,
                           category=category,custid=custid,bill=bill,noitem=noitem,ordobj=ordobj,cid=cid)


@app.route("/customer/menu/<int:custid>/cart/<int:sno>/<int:cid>",methods=["GET","POST"])
def cart(sno,custid,cid):
    global bill
    global noi

    menobj=Menu.query.filter_by(sno=sno).first()
    item=menobj.item
    prize=menobj.prize

    bill=bill+prize
    print(bill)
    try:

        if item not in noi:
            noi[item]=1
        else:
            noi[item]+=1
        #update
        ordobj = Orders.query.filter_by(sno=sno, custid=custid, cid=cid).first()
        ordobj.noi = noi[item]
        db.session.add(ordobj)
        db.session.commit()
    except:
        #insert
        ordobj = Orders(sno=sno, custid=custid, item=item,noi=noi[item],cid=cid)
        db.session.add(ordobj)
        db.session.commit()

    return redirect("/customer/menu/"+str(custid))

@app.route("/customer/menu/<int:custid>/remove/<int:sno>/<int:cid>",methods=["GET","POST"])
def remove(sno,custid,cid):
    global bill
    global noi
    global serr
    try:
        ordobj=Orders.query.filter_by(sno=sno,custid=custid,cid=cid).first()
        menobj = Menu.query.filter_by(sno=sno).first()
        item = menobj.item
        prize=menobj.prize
        if item not in noi:
            serr=True
        else:
            noi[item] -= 1
            bill -= prize
            if noi[item]==0:
                db.session.delete(ordobj)
                db.session.commit()
            else:
                ordobj.noi=noi[item]
                db.session.add(ordobj)
                db.session.commit()

    except:
        serr=True
        print(serr)
    return redirect("/customer/menu/" + str(custid))

@app.route("/main/<company>/order/<cid>")
def orders(company,cid):
    customer=[]
    allord=Orders.query.filter_by(cid=cid).all()
    for order in allord:
        if order.custid not in customer:
            customer.append(order.custid)

    print(allord)
    return render_template("order.html",company=company,cid=cid,allord=allord,customer=customer)

@app.route("/payment/<int:custid>")
def payment(custid):
    global bill
    return render_template("payment.html",bill=bill,custid=custid)

@app.route("/payment/<int:custid>/paid")
def paid(custid):
    global bill
    bill=0
    allord=Orders.query.filter_by(custid=custid).all()
    for order in allord:
        db.session.delete(order)
        db.session.commit()

    custobj=Customer.query.filter_by(custid=custid).first()
    db.session.delete(custobj)
    db.session.commit()
    return redirect("/")
@app.route("/register", methods=['GET','POST'])
def register():
    # Getting details from FORM
    if request.method == "POST":
        name = request.form['name']
        email = request.form['email']
        phone =request.form['phone']
        company=request.form['company']
        branch=request.form['branch']
        password=request.form['password']
        regobj = Register(name=name,email=email,phone=phone,company=company,branch=branch,password=password)
        db.session.add(regobj)
        db.session.commit()
        comobj = Company(company=company, branch=branch)
        db.session.add(comobj)
        db.session.commit()
    allRegister = Register.query.all()
    print(allRegister)
    return render_template("register.html")
# Press the green button in the gutter to run the script.
if __name__ == '__main__':
   app.run(debug=True)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
