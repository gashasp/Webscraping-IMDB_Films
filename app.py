from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

table = soup.find("div", attrs={"lister-list"})
div = table.find_all("div",attrs="lister-item-content")
temp = [] #initiating a tuple

for i in range(0, len(div)):

    row = table.find_all("div",attrs="lister-item-content")[i]
    
    #mengambil data judul
    Title = row.find("a").text
    Title = Title.strip()

    #mengambil data imdb rating
    Rating = row.find("strong").text
    Rating = Rating.strip()
    
    #mengambil data metascore
    try :
        Metascore = row.find('span',attrs='metascore favorable').text
        Metascore = Metascore.strip()
    except :
        Metascore = 0
        
    #mengambil data votes
    Votes = row.find('span',attrs={"name":'nv'}).text
    Votes = Votes.strip()
        
    temp.append((Title,Rating,Metascore,Votes))

###temp = temp[::-1]

#change into dataframe
df = pd.DataFrame(temp, columns=("Title","Rating","Metascore","Votes"))

#insert data wrangling here
df["Votes"] = df["Votes"].str.replace(",","")
df["Rating"] = df["Rating"].astype("float64")
df["Votes"] = df["Votes"].astype("int64")
df["Metascore"] = df["Metascore"].astype("int64")

#data1
data1 = df.groupby('Title').sum()[["Rating"]].sort_values(by="Rating",ascending=False)

#data2
data2 = df.groupby('Title').sum()[["Rating"]].sort_values(by="Rating",ascending=True)

#data3
data3 = df.groupby('Title').sum()[["Metascore"]].sort_values(by="Metascore",ascending=False)

@app.route("/")
def index(): 
	
	card_data = df["Rating"].mean().round(2)

	# generate plot DATA1
	ax = data1.head(8).sort_values(by="Rating",ascending=True).plot(kind="barh",xlabel="Film",ylabel="Value",figsize = (22,10))
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	#DATA2
	ax = data2.head(8).sort_values(by="Rating",ascending=False).plot(kind="barh",xlabel="Film",ylabel="Value",figsize = (22,10))
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result2 = str(figdata_png)[2:-1]

	#DATA3
	ax = data3.head().sort_values(by="Metascore",ascending=True).plot(kind="barh",xlabel="Film",ylabel="Value",figsize = (20,9))
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result3 = str(figdata_png)[2:-1]


	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result,
		plot_result2=plot_result2,
		)


if __name__ == "__main__": 
    app.run(debug=True)
