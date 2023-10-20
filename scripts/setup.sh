# Install Python-related dependencies.
pip install -e .[rest]

# Install npm-related dependencies.
cd frontend/
npm install
cd -

# Add .env file with the necessary envars.
echo "SECRET_KEY=123-this-is-a-dev-key" > .env


# Apply Django-related migrations to setup the database.
python manage.py migrate

# Bundle JavaScript files (this needs to be re-run manually if frontend changes are made).
cd frontend/
npm run build
cd -
