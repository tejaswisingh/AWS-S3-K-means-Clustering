from flask import Flask,render_template,request
from flaskext.mysql import MySQL

import time

#easier to read csv file using pandas
import pandas as pd

#to make data to be in an acceptable format in the form of an array as python doesn't have an array
#import numpy as np
from numpy import vstack

#use Kmeans algorithm
from scipy.cluster.vq import kmeans,vq

#below 2 lines is to make the the graph
import pygal
from pygal.style import DefaultStyle, DarkGreenBlueStyle
custom_style = DarkGreenBlueStyle(colors=('#E853A0', '#E8537A', '#E95355', '#E87653', '#E89B53'))


mysql = MySQL()
app = Flask(__name__)

#mysql credentials
app.config['MYSQL_DATABASE_USER'] = 'USer_name'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Password'
app.config['MYSQL_DATABASE_DB'] = 'Database_name'
app.config['MYSQL_DATABASE_HOST'] = 'Datbase_host'
mysql.init_app(app)



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cluster')
def cluster():
    # values required
    start=time.time()
    col1 = request.args.get('col1')
    col2 = request.args.get('col2')
    n_clusters = int(request.args.get('cluster'))

    # reading data from Database
    conn = mysql.connect()
    print 'mysql connected'

    cursor = conn.cursor()
    print 'cursor creted'
    print 'querying'

    cursor.execute("select "+col1+", "+col2+" from mydb.new")
    print 'fetching data'
    result = cursor.fetchall()


    # forming sets ---- x[1,2,3...] and y[6,7,8....] to data[[1,6],[2,7],[3,8]]
    data = []
    for each in result:
        inner_list = []
        inner_list.append(float(each[0]))
        inner_list.append(float(each[1]))
        data.append(inner_list)

    print data


    data = vstack(data)

    # creating centroids from data given
    centroids, distortion = kmeans(data, n_clusters)
    ##centroids -> centre point of clusters
    print centroids


    #calculating number of points in each cluster
    list = ''
    total_count = 0
    cluster_names = []
    for i in range(n_clusters):

        name = "Cluster " + str(i + 1)
        cluster_names.append(name)

        # count points in each cluster based on data and idx labels
        points = data[idx == i, 0]
        count = 0
        for point in points:
            count += 1

        list += "Total cluster points in {0} is : {1}\n".format(name, count)
        total_count += count

    print list
    print total_count

    print "Centroids :"
    print centroids

    # making centroid poins as actual set of points like [1,2]
    centroid_points = []
    for row in centroids:
        cent = []
        cent.append(row[0])
        cent.append(row[1])
        centroid_points.append(cent)

    print centroid_points

    # creating scatter graph

    # creating an object of pygal graphs
    # xy is to show that it is a x-y coordinate graph
    # stroke-False, as we dont need line strokes
    scatter_chart = pygal.XY(stroke=False, style=DefaultStyle, dots_size=2, width=1280, height=720,
                             legend_at_bottom=False, title='K-Means Clustering')

    # adding points for each cluster to scatter plot
    for i in range(0, n_clusters):
        for j in range(0, 1):
            scatter_data = []
            for k in range(0, len(data[idx == i, j]) - 1):
                each_tuple = (data[idx == i, j][k], data[idx == i, j + 1][k])
                scatter_data.append(each_tuple)

            scatter_chart.add(cluster_names[i], scatter_data)

    # adding centroids to scatter plot
    scatter_data = []
    for i in range(len(centroids[:, 0])):
        each_tuple = (centroids[:, 0][i - 1], centroids[:, 1][i - 1])
        scatter_data.append(each_tuple)

    scatter_chart.add("Centroids", scatter_data)

    return scatter_chart.render_response()


if __name__ == '__main__':
	app.run(debug=True)
