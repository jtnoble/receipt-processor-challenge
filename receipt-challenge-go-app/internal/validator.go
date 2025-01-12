package internal

import (
	"encoding/json"
	"io"
	"regexp"
	// "fmt"
)

/* Validate Receipt
 * Return false if any errors are found with formatting
 * Otherwise, return true
 */
func ValidateRecept(r io.ReadCloser) bool {
	// decode json
	decoder := json.NewDecoder(r)
	decoder.DisallowUnknownFields()

	var receipt Receipt
	err := decoder.Decode(&receipt)

	if err != nil {
		return false
	}

	// match regex for each field
	retailerRegex := regexp.MustCompile(`^[\w\s-&]+$`)
	purchaseDateRegex := regexp.MustCompile(`^(19[0-9]{2}|20[0-9]{2})-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$`) // YYYY-MM-DD: 1900->2099, 01->12, 01->31
	purchaseTimeRegex := regexp.MustCompile(`^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$`)                             // HH:MM: 00->23, 00->59
	totalRegex := regexp.MustCompile(`^\d+\.\d{2}$`)
	itemShortDescriptionRegex := regexp.MustCompile(`^[\w\s\-]+$`)
	itemPriceRegex := regexp.MustCompile(`^\d+\.\d{2}$`)

	if receipt.Retailer == "" || !retailerRegex.MatchString(receipt.Retailer) {
		// fmt.Print("problem at: retailer")
		return false
	}
	if receipt.PurchaseDate == "" || !purchaseDateRegex.MatchString(receipt.PurchaseDate) {
		// fmt.Print("problem at: purchasedate")
		return false
	}
	if receipt.PurchaseTime == "" || !purchaseTimeRegex.MatchString(receipt.PurchaseTime) {
		// fmt.Print("problem at: purchasetime")
		return false
	}
	if receipt.Total == "" || !totalRegex.MatchString(receipt.Total) {
		// fmt.Print("problem at: total")
		return false
	}

	if len(receipt.Items) == 0 {
		return false
	}
	for _, item := range receipt.Items {
		if item.ShortDescription == "" || !itemShortDescriptionRegex.MatchString(item.ShortDescription) {
			// fmt.Print("problem at: item shortdesc")
			return false
		}
		if item.Price == "" || !itemPriceRegex.MatchString(item.Price) {
			// fmt.Print("problem at: item price")
			return false
		}
	}

	return true
}
