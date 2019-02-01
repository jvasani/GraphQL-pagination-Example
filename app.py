from flask import Flask
from flask import render_template
from flask import request,redirect
from flask import Flask
from flask_graphql import GraphQLView
from schema import schema, Department, Employee
from models import db_session, Department as DepartmentModel, Employee as EmployeeModel
from flask import Blueprint
from flask_paginate import Pagination, get_page_parameter

app = Flask(__name__)

mod = Blueprint('employee', __name__)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.form:
        department = DepartmentModel(name=request.form.get("department"))
        employee = EmployeeModel(name=request.form.get("name"),department=department)
        db_session.add(employee)
        db_session.commit() 
    return render_template("addEmployee.html")

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.form == 'POST' :
        return render_template('search_result.html')      
    return render_template('search.html')

@app.route('/search_result',methods=['GET', 'POST'])
def search_result():
    if request.form :
        search_name = request.form.get('name') 
        qry = db_session.query(EmployeeModel).filter(EmployeeModel.name.contains(search_name))
        data = qry.all()
        search = False
        q = request.args.get('q')
        if q:
            search = True
        page = request.args.get(get_page_parameter(), type=int, default=1)
        pagination = Pagination(page=page, total=db_session.query(EmployeeModel).filter(EmployeeModel.name.contains(search_name)).count(), search=search, record_name='Results')

        return render_template('list.html', data=data,pagination=pagination,page=page) 


@app.route('/list')
@app.route('/list/page/<int:page>')
def all_data(page=1):
    search = False
    q = request.args.get('q')
    if q:
        search = True
    page = request.args.get(get_page_parameter(), type=int, default=1)

    data = EmployeeModel.query.all()

    pagination = Pagination(page=page, total=db_session.query(EmployeeModel).filter(EmployeeModel.id).count(), search=search, record_name='Results')
    return render_template('list.html', data=data,pagination=pagination,page=page) 
    

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True # for having the GraphiQL interface
    )
)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
     app.run(debug=True)