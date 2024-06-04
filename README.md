## README.md

# Loan Management API

This project implements a REST API using Django Rest Framework to manage and monitor customer loans and payments. 

## Features

- **Customer Management:**
    - Create and retrieve customers. Each customer has a unique `external_id`, a `score` representing their credit limit, and a status ("Active" or "Inactive").
- **Loan Management:**
    - Create and retrieve loans. Loans are associated with a customer and validated against their credit limit. Different loan statuses are handled: "Pending", "Active", "Rejected", and "Paid".
- **Payment Management:**
    - Create and retrieve payments. Payments are associated with a customer and automatically distributed among their loans. It's validated that the payment doesn't exceed the customer's total debt. Payment statuses "Pending", "Completed", and "Rejected" are managed.
- **Payment Details:**
    - Payment details are automatically generated when a payment is created, showing the distribution of the payment amount among the customer's loans.

## Business Rules

- **Credit Limit:** Loans cannot exceed the customer's credit limit.
- **Total Debt:** Payments cannot exceed the customer's total debt.
- **Loan Statuses:** Loans are created in "Pending" status and can only be rejected in that state. Once a loan is "Active", it cannot be rejected.
- **Payment Statuses:** Payments are created in "Pending" status. A payment can only be confirmed or rejected if it's in "Pending" status.
- **Outstanding Update:** A loan's `outstanding` is updated when a payment is made.
- **Status Change to "Paid":** A loan's status changes to "Paid" when the `outstanding` reaches 0.

## Running the Application

### Prerequisites

- Docker
- Docker Compose

### Steps

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/your-username/loan-management-api.git
   cd loan-management-api
   ```

2. **Create the Docker Network:**

   ```bash
   make create-network
   ```

3. **Start the Development Environment:**

   ```bash
   make start-development
   ```

## Running the Tests

To run the tests inside the container:

1. Access the container:

   ```bash
   docker exec -it loan-management-api_backend_1 bash
   ```

2. Run the tests:

   ```bash
   python manage.py test
   ```

## Endpoints

**Create Admin User**

- **URL:** `/register-admin/`
- **Method:** `POST`
- **Data:**
  - `secret_key`: Secret key (defined in `settings.py`).
  - `username`: Admin username.
  - `password`: Admin password.

**Create User**

- **URL:** `/register-user/`
- **Method:** `POST`
- **Headers:**
  - `Authorization`: `Api-Key <ADMIN_API_KEY>`
- **Data:**
  - `username`: Username.
  - `password`: Password.
  - `is_admin`: (optional) Boolean, indicates if the user is an admin.

**Customer CRUD**

- **Base URL:** `/loan/api/v1/customers/`
- **Methods:** `GET`, `POST`, `PUT`, `PATCH`, `DELETE`

**Loan CRUD**

- **Base URL:** `/loan/api/v1/loans/`
- **Methods:** `GET`, `POST`, `PUT`, `PATCH`, `DELETE`

**Payment CRUD**

- **Base URL:** `/loan/api/v1/payments/`
- **Methods:** `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
- **Confirm Payment:** `/loan/api/v1/payments/{pk}/confirm/` (Method: `PATCH`)

**Payment Details CRUD**

- **Base URL:** `/loan/api/v1/payment-details/`
- **Methods:** `GET` (read-only)

## Usage Examples

### Get Customer Balance

```bash
curl -H "Authorization: Api-Key <API_KEY>" http://localhost:8000/loan/api/v1/customers/<CUSTOMER_ID>/balance/
```

### Create a Loan

```bash
curl -X POST -H "Authorization: Api-Key <API_KEY>" -H "Content-Type: application/json" -d '{
  "external_id": "external_01-01",
  "customer_id": 1,
  "amount": 500.0,
  "contract_version": "1.0",
  "maximum_payment_date": "2024-02-12T22:29:27.177914Z"
}' http://localhost:8000/loan/api/v1/loans/
```

### Create a Payment

```bash
curl -X POST -H "Authorization: Api-Key <API_KEY>" -H "Content-Type: application/json" -d '{
  "external_id": "payment_01",
  "customer_id": 1,
  "total_amount": 500.0,
  "paid_at": "2023-06-12T12:00:00Z"
}' http://localhost:8000/loan/api/v1/payments/
```

## Dockerization

The application has been dockerized for easy deployment and configuration.

## Makefile

A Makefile is included to simplify the execution of common commands, such as starting and stopping the development environment and creating the Docker network.

```md
```bash
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
```

## Unit Tests

Unit tests have been developed to verify the correct functionality of different components of the application.

## API Documentation

You can use tools like Postman or Swagger to explore the API endpoints and their parameters.


This updated README.md provides a detailed and understandable explanation of the project, including how to run the application, run tests within the container, use the API endpoints, and other important information about the project's development.

