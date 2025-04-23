# Dice Authentication

The project is comprised of 2 sub-projects: `submit` and `dice-auth-service`.

## Submit

`submit` is a program that can be used to submit device entries to a `Redis` Database. The source code can be found in `src/redis_submit.c`. First of all, install `redis`, `redis-lib` and OpenSSL library:
```bash
sudo apt-get install redis-server libhiredis-dev libssl-dev

# Now redis should run. You can verify it:
redis-cli ping
PONG
```

Now you can clone the repository and build `submit` by running:
```bash
git clone git@github.com:nubificus/dice-auth.git
cd dice-auth
make submit
```

And now you can submit a new device entry to the database by running:

```bash
./submit UDS(MAC) [redis-IP]
```
Internally, `submit` will generate the Root certificate of the device using the unique device secret (the MAC address) and will submit a new entry to the Redis database. That entry will contain the certificate that will be used later to verify incoming attestation certificates.

## `list` and `del`
Correspondingly, you can also build the `list` and `del` operations, useful for listing the items of the database, or removing an item based on its UDS.

Use `make ls` or `make delete` to build each one. And use them like:

```bash
./list [redis-IP]
./del UDS [redis-IP]
```

## Dice Auth Service

This is a simple HTTP server that authorizes incoming Attestation certificates. Actually, the server expects `POST` request that contain the attestation certificate, e.g:
```bash
curl -X POST <dice-auth-http-endpoint> -H "Content-Type: text/plain" --data-binary @/path/to/attestation.pem
```
Furthermore, the HTTP server can retrieve the IP of the Redis database from the `REDIS_HOST` or `REDIS_SERVICE_SERVICE_HOST` environment variable (in Kubernetes setups, the second variable is probably set automatically). Otherwise, it will attempt to find the database in localhost.

### Build and Run
```bash
make dice_auth
make run
```
## Cleanup
```bash
make clean
```
