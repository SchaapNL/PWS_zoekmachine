from flask import Flask, render_template, request, redirect, url_for
import Search

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        return redirect('search/' + request.form['query'])
        # return request.form['query']
    return redirect(url_for('index'))


@app.route('/search/<query>')
def search_for(query):
    # return render_template("search.html", query=query)

    links = Search.search_query(query)


    return render_template("search.html", query = query, links = links)

if __name__ == '__main__':
    app.run()