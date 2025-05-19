# turbo.art

A playground for creative exploration that uses [SDXL Turbo](https://huggingface.co/stabilityai/sdxl-turbo) for real-time image editing. Try it now at [https://turbo.art](https://turbo.art)!

![turbo-art](https://github.com/modal-labs/turbo-art/assets/5786378/bb185f24-9946-4c26-a7ca-7c8732ea77f0)

The entire app is serverless and hosted on [Modal](https://modal.com/).

## Developing locally

### File structure

- [turbo_art.py](./turbo_art.py) - model endpoint and FastAPI web server (<150 lines of code!)
- [src/](./src) - Svelte frontend

### Requirements

To run this for yourself, you will need:

1. Modal installed and set up locally, as well as FastAPI

```shell
pip install modal fastapi
modal setup
```

2. [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) installed

### Iterate

During development, it's useful to have both the frontend and the Modal application automatically react to changes in the code. To do this, you'll need to run two processes.

First, in one shell session, run:

```shell
npm install
npm run build:watch
```

Then, in another shell session, run:

```shell
modal serve turbo_art.py
```

In the terminal output, you'll find a URL that you can visit to use your app. While the [`modal serve`](<(https://modal.com/docs/guide/webhooks#developing-with-modal-serve)>) process is running, changes to any of the project files will be automatically applied. `Ctrl+C` will stop the app.

### Deploy

Once you're happy with your changes, [deploy](https://modal.com/docs/guide/managing-deployments#creating-deployments) your app:

```shell
npm run build
modal deploy turbo_art.py
```

In the terminal output, you'll find a different URL that you can visit to use your app. We chose to use Modal's [custom domains](https://modal.com/docs/guide/webhooks#custom-domains) feature to make the URL more memorable. Without a custom domain, you can still [select](https://modal.com/docs/guide/webhook-urls#user-specified-urls) part of the the `modal.run` subdomain you're assigned.

Note that leaving the app deployed on Modal doesn't cost you anything! Modal apps are serverless and scale to 0 when not in use.
