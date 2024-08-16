# bgg-analysis
 Analysis of the Board Game Geek

# Game Group Analysis
Link to review - https://joey-kilgore.github.io/bgg-analysis/

The analysis is done in the `gameGroupAnalysis.ipynb`

To build docs (linux):  
```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
cd docs
make html
```


# initial setup
To start collecting BGG data, we will grab random threads to easily get a random collection of usernames. We will then grab the ratings and games that each of those users has, and from there the data is aggregated into three pickled objects.

You are welcome to run spider yourself to get your own random data, but a sample dataset of my own collecting is available on google drive at the following link:

https://drive.google.com/drive/folders/1a4hezOIohPHHbpyJ8lmThzMPAvsUX5Fo?usp=drive_link

# Analysis
Checkout `overallAnalysis.ipynb` for a sample script that looks through how to analyze this data by looking at overall ratings, and trying to find ways to link similar gamers together. 
