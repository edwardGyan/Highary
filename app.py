from flask import Flask, render_template, redirect, url_for, request
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
import pandas as pd
 

app = Flask(__name__)
app.config['SECRET_KEY']='secret'
app.config['DEBUG'] = True
 

class ChoiceForm(FlaskForm):
    region = SelectField('Choose Region', choices=[('GREATER ACCRA', 'GREATER ACCRA'), ('EASTERN', 'EASTERN'), ('CENTRAL', 'CENTRAL'),
                                                   ('VOLTA', 'VOLTA'), ('WESTERN', 'WESTERN'), ('WESTERN NORTH', 'WESTERN NORTH'), 
                                                   ('ASHANTI', 'ASHANTI'), ('BRONG AHAFO', 'BRONG AHAFO'), ('BONO EAST', 'BONO EAST'), 
                                                   ('AHAFO', 'AHAFO'), ('OTI', 'OTI'), ('NORTHERN', 'NORTHERN'), ('SAVANNAH', 'SAVANNAH'),
                                                   ('UPPER WEST', 'UPPER WEST'), ('NORTH EAST', 'NORTH EAST'), ('UPPER EAST', 'UPPER EAST')])
    status = SelectField('Day or Boarding?', choices=[('Day', 'Day'), ('Day/Boarding', 'Day/Boarding')])
    gender = SelectField('Gender', choices=[('Boys', 'Boys'), ('Girls', 'Girls'), ('Mixed', 'Mixed')])
    submit = SubmitField('Get Recommendations')


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/selection', methods=['GET', 'POST'])   
def selection():
    form = ChoiceForm()
    if form.validate_on_submit():
        region = form.region.data
        status = form.status.data
        gender = form.gender.data
        return redirect(url_for('results', region=region, status=status, gender=gender))
    return render_template('selection.html', form = form)

@app.route('/results', methods=['GET','POST'])  
def results():
    region = request.args.get('region')
    status = request.args.get('status')
    gender = request.args.get('gender')

    recommendations = start_recs(region=region, status=status, gender=gender)
    print(recommendations)



    return render_template('results.html', region=region, status=status, gender=gender, recommendations=recommendations)
 

@app.route('/more', methods=['GET','POST'])  
def more():
    return render_template('more.html')


#recommendation function
def start_recs(region, gender, status):
# Load the dataset
    df = pd.read_csv('high_schools.csv')

    # Perform frequency encoding
    region_freq = df['REGION'].value_counts(normalize=True)
    location_freq = df['LOCATION'].value_counts(normalize=True)
    gender_freq = df['GENDER'].value_counts(normalize=True)
    status_freq = df['STATUS'].value_counts(normalize=True)
    df['region_encoded'] = df['REGION'].map(region_freq)
    df['location_encoded'] = df['LOCATION'].map(location_freq)
    df['gender_encoded'] = df['GENDER'].map(gender_freq)
    df['status_encoded'] = df['STATUS'].map(status_freq)

    # Define the user's preferences
    user_preferences = {
        'REGION': region,
        'GENDER': gender,
        'STATUS': status
        

    }

    # Filter schools based on user preferences
    filtered_schools = df.copy()
    # print(filtered_schools)
    for attribute, value in user_preferences.items():
        filtered_schools = filtered_schools[filtered_schools[attribute] == value]

    attributes = ['region_encoded', 'gender_encoded', 'status_encoded']
    filtered_attributes = filtered_schools[attributes]

    # Normalize numerical attributes
    normalized_attributes = (filtered_attributes - filtered_attributes.min()) / (filtered_attributes.max() - filtered_attributes.min())

    # Calculate cosine similarity
    similarity_matrix = normalized_attributes.dot(normalized_attributes.T)

    # Get top recommendations
    top_recommendations = similarity_matrix.mean(axis=1).nlargest(5)

    recommended_schools = df.loc[top_recommendations.index]
    filtered_recommendations = recommended_schools.drop(columns=['region_encoded', 'location_encoded', 'gender_encoded', 'status_encoded'])

    # convert to a list of dictionaries, easier for processing in html. 
    new_filtered_recommendations = filtered_recommendations.to_dict('records')
    
    return new_filtered_recommendations
    


if __name__ == '__main__':
    app.run()