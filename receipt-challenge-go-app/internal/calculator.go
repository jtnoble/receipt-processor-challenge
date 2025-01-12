package internal

import (
	"bytes"
	"encoding/json"
	"math"
	"strconv"
	"strings"
	"time"
	"unicode"
	// "fmt"
)

/* Calculate Points
 * Input: Bytes from http body
 * Output: Integer value of points rewarded
 */
func CalculatePoints(r *bytes.Reader) int {
	// decode json
	decoder := json.NewDecoder(r)
	decoder.DisallowUnknownFields()
	var receipt Receipt
	err := decoder.Decode(&receipt)
	if err != nil {
		// fmt.Printf("Error decoding JSON: %v", err)
		return 0
	}

	// fmt.Println(receipt.Retailer)

	points := 0

	// One point for every alphanumeric character in the retailer name.
	for _, c := range receipt.Retailer {
		if unicode.IsLetter(c) || unicode.IsDigit(c) {
			// fmt.Println("+1 per character")
			points += 1
		}
	}

	// 50 points if the total is a round dollar amount with no cents.
	totalFloat, _ := strconv.ParseFloat(receipt.Total, 64)
	if totalFloat == math.Floor(totalFloat) {
		// fmt.Println("+50 for total being .00")
		points += 50
	}

	// 25 points if the total is a multiple of 0.25.
	if totalFloat*4 == float64(int(totalFloat*4)) {
		// fmt.Println("+25 for total being multiple of .25")
		points += 25
	}

	// 5 points for every two items on the receipt.
	// fmt.Printf("+%d for amount of items on receipt\n", 5*(len(receipt.Items)/2))
	points += (5 * (len(receipt.Items) / 2))

	// If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer. The result is the number of points earned.
	for _, item := range receipt.Items {
		if len(strings.TrimSpace(item.ShortDescription))%3 == 0 {
			price, _ := strconv.ParseFloat(item.Price, 64)
			// fmt.Printf("+%d points for item being a multiple of 3\n", int(math.Ceil(price*0.2)))
			points += int(math.Ceil(price * 0.2))
		}
	}

	// 6 points if the day in the purchase date is odd.
	d, _ := time.Parse("2006-01-02", receipt.PurchaseDate)
	if d.Day()%2 == 1 {
		// fmt.Println("+6 points for date being odd!")
		points += 6
	}

	// 10 points if the time of purchase is after 2:00pm and before 4:00pm.
	t, _ := time.Parse("15:04", receipt.PurchaseTime)
	startTime := time.Date(t.Year(), t.Month(), t.Day(), 14, 0, 0, 0, t.Location())
	endTime := time.Date(t.Year(), t.Month(), t.Day(), 16, 0, 0, 0, t.Location())
	if t.After(startTime) && t.Before(endTime) {
		// fmt.Println("+10 points since purchase time is between 2pm and 4pm")
		points += 10
	}

	// fmt.Printf("Points: %d", points)
	return points
}
