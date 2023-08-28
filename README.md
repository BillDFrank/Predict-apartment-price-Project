# Apartment Price Prediction Project

## Table of Contents

- [Introduction](#introduction)
- [Data Sources](#data-sources)
- [Data Preprocessing](#data-preprocessing)
- [Model Architecture](#model-architecture)
- [Training Process](#training-process)
- [How to Use for Predictions](#how-to-use-for-predictions)

## Introduction

The Apartment Price Prediction Project aims to predict the price of apartments based on their characteristics, including location, number of rooms, area, and more. This project uses data science and machine learning techniques to provide accurate price predictions for real estate properties. It's a personal project, for personal use only.

## Data Sources

The project uses data scraped from the ImoVirtual listing website. The following information is collected for each property:

- URL for advertising
- Title
- Price
- Location
- Number of Rooms
- Area
- Number of Bathrooms
- Listing Type
- Pictures of the advertising

## Data Preprocessing

1. **Cleaning and Structuring**: The scraped data is cleaned and structured to ensure consistency and accuracy. Features are aligned properly and missing values are handled appropriately.

2. **Feature Engineering**: Additional features are created, such as the domain extracted from the URL and ratios like rooms-to-area, to enhance the predictive power of the model.

3. **Normalization and Encoding**: Numerical features are normalized, and categorical features like location and listing type are encoded using one-hot encoding.

## Model Architecture

The project uses a machine learning model for regression-based prediction. The model architecture consists of the following components:

- Input Layer: Combines numerical and encoded categorical features.
- Hidden Layers: Multiple layers with varying units and activation functions.
- Output Layer: Single node for predicting the apartment's price.

## Training Process

1. **Data Splitting**: The dataset is split into training and testing sets using a predefined ratio.
2. **Model Selection**: Various regression models are considered, and the chosen model is fine-tuned through experimentation.
3. **Hyperparameter Tuning**: Hyperparameters like learning rate, batch size, and activation functions are optimized.
4. **Model Training**: The model is trained on the training dataset, and its performance is evaluated using metrics like Mean Squared Error (MSE) on the testing dataset.

## How to Use for Predictions

To use the trained model for price predictions of new properties, follow these steps:

1. Install the required libraries by running `pip install -r requirements.txt`.
2. Prepare the input data for the new property, including its characteristics.
3. Utilize the trained model (saved weights) to predict the price using the provided code snippets in the `predict_price.py` file.

Please note that accurate predictions depend on the quality and relevance of input data. The model's predictions are based on patterns observed in the training data.
