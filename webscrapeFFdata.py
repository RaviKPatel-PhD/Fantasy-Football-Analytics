import pandas as pd
from bs4 import BeautifulSoup
import urllib.request, urllib.parse, urllib.error
import re
import csv
import ssl
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

# Ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = input('Enter URL- ')
if len(url) < 1:
    url = "https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php"
html = urllib.request.urlopen(url, context = ctx).read()
soup = BeautifulSoup(html, "html.parser")

#get column titles
columnheads = [th.getText() for th in
    soup.findAll('tr', limit=1)[0].findAll('th')][0:9]
    #I had to subet 0:9 here because the last column 'notes' didn't actually contain any data
#print(columnheads)

#Scrape the data for each player
data_rows = soup.findAll('tr', {"data-id" : re.compile(r".*")})
#I was going to skip the first header row, but since I told it to only pull out "data-id" I didn't have too
#I also skipped tier rows here wth "data-id"
#print(str(data_rows))

#collect the player data from the list of HTML that is data_rows
#This will make a list of lists
player_data = []  # create an empty list to hold all the data
for i in range(len(data_rows)):  # for each table row
    player_row = []  # create an empty list for each pick/player
    # for each table data element from each table row
    for td in data_rows[i].findAll('td'): #just a note, this tag will change based on which profootballers sheet I am scraping
        # get the text content and append to the player_row
        player_row.append(td.getText())
    # then append each pick/player to the player_data matrix
    player_data.append(player_row)
#print(player_data[0:4])

#Next we can construct a dataframe using pandas
df = pd.DataFrame(player_data, columns=columnheads)
#print(df.head())  # head() lets us see the 1st 5 rows of our DataFrame by default
df.rename(columns={'Overall (Team)':'Name'}, inplace=True)
#Here I am renaming a column that has a confusing title
df = df[df.Rank.notnull()] #removes all rows that contain missing values
df.drop('WSID', 1, inplace=True) #this will delete the WSID column, which contains no data
#print(df.head())

#next change the data to the proper type if necessary
df = df.convert_objects(convert_numeric=True)
#print(df.dtypes)  # Take a look at data typse in each column

#Save the file as a .csv so we can manipulate it an another program if we like
#df.to_csv("FFranking.csv")

#Now I will write a for loop to go through each row and count the number of
#draftable players at each position
RB = 0.0 #Name each vairable that I will count
WR = 0.0
TE = 0.0
QB = 0.0
K = 0.0
for p in df.Pos :
    if re.match(r'^(RB)', p) : RB = RB + 1  #count which player of each position
    if re.match(r'^(WR)', p) : WR = WR + 1
    if re.match(r'^(TE)', p) : TE = TE + 1
    if re.match(r'^(QB)', p) : QB = QB + 1
    if re.match(r'^(K)', p) : K = K + 1
print('There are', int(RB), 'draftable RBs \n'
    'There are', int(WR), 'draftable WRs \n'
    'There are', int(TE), 'draftable TEs \n'
    'There are', int(QB), 'draftable QBs \n'
    'There are', int(K), 'draftable Kickers')

#Next plot the number of draftable players at each position
positions = ('Running\nBacks', 'Wide\nRecievers', 'Tight Ends', 'Quarterbacks', 'Kickers')
y_pos = np.arange(len(positions))
number = [int(RB), int(WR), int(TE), int(QB), int(K)]

plt.bar(y_pos, number, align='center', alpha=0.5)
plt.xticks(y_pos, positions)
plt.ylabel('Draftable Players')
plt.title('Position')

#plt.show()
plt.savefig('FFdraftablePos.png', bbox_inches='tight') #Save as a png







#Major props to Sarvass Tjortjoglou, I used a lot of his code analyzing NBA draft
#to go thorugh this analysis
#His website: http://savvastjortjoglou.com/nba-draft-part01-scraping.html
