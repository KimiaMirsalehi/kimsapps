import streamlit as st
import statsmodels.api as sm
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import plotly.figure_factory as ff
from statsmodels.stats.outliers_influence import variance_inflation_factor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np
import base64
import hmac


# Function to load and process the dataset
def load_data():
    longley = sm.datasets.longley.load_pandas().data
    longley['YEAR'] = longley['YEAR'].astype(str)  # Convert Year to str for coloring later
    return longley

# Function to display summary statistics
def display_summary_statistics(data):
    st.write("Summary Statistics:")
    st.write(data.describe())

# Function to display correlation matrix
def display_correlation_matrix(data):
    corr_matrix = data.corr()
    st.write("Correlation Matrix:")
    st.write(corr_matrix)

    # Heatmap of the correlation matrix
    st.write("Correlation Matrix Heatmap:")
    fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", color_continuous_scale='RdBu_r')
    st.plotly_chart(fig)

# Function to display scatter plot matrix
def display_scatter_plot_matrix(data):
    st.write("Scatter Plot Matrix:")
    fig = px.scatter_matrix(data, dimensions=data.columns, title="Scatter Plot Matrix")
    st.plotly_chart(fig)

# Function to fit and display multiple linear regression model
def fit_model(data, x_cols, y_col):
    # Filter numeric columns for imputation
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    data_filled = data.copy()
    data_filled[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].max())

    X = data_filled[x_cols]
    y = data_filled[y_col]
    X = sm.add_constant(X)
    
    try:
        model = sm.OLS(y, X).fit()
        return model
    except Exception as e:
        st.error(f"Error fitting the model: {e}")
        return None

    

# Function to display model summary
def display_model_summary(model):
    st.write("Model Summary:")
    st.write(model.summary())

# Function to plot actual vs predicted values
def plot_actual_vs_predicted(model, X, y):
    st.write("Actual vs Predicted Employment:")
    X_with_const = sm.add_constant(X)
    predicted = model.predict(X_with_const)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=y, y=predicted, mode='markers', name='Actual vs Predicted', marker=dict(color='blue')))
    fig.add_trace(go.Scatter(x=[y.min(), y.max()], y=[y.min(), y.max()], mode='lines', name='Ideal', line=dict(color='red', dash='dash')))
    fig.update_layout(xaxis_title="Actual Employment", yaxis_title="Predicted Employment", title="Actual vs Predicted Employment")
    st.plotly_chart(fig)


# Function to plot residuals
def plot_residuals(model, X, y):
    X_with_const = sm.add_constant(X)
    residuals = y - model.predict(X_with_const)
    st.write("Residuals vs Predicted Employment:")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=model.predict(X_with_const), y=residuals, mode='markers', name='Residuals', marker=dict(color='blue')))
    fig.add_trace(go.Scatter(x=model.predict(X_with_const), y=[0]*len(residuals), mode='lines', name='Zero Line', line=dict(color='red', dash='dash')))
    fig.update_layout(xaxis_title="Predicted Employment", yaxis_title="Residuals", title="Residuals vs Predicted Employment")
    st.plotly_chart(fig)

    st.write("Residuals Distribution:")
    fig = px.histogram(residuals, nbins=30, title="Residuals Distribution", marginal="box", opacity=0.7)
    st.plotly_chart(fig)


