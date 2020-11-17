# SP Event Recommender

This project is based on the YouTube Video Recommender project designed and taught by Mário Filho on his Hotmart course (https://curso.mariofilho.com/).

I decided to do something similar, but trying to predict events that I would like to attend in São Paulo. For that, I collected information from events from two ticket-selling aggregator websites: Sympla and Eventbrite, manually labeled them and fit several models to evaluate which one had better performance. A quick overview is detailed below and there are also explanation notes in the notebook where the project is implemented (Event_Recommender_vgit.ipynb):

After collecting information, I decided to process each event column as follows:
- Name: make it lowercase, remove punctuation, accented chars and numbers
- Date: use day of week (DOW) as possible feature
- Location: make it lowercase, remove punctuation, accented chars and numbers
- Price: use mean or lowest price
- Info: make it lowercase, remove punctuation, accented chars and numbers
- Description: make it lowercase, remove punctuation, accented chars
- Organizer: make it lowercase, remove punctuation, accented chars

Since many of the features were textual, in order to prepare them for vectorization, I applied tokenization, stopword removal and duplicate word removal. Stemming was not applied as default, but is implemented and can be performed by setting a flag

For the other columns, I normalized prices by subtracting its mean and dividing by its standard deviation (StandardScaler object). And for the DOW feature, I imputed its mode for null values and transformed it to dummy variables with one-hot encoding (OneHotEncoder object).

Finally, I fit several models (with and without the non-textual features) and chose the one that I considered achieved the best performance: **optimized (for F1-Score) Random Forest without non-textual features**

*It didn't overfit the training data (had higher than 0 training misclassification error (ME)); and achieved highest accuracy (lowest ME), F1-score and second highest recall with validation data*

Since this is a personal project and an initial version, I run it locally using Flask. It returns me predictions for the current events on the first 2 search pages of both websites. Below is a screenshot of the final template with the event links and predictions:

![Final template](https://github.com/rafael-siqueira/event_rec/blob/master/Event_Recommender.png)

There are 4 implementation scripts: app.py, get_data.py, prediction.py, run_backend.py. They are commented with brief explanations of what each is doing.  

Having all scripts in the same folder, just run the following commands on the command line and access http://127.0.0.1:5000/ to obtain the predictions

`set FLASK_APP=app.py`  
`python -m flask run`
