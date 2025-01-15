from flask import Flask, render_template

app = Flask(__name__)

# Route for the Index Page
@app.route('/')
def index():
    return render_template('index.html')  # Your index page template

# Route for the Protect Page
@app.route('/protect')
def protect():
    return render_template('protect.html')  # Make sure to create 'protect.html'

# Route for the About Page
@app.route('/about')
def about():
    return render_template('about.html')  # Make sure to create 'about.html'

# Route for the Doctors Page
@app.route('/doctors')
def doctors():
    return render_template('doctors.html')  # Make sure to create 'doctors.html'

# Route for the News Page
@app.route('/news')
def news():
    return render_template('news.html')  # Make sure to create 'news.html'

if __name__ == '__main__':
    app.run(debug=True)
