# Movie Recommender System

This project builds a **content-based Movie Recommendation System** that suggests similar movies based on a film’s metadata such as **genres, cast, crew, keywords, and overview**.
Model development is performed in **Google Colab**, and the final system is deployed through a **Streamlit web application** that provides dynamic recommendations with real-time movie posters fetched from the **TMDB API**.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Project Workflow](#project-workflow)
4. [Data Preprocessing](#1-data-preprocessing)
5. [Feature Engineering](#2-feature-engineering)
6. [Vectorization](#3-vectorization)
7. [Similarity Computation](#4-similarity-computation)
8. [Model Export](#5-model-export)
9. [Streamlit Web App](#streamlit-web-app)
10. [Installation & Setup](#installation--setup)
11. [How to Run](#how-to-run)
12. [Results](#results)
13. [Future Improvements](#future-improvements)
14. [Tech Stack](#tech-stack)

---

## Overview

The main objective of this project is to recommend movies that are **most similar** to a user-selected movie.
Instead of using user ratings or collaborative filtering, this system is purely **content-based**, focusing on movie descriptions such as:

* Movie overview
* Genres
* Keywords
* Top 3 cast members
* Director

This information is combined into a single **text feature ("tags")**, vectorized using **TF-IDF**, and compared using **Cosine Similarity**.

The system includes:

* **A Google Colab Notebook** for full data preprocessing and model creation
* **A Streamlit App** for interactive movie recommendations with poster display

---

## Features

* Cleans and preprocesses the TMDB 5000 dataset
* Extracts genres, keywords, top cast, and director using JSON parsing
* Applies stemming to reduce vocabulary size
* Converts text into numeric vectors using **TF-IDF**
* Computes similarity using **cosine similarity on 5000-dimensional vectors**
* Pickles the movies metadata and similarity matrix for fast loading
* Fetches movie posters in real-time using **TMDB API**
* Provides a simple and interactive **Streamlit interface**

---

## Project Workflow

1. Load TMDB datasets
2. Clean and filter needed columns
3. Extract structured info from JSON fields
4. Build combined text-based tags
5. Apply stemming
6. Vectorize text using TF-IDF
7. Compute cosine similarity
8. Save `.pkl` files
9. Integrate with Streamlit

---

## 1. Data Preprocessing

* Loaded:

  * **tmdb_5000_movies.csv**
  * **tmdb_5000_credits.csv**
* Merged both datasets using the `title` column
* Kept only the relevant columns:
  `movie_id, title, overview, genres, keywords, cast, crew`
* Removed:

  * Missing values
  * Duplicate entries
* Converted stringified JSON fields to Python lists using `ast.literal_eval`

---

## 2. Feature Engineering

Performed multiple transformations:

### Extracted structured data:

* **Genres** → list of genre names
* **Keywords** → list of keywords
* **Cast** → top 3 cast members
* **Crew** → extracted **Director**

### Text Processing:

* Converted overview paragraph to a list of words

* Removed spaces inside multi-word names (e.g., “Science Fiction” → “ScienceFiction”)

* Constructed a unified **tags** column:

  ```
  tags = overview + genres + keywords + cast + crew
  ```

* Converted tags to lowercase

---

## 3. Vectorization

### Stemming

* Used **PorterStemmer** to normalize similar words:

  ```
  loved → love, movies → movi
  ```

### TF-IDF Vectorizer

Used:

```python
TfidfVectorizer(max_features=5000, stop_words='english')
```

* Converted all movie tags into a 5000-dimensional sparse matrix

---

## 4. Similarity Computation

Computed pairwise similarity using:

```python
from sklearn.metrics.pairwise import cosine_similarity
similarity = cosine_similarity(vectors)
```

* Each movie now has similarity scores with all others
* For a selected movie, the top 5 similar movies are extracted

---

## 5. Model Export

Two files are saved for the Streamlit app:

* **movies.pkl** → Contains movie_id, title, and processed tags
* **similarity.pkl** → Contains the full cosine similarity matrix

Because `similarity.pkl` is usually **>100MB**, it cannot be pushed to GitHub.
Instead, it should be stored in **Google Drive** and downloaded automatically in Streamlit during runtime.

---

## Streamlit Web App

The Streamlit application provides an elegant UI to interact with the recommendation engine.

### Key Functionalities

* Select a movie through a dropdown box
* See 5 recommended movies instantly
* Movie posters fetched via **TMDB API** using a personal API key
* Columns used to display movie titles + posters

### Poster Fetching Logic

```python
https://api.themoviedb.org/3/movie/{movie_id}?api_key=YOUR_KEY&language=en-US
```

---

## Installation & Setup

1. **Clone the repository**

   ```bash
   git clone https://github.com/<your-username>/movie-recommender-system.git
   cd movie-recommender-system
   ```

2. **Create virtual environment**

   ```bash
   python -m venv myenv
   myenv\Scripts\activate   # Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set your TMDB API Key**

   ```bash
   setx TMDB_API_KEY "your_api_key_here"
   ```

5. **Download large files (from Google Drive) inside the app**
   The Streamlit app auto-downloads `similarity.pkl` using `gdown`.

---

## How to Run

**Option 1 — Run in Google Colab Notebook**

Open:

```
movie-recommender-system.ipynb
```

Run all cells.

**Option 2 — Launch Streamlit App**

```bash
streamlit run app.py
```

Choose a movie → click **Recommend** → view similar recommendations + posters.

---

## Results

* **Content-Based Filtering** using movie metadata
* **TF-IDF + Cosine Similarity** for vector distance
* **Top 5 recommendations** displayed with real posters
* Handles 5000+ movies with efficiently cached similarity lookups

---

## Future Improvements

* Switch to **Word2Vec embeddings** or **Universal Sentence Encoder**
* Add **ratings**, **runtime**, **popularity**, and hybrid filtering
* Use **FAISS** for large-scale similarity search
* Add year/genre filters in the UI

---

## Tech Stack

**Python Libraries:**

* Pandas, NumPy
* NLTK (Porter Stemmer)
* scikit-learn (TF-IDF, cosine similarity)
* Streamlit
* Requests
* Pickle
* gdown

**Tools:**

* Google Colab
* TMDB API
* Streamlit Cloud

