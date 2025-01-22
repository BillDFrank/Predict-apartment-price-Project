from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def evaluate_model_performance(y_test, predictions):
    # Calculate Mean Absolute Error (MAE)
    mae = mean_absolute_error(y_test, predictions)

    # Calculate Mean Squared Error (MSE)
    mse = mean_squared_error(y_test, predictions)

    # Calculate Root Mean Squared Error (RMSE)
    rmse = np.sqrt(mse)

    # Calculate R-squared (R2)
    r2 = r2_score(y_test, predictions)

    return {
        'MAE': mae,
        'MSE': mse,
        'RMSE': rmse,
        'R2': r2
    }


def analyze_precision(X_test, y_test, predictions):
    # Create a DataFrame to store the results
    results = pd.DataFrame({'Actual': y_test, 'Predicted': predictions.flatten()})

    # Calculate the absolute error
    results['Absolute Error'] = np.abs(results['Actual'] - results['Predicted'])

    # Define price ranges
    price_ranges = np.arange(50000, 800001, 50000)

    # Create a list to store precision data
    precision_data = []

    # Calculate precision for each price range
    for lower_price in price_ranges:
        upper_price = lower_price + 50000
        subset = results[(results['Actual'] >= lower_price) &
                         (results['Actual'] < upper_price)]
        mae = subset['Absolute Error'].mean()
        precision_data.append(
            {'Price Range': f'{lower_price}-{upper_price}', 'MAE': mae})

    # Create a DataFrame from the precision data
    precision_df = pd.DataFrame(precision_data)

    # Plot the precision data
    plt.figure(figsize=(12, 6))
    sns.barplot(data=precision_df, x='Price Range', y='MAE')
    plt.title('Mean Absolute Error (MAE) by Price Range')
    plt.xlabel('Price Range')
    plt.ylabel('MAE')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Distribution plot
    plt.figure(figsize=(12, 6))
    sns.kdeplot(y_test, label='Actual Values', color='blue', fill=True)
    sns.kdeplot(predictions, label='Predicted Values', color='red', fill=True)
    plt.title('Distribution of Actual vs. Predicted Values')
    plt.xlabel('Values')
    plt.ylabel('Density')
    plt.legend()
    plt.grid(True)
    plt.show()

    # Prediction vs. Actual Scatter Plot
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, predictions)
    plt.title('Prediction vs. Actual Scatter Plot')
    plt.xlabel('Actual Values')
    plt.ylabel('Predicted Values')
    plt.grid(True)
    plt.show()