# Function to calculate and display VIF
def display_vif(X):
    vif_data = pd.DataFrame()
    vif_data["Feature"] = X.columns
    vif_data["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]
    st.write("Variance Inflation Factors (VIF):")
    st.write(vif_data)

# Function to plot a 3D scatter plot
def plot_3d_scatter(data, x_var, y_var, z_var):
    st.write("3D Scatter Plot:")
    fig = px.scatter_3d(data, x=x_var, y=y_var, z=z_var, color='YEAR', title=f"3D Scatter Plot: {x_var} vs {y_var} vs {z_var}")
    st.plotly_chart(fig)


# Function to plot parallel coordinates
def plot_parallel_coordinates(data):
    st.write("Parallel Coordinates Plot:")
    fig = px.parallel_coordinates(data, color='TOTEMP', labels={'GNPDEFL': 'GNP Deflator', 'GNP': 'GNP', 'UNEMP': 'Unemployed', 'ARMED': 'Armed Forces', 'POP': 'Population', 'YEAR': 'Year', 'Employed': 'Employed'}, title="Parallel Coordinates Plot")
    st.plotly_chart(fig)

# Function to plot time series
def plot_time_series(data):
    st.write("Time Series Plot:")
    fig = px.line(data, x='YEAR', y='TOTEMP', title="Time Series Plot: Employment Over Time")
    st.plotly_chart(fig)


def calculate_regression_metrics(model, X, y):
    X_with_const = sm.add_constant(X)
    predicted = model.predict(X_with_const)
    
    r2 = r2_score(y, predicted)
    mae = mean_absolute_error(y, predicted)
    mse = mean_squared_error(y, predicted)
    rmse = np.sqrt(mse)
    
    return r2, mae, mse, rmse

# Function to display regression metrics
def display_regression_metrics(model, X, y):
    r2, mae, mse, rmse = calculate_regression_metrics(model, X, y)
    st.write("### Regression Metrics")
    st.write(f"**R-squared:** {r2:.4f}")
    st.write(f"**Mean Absolute Error (MAE):** {mae:.4f}")
    st.write(f"**Mean Squared Error (MSE):** {mse:.4f}")
    st.write(f"**Root Mean Squared Error (RMSE):** {rmse:.4f}")

def calculate_yoy_diff(data):
    numeric_columns = data.select_dtypes(include=[np.number]).columns  # Select numeric columns
    data_diff = data[numeric_columns].diff().dropna()
    data_diff.columns = [col + '_diff' for col in data_diff.columns]
    return data_diff

def check_password():
    """Returns `True` if the user has the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Password incorrect")
    return False


# Function to set background image and primary color
def set_background_and_primary_color():
    background_image_url = "https://get.wallhere.com/photo/simple-background-minimalism-humor-artwork-death-dark-humor-brand-product-243890.jpg"  # Replace with the URL to your background image
    
    css = f"""
    <style>
    .stApp {{
       background-image: url("{background_image_url}");
       background-size: cover;
    }}
    .stButton > button {{
       background-color: #6a0dad;
       color: white;
    }}
    .stSelectbox > div > div > div {{
       color: #6a0dad;
    }}
    .stSidebar > div {{
       background-color: #6a0dad;
    }}
    .css-1e5imcs {{
       color: #6a0dad;
    }}
    .css-1v3fvcr {{
       color: #6a0dad;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def main():
    # Password protection
    if not check_password():
        st.stop()  # Do not continue if check_password is not True.
    set_background_and_primary_color()

    # Your main app logic starts here
    st.title("Longley Dataset Analysis")

    # Load data
    data = load_data()

    # Display data overview
    st.write("Dataset Overview:")
    st.write(data.head())

    # User input for model fitting
    st.sidebar.title("Model Input")

    transform_data = st.sidebar.checkbox("Apply Year-over-Year Difference Transformation")

    # Apply transformation if selected
    if transform_data:
        data_diff = calculate_yoy_diff(data)
        data = pd.concat([data, data_diff], axis=1)

    available_columns = data.columns.tolist()
    x_cols = st.sidebar.multiselect("Select independent variables (X)", options=available_columns)
    y_col = st.sidebar.selectbox("Select dependent variable (Y)", options=available_columns)

    # Fit the model
    if x_cols and y_col:
        model = fit_model(data, x_cols, y_col)

    # Sidebar for selecting visualization
    st.sidebar.title("Select Visualization")
    visualization = st.sidebar.selectbox("Choose a visualization to display", 
                                         options=["Summary Statistics", "Correlation Matrix", 
                                                  "Scatter Plot Matrix", "3D Scatter Plot", 
                                                  "Parallel Coordinates Plot", "Time Series Plot", "Model Summary", 
                                                  "Actual vs Predicted", "Residuals", "VIF"])

    # Variables for 3D scatter plot
    if visualization == "3D Scatter Plot":
        st.sidebar.title("3D Scatter Plot Variables")
        x_var = st.sidebar.selectbox("Select X variable", options=available_columns)
        y_var = st.sidebar.selectbox("Select Y variable", options=available_columns)
        z_var = st.sidebar.selectbox("Select Z variable", options=available_columns)

    # Display the selected visualization
    if visualization == "Summary Statistics":
        display_summary_statistics(data)
    elif visualization == "Correlation Matrix":
        display_correlation_matrix(data)
    elif visualization == "Scatter Plot Matrix":
        display_scatter_plot_matrix(data)
    elif visualization == "3D Scatter Plot":
        plot_3d_scatter(data, x_var, y_var, z_var)
    elif visualization == "Parallel Coordinates Plot":
        plot_parallel_coordinates(data)
    elif visualization == "Time Series Plot":
        plot_time_series(data)
    elif visualization == "Model Summary" and x_cols and y_col:
        display_model_summary(model)
        display_regression_metrics(model, data[x_cols], data[y_col])
    elif visualization == "Actual vs Predicted" and x_cols and y_col:
        plot_actual_vs_predicted(model, data[x_cols], data[y_col])
    elif visualization == "Residuals" and x_cols and y_col:
        plot_residuals(model, data[x_cols], data[y_col])
    elif visualization == "VIF" and x_cols and y_col:
        display_vif(sm.add_constant(data[x_cols]))

# Run the app
if __name__ == "__main__":
    main()

