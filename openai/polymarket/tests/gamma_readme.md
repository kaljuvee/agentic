# Polymarket Gamma API Data Structure

This document explains the structure and contents of the data retrieved from the Polymarket Gamma API endpoint (`https://gamma-api.polymarket.com/markets`).

## Overview

The API returns an array of market objects, each representing a prediction market on the Polymarket platform. The data is saved in `data/markets.json`.

## Market Object Structure

Each market object contains the following key fields:

### Basic Information
- `id`: Unique identifier for the market
- `question`: The prediction market question
- `slug`: URL-friendly version of the question
- `description`: Detailed description of the market and its resolution criteria
- `category`: Market category (e.g., "Crypto", "US-current-affairs", "Pop-Culture")
- `endDate`: ISO timestamp when the market closes
- `active`: Boolean indicating if the market is currently active
- `closed`: Boolean indicating if the market is closed
- `archived`: Boolean indicating if the market is archived

### Market Details
- `conditionId`: Unique identifier for the market condition
- `marketType`: Type of market (e.g., "normal", "scalar")
- `outcomes`: Array of possible outcomes
- `outcomePrices`: Array of prices for each outcome
- `volume`: Total trading volume
- `liquidity`: Available liquidity in the market

### Resolution Information
- `resolutionSource`: Source used to determine the market outcome
- `marketMakerAddress`: Ethereum address of the market maker
- `closedTime`: Timestamp when the market was closed

### Additional Metadata
- `image`: URL to market image
- `icon`: URL to market icon
- `twitterCardImage`: URL to Twitter card image
- `createdAt`: Timestamp of market creation
- `updatedAt`: Timestamp of last update

## Example Market Categories

The data includes markets across various categories:
1. Crypto (Bitcoin price predictions, DeFi metrics)
2. US Current Affairs (Election predictions, Supreme Court)
3. Pop Culture (Entertainment events, Sports)
4. Coronavirus (COVID-19 related predictions)

## Data Usage

This data can be used to:
1. Analyze market activity and trading volumes
2. Track prediction accuracy across different categories
3. Study market liquidity and pricing
4. Monitor market resolution sources and criteria

## Notes

- All timestamps are in UTC
- Prices are represented in the platform's native token
- Some fields may be null or empty depending on the market type and status 