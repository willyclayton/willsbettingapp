from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def predict_game_outcome(df):
    # Split the data into features (X) and target (y)
    X = df.drop('Outcome', axis=1)
    y = df['Outcome']
    
    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    
    # Train the classifier
    clf = DecisionTreeClassifier()
    clf.fit(X_train, y_train)
    
    # Make predictions on the testing data
    y_pred = clf.predict(X_test)
    
    # Calculate the accuracy of the predictions
    accuracy = accuracy_score(y_test, y_pred)
    
    return accuracy

df = pd.read_csv('dummyframe.csv')
