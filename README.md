# chatter

A hobby real-time chatting web application.

## Tech Stack

### Frontend

- JavaScript
- React
- React Router
- Zustand
- Material UI

### Backend

- Django
- Django Rest Framework
- Django Channels
- PostgreSQL

## Usage

Setup the development environment by hopping on to VSCode and taking advantage of the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension.
When you made it into the development container, do the following:

1. Apply Django-related migrations to setup the database: `python manage.py migrate`.
2. Bundle JavaScript files by doing the following:

```console
# Assuming your at the project root directory
cd frontend/
npm run build
cd ..
```

3. Start the Daphne server: `python manage.py runserver`.

And you should be good to go!
