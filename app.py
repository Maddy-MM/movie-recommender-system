import streamlit as st
import pickle
import requests
import os
import gdown

# --- PAGE CONFIG ---
st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# --- SIDEBAR (unchanged) ---
with st.sidebar:
    st.title("Project Reference")
    st.caption("Movie Recommender System — Documentation")
    st.divider()
    st.header("About This Project")
    st.info(
        """
        This app is a portfolio project demonstrating content-based filtering.
        All code and data are available on GitHub.
        """
    )
    st.page_link("https://github.com/Maddy-MM/movie-recommender-system", label="View Source Code on GitHub", icon="🔗")
    st.page_link("https://www.linkedin.com/feed/", label="Author's LinkedIn Profile", icon="🧑‍💼")
    st.divider()
    st.header("Project Documentation")
    with st.expander("Overview", expanded=False):
        st.write(
            """
            This app recommends movies based on **content-based filtering**. 
            Users select a movie, and the app finds 5 other movies that are
            most similar in content.
            """
        )
    with st.expander("How it Works", expanded=False):
        st.markdown(
            """
            - **Data:** Movie data (titles, genres, keywords, cast, crew) is processed and vectorized.
            - **Similarity:** A cosine similarity matrix is pre-computed and saved as `similarity.pkl`.
            - **Recommendation:** The app finds similar movies and uses the TMDB API to fetch posters.
            """
        )

# --- DATA LOADING ---
@st.cache_data
def load_data():
    """Loads movies and downloads/loads similarity matrix."""
    movies = pickle.load(open('movies.pkl', 'rb'))
    titles = movies['title'].values

    # Correct Drive URL (was missing https://)
    file_id = "17ey95GCmLtm3cvcRATnSOaHUUb801kES"
    url = f"https://drive.google.com/uc?id={file_id}"
    file_path = "similarity.pkl"

    if not os.path.exists(file_path):
        with st.spinner("Downloading recommendation model (one-time)..."):
            gdown.download(url, file_path, quiet=False)

    with open(file_path, "rb") as f:
        similarity = pickle.load(f)

    return movies, titles, similarity

movies, titles, similarity = load_data()

# --- API & APP LOGIC ---
# Prefer providing your API key in env or streamlit secrets. If not present, we'll show placeholders.
my_api_key = os.getenv("TMDB_API_KEY") or st.secrets.get("TMDB_API_KEY", None)
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"

@st.cache_data
def fetch_poster(movie_id):
    # Ensure movie_id is correct type/string
    if not my_api_key:
        return PLACEHOLDER

    url = f"https://api.themoviedb.org/3/movie/{movie_id}"  # fixed missing https://
    params = {"api_key": my_api_key, "language": "en-US"}

    try:
        response = requests.get(url, params=params, timeout=5)
        # helpful debug: uncomment if needed
        # st.write("TMDB status:", response.status_code)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        if not poster_path:
            return PLACEHOLDER
        return "https://image.tmdb.org/t/p/w500" + poster_path
    except requests.exceptions.RequestException:
        return PLACEHOLDER

def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return [], []

    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_titles = []
    recommended_posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_titles.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_titles, recommended_posters

# --- UI LAYOUT ---
_, mid_col, _ = st.columns([1, 2, 1])

with mid_col:
    st.markdown("<h1 style='text-align: center;'>🎬 Movie Recommender System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Find movies similar to your favorites.</p>", unsafe_allow_html=True)

    with st.form(key='recommender_form'):
        selected_movie_name = st.selectbox('Select a movie you like:', titles, label_visibility="collapsed")
        submitted = st.form_submit_button('Recommend', type="primary", use_container_width=True)

# --- Display Results ---
if submitted:
    with st.spinner('Finding recommendations...'):
        rec_titles, posters = recommend(selected_movie_name)

        if rec_titles:
            _, col1, col2, col3, col4, col5, _ = st.columns([0.5, 1, 1, 1, 1, 1, 0.5], gap="medium")
            with col1:
                st.image(posters[0], caption=rec_titles[0])
            with col2:
                st.image(posters[1], caption=rec_titles[1])
            with col3:
                st.image(posters[2], caption=rec_titles[2])
            with col4:
                st.image(posters[3], caption=rec_titles[3])
            with col5:
                st.image(posters[4], caption=rec_titles[4])
        else:
            with mid_col:
                st.error("Sorry, couldn't find recommendations for that movie.")
