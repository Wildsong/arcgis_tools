# Locator App

A web app to test the Clatsop County Locator

I'm thinking there is no server component for this one, just a client.
The server is Portal.

The point of writing this is to test how I can use the locator services
built with ArcGIS Pro. The docs are vague and the form that Esri gives
me just yapps "Unable to complete operation" no matter what I say.

## Major components

Client side / front end: Runs in the browser and does queries to backendusing Apollo GraphQL client.

* React
* react-bootstrap
* Parcel bundler
* Node 18 (LTS) (runs "serve" just as a very simple static HTTP server on port 8080)

I wonder if I need any ArcGIS code in here?
I think it's just REST.

## Prerequisites for set up

You need Node, either in Docker or at the shell. Currently I am using "nvm" and working from the shell
for development and Docker in deployment.

Install nvm in three steps, crazy how easy this is compared to "apt", which installs about 50 (outdated) packages.

    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.37.2/install.sh | bash
    Now log out and back in to refresh environment
    nvm install node

## Development

In theory you can run in development mode anywhere, in practice I have found
that working on cc-testmaps is more reliable. 

Command to copy from local source to cc-testmaps, for testing there.

    cd ~/Documents/source
    rsync -av arcgis_tools rsync://cc-testmaps/source

### Browser app (aka "client" aka "front end" bu there is no back end.)

Start the front end running,

    cd client
    npm install
    npm start

Debugging in Visual Studio Code: The [Parcel site has tips.](https://parceljs.org/recipes/debugging/) 

Basically you start the client running, it automatically builds source
maps.  Look in the .vscode/launch.json file; there it will be set up
to find the source maps. Then run the VS Code debugger, by selecting
"Launch client" and hitting F5. This will open the app in Chrome. You
should be able to do all the usual breakpoint / single-step / look at
values things like a real program. (Come on, it IS a "real program"
jeez get some self-esteem.)