#%%
import pandas as pd
import joblib
import logging
import numpy as np

def main():
    """
    Loads and preprocesses data, loads model, generates 
    predictions, and logs to prediction.log
    """

    # Load data to be scored
    X_val = pd.read_csv('data/prediction_data.csv')

    # Preprocess data
    prep_pipeline = joblib.load('models/prep_pipeline.joblib')
    X_val = prep_pipeline.transform(X_val)    

    # Load model
    model = joblib.load('models/model.joblib')
    
    # Generate predictions
    predictions = np.exp(model.predict(X_val))
    
    # Log predictions
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    f_handler = logging.FileHandler('predictions.log')
    f_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    f_handler.setFormatter(f_format)
    logger.addHandler(f_handler)
    logger.info(f'predictions: {predictions}')

if __name__ == '__main__':
    main()

# %%