import psycopg2
import psycopg2.extras
import pandas as pd
import numpy as np

# graphing
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json

# wordcloud
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

################## Functions being used by views.py ####################

def sectors_by_role(): 
    ''' Gets sector information per role. Returns a side by side barplot as a json'''

    # Database connection
    conn = psycopg2.connect(dbname='dataworks')
    cur = conn.cursor()

    # Query
    cur.execute('''select job_type, sector, count(*) 
                from jobs2 
                group by (job_type, sector) 
                order by count desc;''')

    rows = cur.fetchall()

    # Data Frame
    sector_counts = pd.DataFrame(rows, columns = ['job_type', 'sector', 'count'])
    sector_counts = sector_counts.dropna(axis = 0)
    print(sector_counts.sector.unique())

    # plotly
    sector_barplot = px.bar(sector_counts, x="job_type", y="count", color="sector", barmode="group", title="Sector Variation across Job Type")

    return json.dumps(sector_barplot,cls=plotly.utils.PlotlyJSONEncoder)

def salaries(): 
    ''' Gets the salaries to be plotted via plotly as boxplots. Returns a boxplot as a json'''

    # Connect to database
    conn = psycopg2.connect(dbname='dataworks')
    cur = conn.cursor()

    # Query
    cur.execute('''select title, job_type, salary_floor, salary_ceil, round(((salary_floor + salary_ceil) / 2.0),2) as salary_midpoint from jobs2;''')
    rows = cur.fetchall()

    # Data Frame
    salary_ranges = pd.DataFrame(rows, columns = ['title', 'job_type', 'floor', 'ceil', 'salary'])

    # plotly figure
    fig = px.box(salary_ranges, x="job_type", y="salary", color="job_type", title="Salary by Job Type")
    
    return json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

############## Summary statistics related to jobtypes, not used by views.py ##################
def word_cloud(): 

    # Connect to database
    conn = psycopg2.connect(dbname='dataworks')
    cur = conn.cursor()

    # Query for data scientist jobs
    cur.execute('''select description from jobs2 where job_type = 'Data Scientist';''')
    rows = cur.fetchall()

    descriptions_ds = str(rows)

    # Query for Data Analyst jobs
    cur.execute('''select description from jobs2 where job_type = 'Data Analyst';''')
    rows = cur.fetchall()
    descriptions_da = str(rows)

    # Query for Data Engineer jobs
    cur.execute('''select description from jobs2 where job_type = 'Data Engineer';''')
    rows = cur.fetchall()
    descriptions_de = str(rows)

    # Query for Business Analyst jobs
    cur.execute('''select description from jobs2 where job_type = 'Business Analyst';''')
    rows = cur.fetchall()
    descriptions_ba = str(rows)

    stopwords = set(STOPWORDS)

    # Generate wordclouds for each of the 4 roles

    # Data science role
    print("enter wordcloud generation")
    wordcloud_ds = WordCloud(
                    background_color ='white',
                    stopwords = stopwords,
                    min_font_size = 10).generate(descriptions_ds)
    # matplotlib figure
    wordcloud_ds.to_file('/var/www/DataWorks/wc_ds.png')

    # data analyst role
    wordcloud_da = WordCloud(
                background_color ='white',
                stopwords = stopwords,
                min_font_size = 10).generate(descriptions_da)

    wordcloud_da.to_file('/var/www/DataWorks/wc_da.png')

    # Data engineer role
    wordcloud_de = WordCloud(
            background_color ='white',
            stopwords = stopwords,
            min_font_size = 10).generate(descriptions_de)

    wordcloud_de.to_file('/var/www/DataWorks/wc_de.png')

    # business analyst role
    wordcloud_ba = WordCloud(
            background_color ='white',
            stopwords = stopwords,
            min_font_size = 10).generate(descriptions_ba)

    wordcloud_ba.to_file('/var/www/DataWorks/wc_ba.png')
    
############## Summary statistics related to jobtypes, not used by views.py ##################

def salary_range(): 
    ''' Get the salary range for each job type. Returns a data frame of salary ranges for each job type'''

    # Database connection
    conn = psycopg2.connect(dbname='dataworks')
    cur = conn.cursor()

    # Query
    cur.execute('''select job_type, round(avg(salary_floor),2) floor, round(avg(salary_ceil),2) ceil from jobs2 group by job_type;''')
    rows = cur.fetchall()

    # Dataframe
    salary_ranges = pd.DataFrame(rows, columns = ['job_type', 'floor', 'ceil'])

    return salary_ranges

def top_companies(): 
    ''' Get the top 10 companies for each job type. Results of the form
     job_type         |             company              | rating | count 
    ------------------+----------------------------------+--------+-------
    Business Analyst  | Staffigo Technical Services, LLC |    5.0 |   178
    '''

    # Database connection
    conn = psycopg2.connect(dbname='dataworks')
    cur = conn.cursor()

    # Query
    cur.execute('''select job_type, company, rating, count(*) 
                from jobs2 
                group by (job_type, company, rating) 
                order by count desc;''')

    rows = cur.fetchall()

    # return statement

############## Functions for testing plotting and searching functionality ##################

def plotlyGOTest(): 
    ''' Sample test for plotly.graph_objects plots'''
    np.random.seed(1)

    y0 = np.random.randn(50) - 1
    y1 = np.random.randn(50) + 1

    fig = go.Figure()
    fig.add_trace(go.Box(y=y0))
    fig.add_trace(go.Box(y=y1))

    return json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

def plotlyPXTest(): 
    ''' Sample test for plotly.express plots'''

    df = px.data.tips()
    print(df.head)

    fig = px.box(df, x="day", y="total_bill", color="day")
    return json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)

def search(): 
    ''' Search for jobs given values from a form '''
   
    values = {'jobtype': 'Data Analyst'}

    conn = psycopg2.connect(dbname='dataworks')
    dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    dict_cur.execute('''select * from jobs2 where job_type =(%s) limit 10;''',[values['jobtype']])
    results = dict_cur.fetchall()

    dict_cur.close()
    conn.close()

    return render_template('results.html', jobs = results, query = values)

if __name__ == '__main__':
    # word_cloud()
    salary_range()