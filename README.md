# Receipt Processor Challenge
Challenge accepted by ["Fetch"](https://github.com/fetch-rewards/receipt-processor-challenge/tree/main) to create a web API meeting specified criteria. Two separate submissions, one Python-Flask based, one Go based

# Wait, Why Python *and* Go?
The challenge prefers that you use Go as your primary language; however, it does not require it. I have been using Python as my primary language for years, and have only installed Go as of the day of receiving the challenge. I decided to give Go a try, while still having a Python solution that I understand better. Both should work separately, but should also end up with the same result.

# Building/Running (Python)
- Clone this repository
- Navigate to your cloned directory so that you are in the same directory as `Dockerfile`
- Build with `docker build --tag receipt-challenge-jtn .`
- Run with `docker run --name receipt-challenge-jtn -p 5000:5000 receipt-challenge-jtn`
- Navigating to `http://localhost:5000/` should show "Receipt Processor Challenge API Live", indicating it is running
- Once running, requests can be made using a method of your choosing. I personally used the VSCode ThunderClient extension

# Building/Running (Go)
- Clone this repository
- Navigate to the `receipt-challenge-go-app` directory
- Run with `go run ./server/main.go`
  - Alternatively, you can build an exe first with `go build -o main.exe ./server/main.go`
- Navigating to `http://localhost:8080/` should show "Receipt Processor Challenge API Live", indicating it is running
- Once running, requests can be made using a method of your choosing. I personally used the VSCode ThunderClient extension

# Endpoints

#### `/receipts/process`
- Methods: POST
- Generates an amount of points based on receipt contents
- Requires a json body following a specified schema
    ```json
        {
            "retailer": "Test Store",
            "purchaseDate": "2025-01-09",
            "purchaseTime": "14:30",
            "total": "50.00",
            "items": [
                {"shortDescription": "item1", "price": "10.00"},
                {"shortDescription": "item2", "price": "20.00"}
            ]
        }
    ```
- Status 200: Returns a UUID to be saved and used for viewing points
    ```json
        {
            "id": "21e1968c-bce4-4a06-a31f-28d7e8cbc6e2"
        }
    ```
- Status 400: JSON input does not match the specified schema

#### `/receipts/<id>/points`
- Methods: GET
- Status 200: Returns the amount of points a receipt totals via UUID
    ```json
        {
            "points": 25
        }
    ```
- Status 404: Could not locate the UUID provided.

# Unit Testing 
A test.py file is provided and utilizes unit testing for most possible outcomes. Running this file is not included in the docker container. As for Go, I did not include unit tests, but would look into doing this in the case of a full-fledged production.
