# A https friendly docker image for quakejs

This repo contains a Dockerfile and associated files to conveniently package [quakejs](https://github.com/begleysm/quakejs) for easy https-friendly deployment. 

A pre-built image for both linux/amd64 and linux/arm64 can be [found here](https://github.com/users/neonwatty/packages/container/package/quakejs-https).

This image is used as the base for a [convenient https deployment strategy using kamal 2](https://github.com/neonwatty/kamal-quake).

Parts of this Docker pattern were inspired by this great http-friendly [docker image for quakejs](https://github.com/treyyoder/quakejs-docker).


## Build and setup

To build the image cd into the main repo and

```bash
docker build . -t quakejs-https
```

Then run with

```bash
docker run -it -p 80:80 -p 27961:27961 -e SERVER=127.0.0.1 -e HTTP_PORT=80 quakejs-https
```

However because there are no certs (to be handled by kamal) you will only see the JS logo screen.  

To use the image and see its current capabilities you will need to deploy (to localhost even) using [the current kamal setup](https://github.com/neonwatty/kamal-quake).
