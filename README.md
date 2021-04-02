Post-Dispatch app template
==========================

* [What is this?](#what-is-this)
* [Assumptions](#assumptions)
* [Set up OAuth](#set-up-oauth)
* [How to create an app](#how-to-create-an-app)
* [Editing contexts / templates](#editing-contexts--templates)
* [Things to remember](#things-to-remember)

What is this?
-------------

This is a St. Louis Post-Dispatch interactive project, built using our modified version of NPR's [app template](https://github.com/nprapps/app-template/).

Assumptions
-----------

To build an app using this app template, the following things must be true:

* You are running MacOS X.
* You are using Python 2.7.
* You have [virtualenv](https://pypi.python.org/pypi/virtualenv) and [virtualenvwrapper](https://pypi.python.org/pypi/virtualenvwrapper) installed and working.

If you need help to set up your Mac for coding/development, see NPR's [development environment blog post](http://blog.apps.npr.org/2013/06/06/how-to-setup-a-developers-environment.html).


Set up OAuth
------------

This is something you need to do one time only on your development Mac.

1. Contact Josh Renaud to get a set of three environment variables (`GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CONSUMER_SECRET`, `AUTHOMATIC_SALT`) that need to be added to `~/.bash_profile` on your Mac. These will ensure the app-template can communicate with the P-D interactive Google API account.

2. You will need authenticate with Google the very first time you try Fabric command #2 (below). See this [NPR blog post](http://blog.apps.npr.org/2015/03/02/app-template-oauth.html#authenticating) for details.

3. Once you do these steps, you'll never have to do them again for any other app-template project.


How to create an app
--------------------

1. Create a GitHub repo for your project. Note the name (e.g. `your-project-name`)

2. Clone the P-D app-template repo to your local drive as the basis for your new project:

```
git clone git@github.com:PostDispatchInteractive/app-template.git your-project-name
```

3. Run the following commands to set up the new project.

```
cd your-project-name

mkvirtualenv your-project-name

pip install -r requirements.txt

npm install

fab bootstrap
```

4. The bootstrap process will create a new Google sheet for you, which you can edit. If you already have created a spreadsheet that you would rather use instead, then change COPY_GOOGLE_DOC_KEY to your preferred spreadsheet's key in `app_config.py`.

5. Share your spreadsheet with both `pdstltoday@p-d-interactive-oauth.iam.gserviceaccount.com` and `pdstltoday@gmail.com`.

6. Change the owner of your spreadsheet to `pdstltoday@gmail.com`. All Post-Dispatch apps and projects should be owned by this account.

7. Run the following command to download your spreadsheet locally.

```
fab text
```

8. You are now ready to begin editing templates, writing code and building the app! Continue reading to see how.


Editing contexts / templates
----------------------------

The app-template uses the [copytext](https://copytext.readthedocs.io/en/0.2.1/) library to store your spreadsheet data in the `COPY` variable, which is available to all of your templates.

Templates are written in the [Jinja2](https://jinja.palletsprojects.com/en/2.10.x/) templating language. It has a Python-like syntax. If you want to iterate over the rows of the `restaurants` sheet in your Google spreadsheet, you might write template code like this:

```
{% for restaurant in COPY.restaurants %}
	<h2>{{ restaurant.name }}</h2>
	<p>{{ restaurant.address }}</p>
{% endfor %}
```

If you need to do calculations or somehow transform data from the spreadsheet before passing that data to the template, you must do that work within the appropriate view in `app.py`. After running the calculation, store your new values in the `context` variable. That will make them available for use on the template. For example:

The index() view in app.py:

```
@app.route('/')
def index():
    context = make_context()
    context['todays_date'] = str( datetime.datetime.now() )
    return make_response(render_template('index.html', **context))
```

The index.html template:

```
	<h1>My awesome web page</h1>
	<p>{{ todays_date }}</p>
```



Fabric commands
---------------

1. Update the local copy of the spreadsheet.

```
fab text
```

2. Run the local development web server. (Open http://localhost:8000 in your browser afterwards)

```
fab app
```

3. Render all web files locally.

```
fab render
```

4. Deploy the project to the P-D staging server (graphics.stltoday.com).

```
fab staging main deploy
```

5. Deploy the project to the P-D production server (staging-graphics.stltoday.com).

```
fab production main deploy
```


Things to remember
------------------

* Make sure the "format" of any date/time columns in your Google sheet has been set to "plain text".
	* Change it by highlighting the entire column, then selecting `Format > Number > Plain text` in the menu bar.

* You must use `fab text` to fetch the latest version of your spreadsheet. It does not download automatically.



