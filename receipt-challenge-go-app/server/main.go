package main

import (
	"bytes"
	"fmt"
	"io"
	"net/http"

	"github.com/jtnoble/receipt-challenge-go-app/internal"

	"github.com/google/uuid"
)

type Entry struct {
	points int
}

var entries = make(map[string]Entry)

// POST: /receipts/process
func processReceipt(res http.ResponseWriter, req *http.Request) {
	if req.Method != "POST" {
		http.Error(res, `{"description": "Invalid HTTP Method"}`, http.StatusBadRequest)
		return
	}

	body, err := io.ReadAll(req.Body)
	if err != nil {
		http.Error(res, "Error reading body", http.StatusInternalServerError)
		return
	}

	req.Body = io.NopCloser(bytes.NewReader(body))

	if !internal.ValidateRecept(req.Body) {
		http.Error(res, `{"description": "The receipt is invalid."}`, http.StatusBadRequest)
		return
	}

	id := uuid.New().String()
	entries[id] = Entry{points: internal.CalculatePoints(bytes.NewReader(body))}

	fmt.Fprintf(res, `{"id": "%s"}`, id)

}

// GET: /receipts/{id}/points
func getPoints(res http.ResponseWriter, req *http.Request) {
	if req.Method != "GET" {
		http.Error(res, `{"description": "Invalid HTTP Method"}`, http.StatusBadRequest)
		return
	}

	id := req.PathValue("id")

	points, exists := entries[id]

	if !exists {
		http.Error(res, `{"description": "No receipt found for that ID."}`, http.StatusNotFound)
		return
	}

	fmt.Fprintf(res, `{"points": %d}`, points.points)

}

func main() {
	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprint(w, "You have entered the API!")
	})
	http.HandleFunc("/receipts/process", processReceipt)
	http.HandleFunc("/receipts/{id}/points", getPoints)

	fmt.Println("Server listening on port 8080...")
	http.ListenAndServe(":8080", nil)
}
