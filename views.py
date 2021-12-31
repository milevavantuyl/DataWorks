import psycopg2
import psycopg2.extras
from flask import (render_template, url_for, request)
from theapp import app

# plotting
import json
import plotly
import plotly.express as px

# helper functions
from mileva_functions import (salaries, sectors_by_role, plotlyGOTest, plotlyPXTest)

@app.route('/')
def index():
    '''Route to the landing page of the Flask application'''
    return render_template('index.html', title = "Data Science Jobs")

@app.route('/searchJobs/', methods=['GET','POST'])
def jobform(): 
    '''Route to the page containing the job form'''
    return render_template('jobform.html', title = 'Job Search')

@app.route('/search/', methods = ['GET', 'POST'])
def search(): 
    '''Given values from a form, finds a list of top job results.'''

    # Gets the form values as a dictionary {<field1>: <value1>, <field2>: <value2>, ...}
    values = request.form.to_dict()

    # Print statements for debugging 
    print("form values:", values)
    print("jobtype:", values['jobtype'])

    # Set up dictionary cursor connected to dataworks database
    conn = psycopg2.connect(dbname='dataworks')
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Query to find and rank top job results 
    # @richard flesh out this query for your portion. 
    dict_cur.execute('''select * from jobs2 
                        where job_type =(%s) and salary_ceil is not null and salary_floor is not null and rating is not null
                        order by rating desc, salary_ceil desc, salary_floor desc
                        limit 250;''',
                    [values['jobtype']])
    jobResults = dict_cur.fetchall()

    # Close cursor and connection
    dict_cur.close()
    conn.close()

    # Populate the results.html page with list of job 
    return render_template('results.html', jobs = jobResults, query = values)

@app.route('/job/<id>', methods=['GET','POST'])
def showJob(id):
    '''Given a job id, create and display details and visualizations for the job''' 

    # Set up dictionary cursor connected to dataworks database
    conn = psycopg2.connect(dbname='dataworks')
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Query for the specified job
    dict_cur.execute('''select * from jobs2 where id =(%s);''',[id])
    job = dict_cur.fetchone()

    # Populate the jobs.html page with the job details and visualizations
    return render_template('jobs.html', job = job)

@app.route('/jobtypes/', methods=['GET','POST'])
def jobTypeComparison(): 
    '''Generate visualizations to compare different data science roles'''

    # Generates a boxplot of salaries for each role
    salary_boxplot = salaries()

    # Generates a barplot about the different sectors with data related jobs
    sectors_barplot = sectors_by_role()

    return render_template('jobtypes.html', title = 'Job Type Comparison', graph1 = salary_boxplot, graph2 = sectors_barplot)

@app.route('/test/', methods = ['GET', 'POST'])
def test(): 
    '''Basic method to test connection to database is set up properly'''

    conn = psycopg2.connect(dbname='dataworks')
    cur = conn.cursor()
    cur.execute('''select * from foo2;''')

    results = cur.fetchall()
    print(results)

    return f'<h1> Executed Search. Results: {results}</h1>'