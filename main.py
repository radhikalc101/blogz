from flask import Flask, request, redirect, render_template,flash,session
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash, check_pw_hash

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:radhikablogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'EakyJe4LYRecryCLMQAqiqiT'

#creating table in databate through python 
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, body,owner):
        self.title = title
        self.body = body
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    pw_hash = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')


    def __init__(self, username, password):
        self.username = username
        self.pw_hash = make_pw_hash(password)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        errorMessage=''
        if username == '' or password == '':
            errorMessage = "User Name and/or Password can not be empty"
            return render_template('login.html',errorMessage=errorMessage)
        else:    
            user = User.query.filter_by(username=username).first()
            if user and check_pw_hash(password, user.pw_hash):
                session['username'] = username
                return redirect('/newpost')  
            else:
                errorMessage = "Invalid user/password"
                return render_template('login.html',errorMessage=errorMessage)
    else:     
        return render_template('login.html', errorMessage='')


@app.route("/signup", methods=['POST','GET'])
def signup():
    if request.method == 'POST':
        user_name = request.form["username"]
        password = request.form["password"]
        varify_password = request.form["verifypassword"]

        user_name = user_name.strip()
        password = password.strip()
        varify_password = varify_password.strip()

        usernameError = ''
        if user_name == '' or len(user_name) > 20 or  len(user_name) < 3:
            usernameError = "That's not a valid username"
            
        passwordError = ''
        if password == '' or len(password) > 20 or  len(password) < 3:
            passwordError = "That's not a valid password"

        verifypasswordError = ''
        if varify_password == '' or password != varify_password:
            verifypasswordError= " Password does not match"  

        if usernameError == '' and passwordError == '' and verifypasswordError == '':
            existing_user = User.query.filter_by(username=user_name).first()
            if not existing_user:
                new_user = User(user_name, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = user_name
                return redirect('/newpost')
            else:
                errorMsg = "A user with that username already exists"
                # TODO - user better response messaging
                return render_template('signup.html', existing_user_errormsg=errorMsg)
        else:
            return render_template("signup.html",username=user_name,usernameError=usernameError,passwordError=passwordError,verifypasswordError=verifypasswordError)
                            #"signup.html",'/?username='  remaing from top line
    
    return render_template('signup.html')
    


@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    #owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST': 
        title = request.form['title']
        body = request.form['body']
        titleError = ""
        bodyError =""
        if title == "" or body == "":
            if title == "":
                titleError = 'Please enter the title'
            if body == "":
                bodyError='Please enter the body'
            return render_template('newpost.html',titileMessage=titleError, bodyMessage=bodyError)
        else:
            #newBlog = Blog(title, body,owner)
            owner = User.query.filter_by(username=session['username']).first()
            newBlog = Blog(title, body, owner)
            db.session.add(newBlog)
            db.session.commit() 
            #return redirect("/blog?user=" + user.username)           
            return redirect("/blog?id=" + str(newBlog.id))
    elif 'username' in session:
        return render_template('newpost.html',titileMessage="", bodyMessage="") 
    else:
        return redirect('/login')  

@app.route("/logout")
def logout():
    del session['username']
    return redirect("/allBlogs")
    
@app.route('/allBlogs')
def blogs():
    blogs = []
    userId = request.args.get('user')
    if userId:
        #print("userid..."+str(userId))
        user = User.query.filter_by(id=userId).first()
        blogs = Blog.query.filter_by(owner_id=user.id)
        return render_template('singleUser.html',blogs=blogs,user=user,title="Blog Posts!")
    else :
        blogs = Blog.query.all()
       
        users = {}
        for blog in blogs:
            if not users.get(blog.owner_id):
                user = User.query.filter_by(id=blog.owner_id).first()
                users[user.id] = user
        #print("BLOGS and USERS.....")
        #print(blogs)
        #print(users)
        #users['1'] = User{id='1', username='Rishi',password='', blogs=[]}
        #users['2'] = User{id='2', username='Teju',password='', blogs=[]}
        return render_template('blog.html',blogs=blogs,users=users, title="Blog Posts!")

@app.route('/blog')
def blog():
    blogId = request.args.get('id')

    blog = Blog.query.filter_by(id=blogId).first()
    blogUser = User.query.filter_by(id=blog.owner_id).first()

    return render_template('view_blog.html',blog=blog, user=blogUser, title="Blog Posts!")

@app.before_request
def require_login():
    print('inside before request..'+request.endpoint)
    allowed_routes = ['login','signup','blogs','index','static','blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route("/")
def index():
    
    all_users = User.query.all()
    print(all_users)
    return render_template('index.html', users=all_users)

if __name__ == '__main__':
    app.run()