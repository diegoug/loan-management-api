# loan-management-api
loan-management-api

### Makefile Instructions


## Usage
```
make <command>
```

## Commands

- **start-development**: Start development environment.
- **stop-development**: Stop development environment.
- **create-network**: Create Docker network for microservices.
- **help**: Show available commands, options, examples, and tips.

## Options for `start-development` Command

- `DEBUG=true`: To debug the microservice.
- `BUILD_IMAGE=true`: To build the Docker image.
- `BUILD_OPTIONS=<value>`: Possible values: `--no-cache`. Applies only if `BUILD_IMAGE=true`.
- `DETACH=true`: To run `docker-compose up` with `-d`.

## Examples

1. **Start development environment**
    ```
    make start-development
    ```

2. **Debug microservice**
    ```
    make start-development DEBUG=true
    ```

3. **Build Docker image**
    ```
    make start-development BUILD_IMAGE=true
    ```

4. **Debug microservice and build Docker image with `--no-cache` option**
    ```
    make start-development DEBUG=true BUILD_IMAGE=true BUILD_OPTIONS=--no-cache
    ```

5. **Build Docker image with `--no-cache` option**
    ```
    make start-development BUILD_IMAGE=true BUILD_OPTIONS=--no-cache
    ```

6. **Run `docker-compose up` with `-d`**
    ```
    make start-development DETACH=true
    ```

7. **Debug microservice and run `docker-compose up` with `-d`**
    ```
    make start-development DEBUG=true DETACH=true
    ```

## Tips

- It is recommended to run `make start-development BUILD_IMAGE=true` when a Python dependency is added to `requirements.txt`.
- It is recommended to run `make start-development BUILD_IMAGE=true BUILD_OPTIONS=--no-cache` when a system dependency is added to the `Dockerfile`.
- If you're developing, you can install system or Python dependencies in the container without the need to run `make start-development` with `BUILD_IMAGE=true` if `DEBUG=true` is set. However, keep in mind that making changes to the `Dockerfile` or `docker-compose` file will cause Docker to reload the container and you'll lose any manually installed dependencies.

