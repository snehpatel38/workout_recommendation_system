from flask import Flask, render_template, request
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import random
import os

app = Flask(__name__)

file_path = os.getenv("DATA_FILE", "gym_recommendation.xlsx")

if not os.path.exists(file_path):
    raise FileNotFoundError(f"The file {file_path} does not exist. Please place it in the correct directory.")

data = pd.read_excel(file_path)

data.drop(columns=['ID'], inplace=True)

# Initialize encoders and scalers
label_enc = LabelEncoder()
scaler = StandardScaler()

# Fit encoders and scalers
for col in ['Sex', 'Hypertension', 'Diabetes', 'Level', 'Fitness Goal', 'Fitness Type']:
    data[col] = label_enc.fit_transform(data[col])

data[['Age', 'Height', 'Weight', 'BMI']] = scaler.fit_transform(data[['Age', 'Height', 'Weight', 'BMI']])

def get_recommendations(user_input):
    # Normalize numerical features
    num_features = ['Age', 'Height', 'Weight', 'BMI']
    user_df = pd.DataFrame([user_input], columns=num_features)
    user_df[num_features] = scaler.transform(user_df[num_features])
    user_input.update(user_df.iloc[0].to_dict())
    user_df = pd.DataFrame([user_input])

    # Calculate similarity scores
    user_features = data[['Sex', 'Age', 'Height', 'Weight', 'Hypertension', 
                         'Diabetes', 'BMI', 'Level', 'Fitness Goal', 'Fitness Type']]
    similarity_scores = cosine_similarity(user_features, user_df).flatten()

    # Get primary recommendation
    similar_user_indices = similarity_scores.argsort()[-5:][::-1]
    similar_users = data.iloc[similar_user_indices]
    recommendation_1 = similar_users[['Exercises', 'Diet', 'Equipment']].mode().iloc[0]

    # Get alternative recommendations
    recommendations = [recommendation_1]
    
    for _ in range(2):
        modified_input = user_input.copy()
        modified_input['Age'] += random.randint(-5, 5)
        modified_input['Weight'] += random.uniform(-5, 5)
        modified_input['BMI'] += random.uniform(-1, 1)

        modified_user_df = pd.DataFrame([modified_input], columns=num_features)
        modified_user_df[num_features] = scaler.transform(modified_user_df[num_features])
        modified_input.update(modified_user_df.iloc[0].to_dict())

        modified_similarity_scores = cosine_similarity(user_features, pd.DataFrame([modified_input])).flatten()
        modified_similar_user_indices = modified_similarity_scores.argsort()[-5:][::-1]
        modified_similar_users = data.iloc[modified_similar_user_indices]
        recommendation = modified_similar_users[['Exercises', 'Diet', 'Equipment']].mode().iloc[0]

        if not any(rec['Exercises'] == recommendation['Exercises'] and 
                  rec['Diet'] == recommendation['Diet'] and 
                  rec['Equipment'] == recommendation['Equipment'] 
                  for rec in recommendations):
            recommendations.append(recommendation)

    return recommendations

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    user_input = {
        'Sex': int(request.form['sex']),
        'Age': float(request.form['age']),
        'Height': float(request.form['height']),
        'Weight': float(request.form['weight']),
        'Hypertension': int(request.form['hypertension']),
        'Diabetes': int(request.form['diabetes']),
        'BMI': float(request.form['bmi']),
        'Level': int(request.form['level']),
        'Fitness Goal': int(request.form['fitness_goal']),
        'Fitness Type': int(request.form['fitness_type'])
    }
    
    recommendations = get_recommendations(user_input)
    return render_template('recommendations.html', recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)