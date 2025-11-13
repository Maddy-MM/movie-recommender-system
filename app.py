import streamlit as st
import pickle
import requests
import os
import gdown

movies = pickle.load(open('movies.pkl','rb'))
titles = movies['title'].values

# similarity = pickle.load(open('similarity.pkl','rb')) -> Can't be uploaded to GitHub due to size more than 100MB

# Google Drive file ID (from the share link)
file_id = "17ey95GCmLtm3cvcRATnSOaHUUb801kES"  
url = f"https://drive.google.com/uc?id={file_id}"

# File name to save locally
file_path = "similarity.pkl"

# Download only if it doesn't already exist
if not os.path.exists(file_path):
    print("Downloading similarity.pkl from Google Drive...")
    gdown.download(url, file_path, quiet=False)

# Load it
with open(file_path, "rb") as f:
    similarity = pickle.load(f)


my_api_key = os.getenv("TMDB_API_KEY")

def fetch_poster(movie_id):
  # Fetching movie details for the given movie_id
  response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={my_api_key}&language=en-US')
  
  # Converting details to JSON format
  data = response.json()

  # Returning the complete poster path
  return "https://image.tmdb.org/t/p/w500" + data['poster_path']

def recommend(movie):
  movie_index = movies[movies['title']==movie].index[0]
  distances = similarity[movie_index]

  movie_list = sorted(list(enumerate(distances)),reverse=True,key=lambda x:x[1])[1:6]
  
  recommended_movies = []
  recommended_movies_posters = []

  for i in movie_list:
    movie_id = movies.iloc[i[0]].movie_id

    # making recommendation list
    recommended_movies.append(movies.iloc[i[0]].title)

    # fetch poster from API 
    # URL = https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US
    # api_key = 6029d769d90a4d69c3719877a6a81d0c
    
    recommended_movies_posters.append(fetch_poster(movie_id))

  return recommended_movies,recommended_movies_posters



st.title('Movie Recommender System')

selected_movie_name = st.selectbox('Please enter the movie name:',titles)

if st.button('Recommend'):
  titles,posters = recommend(selected_movie_name)

  col1, col2, col3, col4, col5 = st.columns(5)

  with col1:
    st.text(titles[0])
    st.image(posters[0])

  with col2:
    st.text(titles[1])
    st.image(posters[1])

  with col3:
    st.text(titles[2])
    st.image(posters[2])

  with col4:
    st.text(titles[3])
    st.image(posters[3])

  with col5:
    st.text(titles[4])
    st.image(posters[4])