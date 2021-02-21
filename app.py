from flask import Flask,render_template,redirect,request
import pandas
from sklearn.model_selection import train_test_split
class popularity_recommender_py():
    def __init__(self):
        self.train_data = None
        self.user_id = None
        self.item_id = None
        self.popularity_recommendations = None

    def create(self, train_data, user_id, item_id):
        self.train_data = train_data
        self.user_id = user_id
        self.item_id = item_id
        train_data_grouped = train_data.groupby([self.item_id]).agg({self.user_id: 'count'}).reset_index()
        train_data_grouped.rename(columns = {'user_id': 'score'},inplace=True)
        train_data_sort = train_data_grouped.sort_values(['score', self.item_id], ascending = [0,1])
        train_data_sort['Rank'] = train_data_sort['score'].rank(ascending=0, method='first')
        self.popularity_recommendations = train_data_sort.head(10)


    def recommend(self, user_id):
        user_recommendations = self.popularity_recommendations
        user_recommendations['user_id'] = user_id
        cols = user_recommendations.columns.tolist()
        user_recommendations = user_recommendations[cols]
        return user_recommendations
song_df_1 = pandas.read_table('https://static.turi.com/datasets/millionsong/10000.txt')
song_df_1.columns = ['user_id', 'song_id', 'listen_count']
song_df_2 =  pandas.read_csv('https://static.turi.com/datasets/millionsong/song_data.csv')
song_df = pandas.merge(song_df_1, song_df_2.drop_duplicates(['song_id']), on="song_id",how='left')
song_df = song_df.head(10000)
song_df['song'] = song_df['title'].map(str) + " - " + song_df['artist_name']
song_grouped = song_df.groupby(['song']).agg({'listen_count': 'count'}).reset_index()
grouped_sum = song_grouped['listen_count'].sum()
song_grouped['percentage']  = song_grouped['listen_count'].div(grouped_sum)*100
song_grouped.sort_values(['listen_count', 'song'], ascending = [0,1])
train_data, test_data = train_test_split(song_df, test_size = 0.20, random_state=0)
pm= popularity_recommender_py()
pm.create(train_data, 'user_id', 'song')
app=Flask(__name__)
@app.route('/',methods=['GET','POST'])
def home():
    if request.method=='POST':
        user_id=request.form['n1']
        a=pm.recommend(user_id)
        a1=a.columns
        l=[]
        for i in a1:
            l.append(list(a[i]))
        return render_template('index.html',l=l,u=user_id)
    else:
        return render_template('index.html')
if __name__=='__main__':
    app.run(debug=True)
