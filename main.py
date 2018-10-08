from flask import Flask, request, redirect, render_template,flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:beprotective@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

#creating table in databate through python 
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST': 
        title = request.form['title']
        body = request.form['body']

        if (title == "" or body == ""):
            #flash('Please enter the title', 'Please enter the body')
            return redirect('/newpost')
        else:
            newBlog = Blog(title, body)
            db.session.add(newBlog)
            db.session.commit()
            return redirect("/blog?id=" + str(newBlog.id))
    else:
        return render_template('newpost.html') 


@app.route('/blog')
def index():
    blogId = request.args.get('id')
    if blogId:
        blog = Blog.query.filter_by(id=blogId).first()
        return render_template("view_blog.html",blog=blog)

    blogs = Blog.query.all()
    return render_template('blog.html',blogs=blogs, title="Build A Blog")

if __name__ == '__main__':
    app.run()