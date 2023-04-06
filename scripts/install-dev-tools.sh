# Install Python-related dependencies.
pip install -e .[rest]

# Install npm-related dependencies.
cd frontend/
npm install
cd -