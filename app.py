import streamlit as st
import pickle
import requests
import os
import gdown

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# --- SIDEBAR DOCUMENTATION & ABOUT ---
with st.sidebar:
    st.title("Project Reference")
    st.caption("Movie Recommender System — Documentation")

    # --- NEW 'ABOUT' SECTION ---
    # This adds professional links to your profile and code
    st.divider()
    st.header("About This Project")
    st.info(
        """
        This app is a portfolio project demonstrating content-based filtering.
        All code and data are available on GitHub.
        """
    )
    
    # Update these links to your own!
    st.page_link(
        "https://github.com/Maddy-MM/movie-recommender-system", 
        label="View Source Code on GitHub", 
        icon="🔗"
    )
    st.page_link(
        "https://www.linkedin.com/feed/", 
        label="Author's LinkedIn Profile", 
        icon="🧑‍💼"
    )
    st.divider()
    # --- END NEW SECTION ---

    # We keep the documentation, but make it collapsed by default
    st.header("Project Documentation")
    with st.expander("Overview", expanded=False): # <-- Set to False
        st.write(
            """
            This app recommends movies based on **content-based filtering**. 
            Users select a movie, and the app finds 5 other movies that are
            most similar in content.
            """
        )

    with st.expander("How it Works", expanded=False): # <-- Set to False
        st.markdown(
            """
            - **Data:** Movie data (titles, genres, keywords, cast, crew) is processed and vectorized.
            - **Similarity:** A cosine similarity matrix is pre-computed from this data and saved as `similarity.pkl`.
            - **Recommendation:**
                1. The app finds the selected movie in the matrix.
                2. It retrieves the list of similarity scores for that movie.
                3. It sorts these scores and selects the top 5 most similar movies.
            - **Display:** The TMDB API is used to fetch movie posters for a clean visual display.
            """
        )

    with st.expander("Model & Data Files", expanded=False): # <-- Set to False
        st.markdown(
            """
            - **`movies.pkl`**: A `pandas.DataFrame` containing the `movie_id` and `title` for the dropdown.
            - **`similarity.pkl`**: A `numpy.ndarray` (or sparse matrix) containing the pre-computed cosine similarity scores between all movies.
            - **TMDB API**: A third-party API used *only* to fetch posters. The recommendation logic is 100% self-contained in `similarity.pkl`.
            """
        )
    
    with st.expander("Interpreting Results", expanded=False): # <-- Set to False
        st.markdown(
            """
            The recommendations are based on **content similarity**. This means movies are suggested if they share:
            - Similar keywords, plot summaries, or taglines
            - The same genres
            - The same director or main actors
            
            The model does **not** use user ratings (collaborative filtering).
            """
        )

# --- DATA LOADING ---
@st.cache_data
def load_data():
    """Loads movies and downloads/loads similarity matrix."""
    movies = pickle.load(open('movies.pkl', 'rb'))
    titles = movies['title'].values
    
    file_id = "17ey95GCmLtm3cvcRATnSOaHUUb801kES"
    url = f"https.drive.google.com/uc?id={file_id}"
    file_path = "similarity.pkl"

    if not os.path.exists(file_path):
        with st.spinner("Downloading recommendation model (one-time)..."):
            gdown.download(url, file_path, quiet=False)
    
    with open(file_path, "rb") as f:
        similarity = pickle.load(f)
        
    return movies, titles, similarity

movies, titles, similarity = load_data()

# --- API & APP LOGIC ---
my_api_key = os.getenv("TMDB_API_KEY")
PLACEHOLDER = "https://via.placeholder.com/500x750?text=No+Poster"

@st.cache_data
def fetch_poster(movie_id):
    url = f"https.api.themoviedb.org/3/movie/{movie_id}"
    params = {"api_key": my_api_key, "language": "en-US"}
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        poster_path = data.get("poster_path")
        
        if not poster_path:
            return PLACEHOLDER
        return "https://image.tmdb.org/t/p/w500" + poster_path
    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
        return PLACEHOLDER

def recommend(movie):
    try:
        movie_index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return [], []

    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    
    recommended_movies = []
    recommended_movies_posters = []

    for i in movie_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters

# --- UI LAYOUT ---

# --- Centered Controls (Title, Select, Button) ---
_, mid_col, _ = st.columns([1, 2, 1])

with mid_col:
    st.markdown(
        "<h1 style='text-align: center;'>🎬 Movie Recommender System</h1>", 
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center;'>Find movies similar to your favorites.</p>", 
        unsafe_allow_html=True
    )
    
    # --- Use st.form for the inputs ---
    with st.form(key='recommender_form'):
        selected_movie_name = st.selectbox(
            'Select a movie you like:',
            titles,
            label_visibility="collapsed"
        )
        
        # --- Use st.form_submit_button ---
        submitted = st.form_submit_button(
            'Recommend', 
            type="primary", 
            use_container_width=True
        )

# --- Display Results (This section is OUTSIDE the 'with mid_col' block) ---
if submitted: # Check if the form was submitted
    with st.spinner('Finding recommendations...'):
        titles, posters = recommend(selected_movie_name)

        if titles:
            # Create centered columns for the posters
            _, col1, col2, col3, col4, col5, _ = st.columns(
                [0.5, 1, 1, 1, 1, 1, 0.5], 
                gap="medium"
            )
            with col1:
                st.image(posters[0], caption=titles[0])
            with col2:
                st.image(posters[1], caption=titles[1])
            with col3:
                st.image(posters[2], caption=titles[2])
            with col4:
                st.image(posters[3], caption=titles[3])
            with col5:
                st.image(posters[4], caption=titles[4])
        else:
            # Display error in the middle column for consistency
            with mid_col:
                st.error("Sorry, couldn't find recommendations for that movie.")