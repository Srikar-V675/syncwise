open terminal and execute:

0. install requirements.txt inside the environment
`pip install -r requirements.txt
1. make sure pre-commit is installed by executing the below command
`pre-commit install`
2. perform the migrations
`python manage.py makemigrations`
`python manage.py migrate`
3. create the default groups and permissions
`python manage.py create_groups`
4. create superuser to access the admin
`python manage.py createsuperuser`
5. run docker-compose
`docker-compose up --build`
6. access the django-server
type `http://localhost:8050/` in browser.
7. access the admin site: `http://localhost:8050/admin/`. create users in the groups and login using their credentials and play around.


> **NOTE:** Make sure you get all pre-commit tests passed after you commit, if not then make the changes and use `git add .` to add the modified files again and commit it. Refer to the below commit for succesful and failed pre-commits.
> ![succesful](image.png)
> ![failed](image-1.png)


React Part:

1. Install Node.js and npm
Ensure Node.js and npm are installed. Verify with:
'node -v'
'npm -v'

Install Axios to interact with the Django API:
'npm install axios'

library is used to handle Cross-Origin Resource Sharing (CORS) in Django applications
'pip install django-cors-headers'

2. Navigate to your project directory and create a React app
3. Run the following to start the React app:

'npm start'

    'The app will be available at http://localhost:3000.'
    'The src/ folder contains the main React code. Modify src/App.js for your needs.'
