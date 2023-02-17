import streamlit as st
import pandas as pd
import numpy as np
chefmozaccepts=pd.read_csv('chefmozaccepts.csv')
chefmozcuisine=pd.read_csv('chefmozcuisine.csv')
chefmozhours4=pd.read_csv('chefmozhours4.csv')
chefmozparking=pd.read_csv('chefmozparking.csv')
geoplaces2=pd.read_csv('geoplaces2.csv')
rating_final=pd.read_csv('rating_final.csv')
usercuisine=pd.read_csv('usercuisine.csv')
userpayment=pd.read_csv('userpayment.csv')
userprofile=pd.read_csv('userprofile.csv')
user_f = pd.read_csv('user_f.csv')

from functools import reduce

#define list of DataFrames
dfs = [chefmozaccepts, chefmozcuisine, chefmozhours4, chefmozparking,geoplaces2,rating_final]

#merge all DataFrames into one
final_df = reduce(lambda  left,right: pd.merge(left,right,on=['placeID'],
                                            how='inner'), dfs)


import base64

@st.cache(allow_output_mutation=True)
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_png_as_page_bg(png_file):
    bin_str = get_base64_of_bin_file(png_file)
    page_bg_img = '''
    <style>
    body {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    
    st.markdown(page_bg_img, unsafe_allow_html=True)
    return



st.set_page_config(page_title=None, page_icon='set_png_as_page_bg("img/PHOTO-Jess.png")', layout="wide", initial_sidebar_state="auto", menu_items=None)
st.title("Restaurants Recommender")
from PIL import Image
image = Image.open('image_restaurant.jpg')

st.image(image)
geoplaces2["city"] = geoplaces2["city"].map(lambda x: x.lower())
geoplaces2["city"].replace({"s.l.p": "san luis potosi", "s.l.p.": "san luis potosi","san luis potos": "san luis potosi","san luis potosi ": "san luis potosi"}, inplace=True)
geoplaces2["city"].replace({"victoria": "victoria", "cd victoria ": "victoria","ciudad victoria": "victoria","cd. victoria ": "victoria","cd victoria": "victoria","cuidad victoria": "victoria","cd. victoria": "victoria"}, inplace=True)


geo_data = geoplaces2.filter(['latitude','longitude'])
st.map(data=geo_data, zoom=5, use_container_width=True)
    
st.write("""
### Best restaurants 
 
""")
final_df["city"] = final_df["city"].map(lambda x: x.lower())
final_df['city'].replace(['?'],final_df['city'].mode(), inplace=True)
final_df['url'].replace(['?'],'No Details', inplace=True)
final_df['address'].replace(['?'],'No Details', inplace=True)
final_df['days'].replace(['?'],'No Details', inplace=True)
final_df['hours'].replace(['?'],'No Details', inplace=True)
final_df['Rcuisine'].replace(['?'],final_df['Rcuisine'].mode(), inplace=True)
final_df['price'].replace(['?'],final_df['price'].mode(), inplace=True)
final_df['Rpayment'].replace(['?'],final_df['Rpayment'].mode(), inplace=True)
final_df['parking_lot'].replace(['?'],final_df['parking_lot'].mode(), inplace=True)
final_df["city"].replace({"s.l.p": "san luis potosi", "s.l.p.": "san luis potosi","san luis potos": "san luis potosi","san luis potosi ": "san luis potosi"}, inplace=True)
final_df["city"].replace({"victoria": "victoria", "cd victoria ": "victoria","ciudad victoria": "victoria","cd. victoria ": "victoria","cd victoria": "victoria","cuidad victoria": "victoria","cd. victoria": "victoria"}, inplace=True)
final_df['Restaurant_information'] ='Address: ' +final_df['address']+ ', City: ' + final_df['city']+', Cuisine: ' +final_df['Rcuisine']
final_df['Additional_information'] =' Price: ' + final_df['price']+ ', Payment Method: ' + final_df['Rpayment']+', Parking_lot :'+final_df['parking_lot']+', days_open : '+final_df['days']+' , Hours : '+final_df['hours']
new_final_df= final_df.drop_duplicates()
new_final_df1= new_final_df.drop_duplicates(subset=['Restaurant_information'])
user_final =pd.merge(user_f,new_final_df1,how = 'inner',on=["placeID"] )

matrix = pd.merge(rating_final,geoplaces2, how ="inner", on = ["placeID"])
matrix1 = pd.merge(matrix,chefmozcuisine, how ="inner", on = ["placeID"])
# modify values : Make the data in all cities to lowecase
matrix1["city"] = matrix1["city"].map(lambda x: x.lower())

def popularity_based_recommender(new_final_df1: pd.DataFrame, min_n_ratings: float):
    
    return (
        new_final_df1
        .groupby(['Additional_information', 'name',  'Restaurant_information'])
        .agg(
           
            rating_mean = ('rating', 'mean'),
            rating_count = ('rating', 'count')
        )
        .reset_index()
        .sort_values(['rating_count'], ascending=False)
        .query('rating_mean >= @min_n_ratings')
        .head(5)
        )
hide_table_row_index = """
       <style>
       tbody th {display:none}
       .blank {display:none}
       </style>
       """
# Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)
most_popular = popularity_based_recommender(new_final_df1.copy(),1.7)
mostPopular = most_popular.filter(['name','Restaurant_information','Additional_information'])
st.table(mostPopular)


st.write("""
    ### Select City of Choice : 

    """)
    #City based Recommendation
city = st.selectbox(
        ' ',
         (new_final_df1['city'].unique()))
col4, col5 = st.columns(2)
def _max_width_(prcnt_width:int = 75):
    max_width_str = f"max-width: {prcnt_width}%;"
    

with col4:
    def city_based_recommender(new_final_df1: pd.DataFrame, city: str):
        return (
            new_final_df1
            .groupby(['city', 'name','Additional_information'])
            .agg(
            rating_mean = ('rating', 'mean'),
            rating_count = ('rating', 'count')
        )
        .reset_index()
        .sort_values(['rating_count'], ascending=False)
        .query('city == @city & rating_mean >= 0')
        .head(5)
         )
    hide_table_row_index = """
        <style>
         tbody th {display:none}
        .blank {display:none}
        </style>
        """
   # Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    most_popular1 = city_based_recommender(new_final_df1.copy(),city)
    mostPopular1 = most_popular1.filter(['name','city','Additional_information'])
    st.table(mostPopular1)
with col5:
    def city_map(geoplaces2: pd.DataFrame, city: str):
        st.write(city)
        return(
            geoplaces2
               .query('city == @city')
               .filter(['latitude','longitude'])
            )
    city_map1=city_map(geoplaces2.copy(),city)
    st.map(data=city_map1, zoom=11, use_container_width=True)
    
    
col1, col2, col3 = st.columns(3)
def _max_width_(prcnt_width:int = 75):
    max_width_str = f"max-width: {prcnt_width}%;"     
        
with col1:
    st.subheader("Rating Based : ")
    #select Rating for city
    rating = st.selectbox(
        ' ',
         (new_final_df1['rating'].unique()))
    def cityRating_based_recommender(new_final_df1: pd.DataFrame, city: str, rating: int):
    
        return (
            new_final_df1
        
            .query('city == @city')
            .query('rating == @rating')
            .groupby(['city', 'name','rating','Restaurant_information'])
            .agg(
           
                rating_mean = ('rating', 'mean'),
                rating_count = ('rating', 'count')
            )
            .sort_values(['rating_count'], ascending=False)
            .reset_index()
            .head(5)
            )
    hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            .reportview-container .main .block-container{{{_max_width_}}}
            </style>
            """
# Inject CSS with Markdown
    st.markdown( hide_table_row_index, unsafe_allow_html=True)
    most_popular1 = cityRating_based_recommender(new_final_df1.copy(),city,rating)
    mostPopular1 = most_popular1.filter(['name','Restaurant_information','rating'])
    st.table(mostPopular1)

with col2:
    st.subheader("Price Range Based :")
    #City and Price based recommendation
    price = st.selectbox(
        ' ',
         (new_final_df1['price'].unique()))
    def cityPrice_based_recommender(new_final_df1: pd.DataFrame, city: str, price: str):
    
        return (
            new_final_df1
            .query('city == @city')
            .query('price == @price')
            .groupby(['city', 'name','price','Restaurant_information'])
            .agg(
           
                rating = ('rating', 'count')
            )
            .sort_values(['rating'], ascending=False)
            .reset_index()
            .head(5)
            )
    hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """
# Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    most_popular1 = cityPrice_based_recommender(new_final_df1.copy(),city,price)
    mostPopular1 = most_popular1.filter(['name','Restaurant_information','price'])
    st.table(mostPopular1)

with col3:
    st.subheader("Cuisine based :")
#City and Cuisine based recommender
    Rcuisine = st.selectbox(
        ' ',
         (new_final_df1['Rcuisine'].unique()))

    def cityCuisine_based_recommender(new_final_df1: pd.DataFrame, city: str, Rcuisine: str):
    
        return (
            new_final_df1
            .query('city == @city')
            .query('Rcuisine == @Rcuisine')
            .groupby(['city', 'name','Rcuisine','Restaurant_information'])
            .agg(
           
                rating = ('rating', 'count')
            )
            .sort_values(['rating'], ascending=False)
            .reset_index()
            .head(5)
            )
    hide_table_row_index = """
            <style>
            tbody th {display:none}
            .blank {display:none}
            </style>
            """
# Inject CSS with Markdown
    st.markdown(hide_table_row_index, unsafe_allow_html=True)
    most_popular1 = cityCuisine_based_recommender(new_final_df1.copy(),city,Rcuisine)
    mostPopular1 = most_popular1.filter(['name','Restaurant_information','price'])
    st.table(mostPopular1)
    

newdf_m= (
    new_final_df1
    .filter(['userID', 'name', 'city','rating'])
    .groupby(['userID'])
    .head(5))
(newdf_m
    .groupby(['userID'])
    .agg(
        mean_rating = ('rating', 'mean'),
        count_rating = ('rating', 'count')
    )
    .reset_index()
    .sort_values('mean_rating', ascending=False))
newdf1 = newdf_m.drop_duplicates()
newdf1.pivot(index='userID', columns='name', values='rating')

def get_sparse_matrix(newdf1: pd.DataFrame): 

    return(
    newdf1
        .pivot(index='userID', columns='name', values='rating')
    )

  
newdataf= (
    matrix1
    .filter(['userID', 'name', 'city','rating','Rcuisine'])
    .groupby(['userID'])
    .head(5))
(newdataf
    .groupby(['userID'])
    .agg(
        mean_rating = ('rating', 'mean'),
        count_rating = ('rating', 'count')
    )
    .reset_index()
    .sort_values('mean_rating', ascending=False))
newdataf1 = newdataf.drop_duplicates()
newdataf1.pivot(index='userID', columns=('name','Rcuisine'), values='rating')
def get_sparse_matrix(newdataf1: pd.DataFrame): 

    return(
    newdataf1
        .pivot(index='userID', columns=('name','Rcuisine'), values='rating')
    )
  
# py function item based recommender
st.write("""
### Select Restaurant of Choice : 
 
""")
name = st.selectbox(
    ' ',
     (new_final_df1['name'].unique()))

def item_based_recommender(dense_matrix: pd.DataFrame, name: str, n: int=5): # n=6, minimum number of ratings
    sparse_matrix = get_sparse_matrix(newdataf1)
    return(
    sparse_matrix
        .corrwith(sparse_matrix[name])
        .sort_values(ascending=False)
        .index
        .to_list()[1:n+1]
    )

hide_table_row_index = """
        <style>
        tbody th {display:none}
        .blank {display:none}
        </style>
        """
    # Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)
st.write("Beacuse you liked "+ name +" you may also like :")
most_popular_item = item_based_recommender(newdataf1,name)
st.table(most_popular_item)


st.write("""
### Select UserID : 
 
""")
#User based Recommendation
userID = st.selectbox(
    ' ',
     (new_final_df1['userID'].unique()))

def get_user_prefered_item(new_final_df1: pd.DataFrame, userID: str):
    data=new_final_df1.copy()
    return(data
    .query('userID == @userID') 
    .sort_values('rating', ascending=False)
    ['name'].to_list()[:3]
    )
hide_table_row_index = """
        <style>
        tbody th {display:none}
        .blank {display:none}
        </style>
        """
    # Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)
most_popular = get_user_prefered_item(new_final_df1,userID)
st.write("Restaurants you like : ")
st.table(most_popular)

def get_user_recommendation(user_final: pd.DataFrame, userID_x: str):
    data=user_final.copy()
    return(data
    .query('userID_x == @userID_x') 
    .sort_values('rating', ascending=False)
    ['name'].to_list()[:5]
    )
hide_table_row_index = """
        <style>
        tbody th {display:none}
        .blank {display:none}
        </style>
        """
    # Inject CSS with Markdown
st.markdown(hide_table_row_index, unsafe_allow_html=True)
recommened_user = get_user_recommendation(user_final,userID)
st.write("Recommended Restaurants  : ")
st.table(recommened_user)
