# import the streamlit library
import streamlit as st

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine


import warnings
warnings.filterwarnings("ignore")

# Define server and database name
server = r'UZZII\SQLEXPRESS' 
database = 'E_COMMERCE'

# Create engine using Windows Authentication

engine = create_engine(
    "mssql+pyodbc://@UZZII\\SQLEXPRESS/E_COMMERCE?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
)


# credentials dictionary
USER_CREDENTIALS = {
    "admin": "admin123",
    "user": "user123"
}

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False


def login():
    st.header("🔐 Welcome to your E-Commerce Hub")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state["authenticated"] = True
            st.success(f"Welcome, {username}!")
            st.rerun()
    
        else:
            st.error("Invalid username or password")

def main_app():

    # loading data
    orders = pd.read_sql('select * from orders',engine)
    order_item_refunds = pd.read_sql('select * from order_item_refunds',engine)
    order_items = pd.read_sql('select * from order_items',engine)
    products = pd.read_sql('select * from products',engine)
    website_pageviews = pd.read_sql('select * from website_pageviews',engine)
    w_sessions = pd.read_sql('select * from w_sessions',engine)


    st.sidebar.title("🧭 Navigation")
    selection = st.sidebar.radio("Go to Section",["Home Page","Key Metrics","Website Performance Analysis","Traffic Source Analysis","Channel Portfolio Management","Business Patterns and Seasonality","Product Analysis","User Analysis"])
    
                                          
    if selection == "Home Page":
        st.markdown(""" 
### 🧸 Client Snapshot:
A fresh-faced startup on a mission to deliver high-quality, huggable stuffed toys. With branding, customer insights, and steady growth in focus, this dashboard helps shape their path to success.
    
                    
### 🎯 Objectives
- Monitor key performance metrics
- Understand website and traffic behavior
- Optimize product and channel strategies
- Deepen customer insights                    
         
       """) 
        

        st.markdown('### 🗂️ Analysis Overview')    
    
        # Data as a list of dictionaries               
        data = [
        {"Section": "Key Metrics", "Description": "Understand overall business health with essential performance indicators."},
        {"Section": "Website Performance Analysis", "Description": "Explore how users interact with the website."},
        {"Section": "Traffic Source Analysis", "Description": "See which channels and campaigns are driving traffic and conversions."},
        {"Section": "Channel Portfolio Management", "Description": "Compare marketing channels to optimize spend and efficiency."},
        {"Section": "Business Patterns and Seasonality", "Description": "Understand how trends and seasonality impact sales and traffic over time."},
        {"Section": "Product Analysis", "Description": "Dive into product performance, sales trends, and refund behavior."},
        {"Section": "User Analysis", "Description": "Customer segmentation and behavior insights."},
        ]
 
        # Create DataFrame
        df_sections = pd.DataFrame(data) 

        # Removes the index and keeps column headers
        st.table(df_sections)



                    

    if selection == "Key Metrics":
        st.header("📊 Performance at a Glance")

        # Start with order_items
        filtered_data = order_items.copy()

        # merge with orders
        filtered_data = filtered_data.merge(orders, how="left", on="order_id",suffixes=("_orderitem", "_order"))

        # merge with products
        filtered_data = filtered_data.merge(products, how="left", left_on="product_id",right_on="product_id",suffixes=("","_products"))

        # merge with refund
        filtered_data = filtered_data.merge(order_item_refunds, how="left", on="order_item_id",suffixes=("","_refunds"))

        # merge with w_sessions
        filtered_data = filtered_data.merge(w_sessions,how="left",left_on="website_session_id",right_on="website_session_id",suffixes=("","_sessions"))

        # Extract Year for filtering
        filtered_data["year"] = filtered_data["created_at_orderitem"].dt.year

        # Extract Month for filtering
        filtered_data["month"] = filtered_data["created_at_orderitem"].dt.month_name()
        month_order = ["January", "February", "March", "April", "May", "June","July", "August", "September", "October", "November", "December"]
        filtered_data["month"] = pd.Categorical(filtered_data["month"],categories=month_order,ordered=True)


        # cogs time to decimal
        def time_to_hour_min_decimal(t):
            try:
                h, m, s = str(t).split(":")
                return float(h) + float(m)/100
            except:
                return None

        filtered_data["cogs_usd_decimal"] = filtered_data["cogs_usd_orderitem"].apply(time_to_hour_min_decimal)

        
        # Filter options
        Year= filtered_data["year"].dropna().sort_values().unique()
        Month =filtered_data["month"].dropna().sort_values().unique()
        Products = filtered_data["product_name"].dropna().unique()
        Sources = filtered_data["utm_source"].dropna().unique()
        Campaigns = filtered_data["utm_campaign"].dropna().unique()
        Devices = filtered_data["device_type"].dropna().unique()
        
        
        st.sidebar.title("🔍 Filters")
        selected_years = st.sidebar.multiselect("Year", Year)

        selected_months = st.sidebar.multiselect("Month", Month)
        
        selected_products = st.sidebar.multiselect("Product", Products)
        
        selected_sources = st.sidebar.multiselect("UTM Source", Sources)
        
        selected_campaigns =st.sidebar.multiselect("UTM Campaign",Campaigns)
        
        selected_devices = st.sidebar.multiselect("Device Type", Devices)


        # Apply filters
        final_df = filtered_data.copy()
        if selected_years:
            final_df = final_df[final_df["year"].isin(selected_years)]
        if selected_months:
            final_df = final_df[final_df["month"].isin(selected_months)]
        if selected_products:
            final_df = final_df[final_df["product_name"].isin(selected_products)]
        if selected_sources:
            final_df = final_df[final_df["utm_source"].isin(selected_sources)]
        if selected_campaigns:
            final_df = final_df[final_df["utm_campaign"].isin(selected_campaigns)]
        if selected_devices:
            final_df = final_df[final_df["device_type"].isin(selected_devices)]

    
        
        st.subheader("📌 Key Metrics")
        # ✅ KPI Calculations
        Total_revenue = final_df['price_usd_orderitem'].sum()/1000000
        Net_revenue = (final_df['price_usd_orderitem'].sum()- final_df['refund_amount_usd'].sum())/1000000
        Total_cost= final_df['cogs_usd_decimal'].sum()/1000
        Net_cost=final_df[final_df['order_item_refund_id'].isna()]['cogs_usd_decimal'].sum()/1000
        Profit = ((final_df['price_usd_orderitem'].sum() - final_df['refund_amount_usd'].sum()) - final_df[final_df['order_item_refund_id'].isna()]['cogs_usd_decimal'].sum()) / 1000000
        Profit_percent = ((final_df['price_usd_orderitem'].sum()- final_df['refund_amount_usd'].sum()- final_df[final_df['order_item_refund_id'].isna()]['cogs_usd_decimal'].sum())/ final_df[final_df['order_item_refund_id'].isna()]['cogs_usd_decimal'].sum()) * 100
        Total_orders = final_df['order_id'].nunique()
        Total_refunds_items = final_df['order_id_refunds'].count()
        Refund_Amount= (final_df['price_usd_orderitem'].sum()/1000000) -((final_df['price_usd_orderitem'].sum()- final_df['refund_amount_usd'].sum())/1000000)
        Refund_Amount_rate =(((final_df['price_usd_orderitem'].sum()) -((final_df['price_usd_orderitem'].sum() - final_df['refund_amount_usd'].sum()))) /
                                            (final_df['price_usd_orderitem'].sum() - final_df['refund_amount_usd'].sum())*100)
        Total_buyers=final_df['user_id'].nunique()
        Total_users=w_sessions['user_id'].nunique()
        Total_Quantity =final_df['items_purchased'].count()
        Total_sessions = w_sessions['website_session_id'].nunique()
        Repeat_sessions = w_sessions['is_repeat_session'].sum()
        conversion_rate = (Total_orders / Total_sessions * 100) 
        repeat_rate = ((final_df['is_repeat_session'].sum()) / (w_sessions['website_session_id'].nunique())* 100)
        avg_revenue_per_session = (final_df['price_usd_orderitem'].sum()) / (w_sessions['website_session_id'].nunique()) 
        avg_order_value = (final_df['price_usd_orderitem'].sum()) / (final_df['order_id'].nunique()) 
        session_page_counts = website_pageviews[['website_session_id' ,'website_pageview_id']].groupby('website_session_id').count().reset_index()
        bounce_sessions = session_page_counts[session_page_counts['website_pageview_id'] == 1]
        bounce_rate = len(bounce_sessions) / len(session_page_counts) * 100
        avg_items_per_order=(final_df['items_purchased'].count())/(final_df['order_id'].nunique())
        avg_session_per_user=( w_sessions['website_session_id'].nunique())/(w_sessions['user_id'].nunique())
        Total_products=final_df['product_name'].nunique()
        Average_revenue_per_buyer=(final_df['price_usd_orderitem'].sum()- final_df['refund_amount_usd'].sum())/(final_df['user_id'].nunique())
        Average_profit_per_buyer=(((final_df['price_usd_orderitem'].sum() - final_df['refund_amount_usd'].sum()) - final_df[final_df['order_item_refund_id'].isna()]['cogs_usd_decimal'].sum()))/(final_df['user_id'].nunique())


        col6, col7, col8 = st.columns(3)
        col6.metric("💰 Total Sales", f"${Total_revenue:,.2f} M")
        col7.metric("💰 Net Revenue", f"${Net_revenue:,.2f} M")
        col8.metric("💰 Total Cost", f"${Total_cost:,.2f} K")

        col9, col10, col11 = st.columns(3)
        col9.metric("💰 Net Cost", f"${Net_cost:,.2f} K")
        col10.metric("🎯 Profit", f"${Profit:,.2f} M")
        col11.metric("🎯 Profit %", f"{Profit_percent:,.2f}")

        col12, col13, col14 = st.columns(3)
        col12.metric("📦 Total Orders", f"{Total_orders}")
        col13.metric("🔁 Total Refund Items", f"{Total_refunds_items}")
        col14.metric("💰 Total Refund Amount", f"${Refund_Amount:,.2f} M") 
        
        col15, col16, col17 = st.columns(3)
        col15.metric("🛒 Total Quantity", f"{Total_Quantity}")
        col16.metric("👥 Total Buyers", f"{Total_buyers}")
        col17.metric("💸 Average order value", f"${avg_order_value:,.2f}")

        col18, col19, col20 = st.columns(3)
        col18.metric("🖥️Total Sessions", f"{Total_sessions}")
        col19.metric("🔄 Repeat Sessions", f"{Repeat_sessions}")
        col20.metric("💼 Average Revenue per Session", f"${avg_revenue_per_session:,.2f}")

        col21, col22, col23 = st.columns(3)
        col21.metric("🧺 Average Items per Order", f"{avg_items_per_order:,.2f}")
        col22.metric("👥 Total Users", f"{Total_users}")
        col23.metric("💹 Refund rate", f"{Refund_Amount_rate:,.2f} %")

        col24, col25, col26 = st.columns(3)
        col24.metric("🪐 Total Products", f"{Total_products}")
        col25.metric("🖥️ Average Sessions per User", f"{avg_session_per_user:,.2f}")
        col26.metric("🪐 Average Revenue per buyer", f"${Average_revenue_per_buyer:,.2f}")
        


        col27, col28, col29 = st.columns(3)
        col27.metric("🪐 Average Profit per buyer", f"${Average_profit_per_buyer:,.2f}")
        col28.metric("➡️ Conversion rate", f"{conversion_rate:,.2f} %")
        col29.metric("🟦 Bounce rate", f"{bounce_rate:,.2f} %")

        
    
    elif selection == "Website Performance Analysis":
        st.title("📊 Website Performance Analysis")

        # Start with order_items
        filtered_data_2 = website_pageviews.copy()

        # merge with w_sessions
        filtered_data_2 = filtered_data_2.merge(w_sessions, how="left", on="website_session_id",suffixes=("_webpage", "_website"))

        # Extract Year for filtering
        filtered_data_2["year"] = filtered_data_2["created_at_webpage"].dt.year

        # Extract Month for filtering
        filtered_data_2["month"] = filtered_data_2["created_at_webpage"].dt.month_name()
        month_order = ["January", "February", "March", "April", "May", "June","July", "August", "September", "October", "November", "December"]
        filtered_data_2["month"] = pd.Categorical(filtered_data_2["month"],categories=month_order,ordered=True)


        # Filter options
        Years = filtered_data_2["year"].dropna().sort_values().unique()
        Month =filtered_data_2["month"].dropna().sort_values().unique()
        Sources = filtered_data_2["utm_source"].dropna().unique()
        Campaigns = filtered_data_2["utm_campaign"].dropna().unique()
        Devices = filtered_data_2["device_type"].dropna().unique()
        
        
        
        st.sidebar.title("🔍 Filters")
        selected_years = st.sidebar.multiselect("Year", Years)
        
        selected_months = st.sidebar.multiselect("Month", Month)
        
        selected_sources = st.sidebar.multiselect("UTM Source", Sources)
        
        selected_campaigns =st.sidebar.multiselect("UTM Campaign",Campaigns)
        
        selected_devices = st.sidebar.multiselect("Device Type", Devices)


        # Apply filters
        final_df_2 = filtered_data_2.copy()
        if selected_years:
            final_df_2 = final_df_2[final_df_2["year"].isin(selected_years)]
        if selected_months:
            final_df_2 = final_df_2[final_df_2["month"].isin(selected_months)]
        if selected_sources:
            final_df_2 = final_df_2[final_df_2["utm_source"].isin(selected_sources)]
        if selected_campaigns:
            final_df_2 = final_df_2[final_df_2["utm_campaign"].isin(selected_campaigns)]
        if selected_devices:
            final_df_2= final_df_2[final_df_2["device_type"].isin(selected_devices)]


        

        st.markdown("### 🏠 Top Entry Pages")
        entry_pages = final_df_2.groupby('website_session_id').first().reset_index()
        top_entry_pages = entry_pages['pageview_url'].value_counts().reset_index()
        top_entry_pages.columns=['pageview_url','Total_views']
 
        st.dataframe(top_entry_pages)

        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=top_entry_pages,y='pageview_url',x='Total_views',color='skyblue',ax=ax)

        # Add count labels
        for container in ax.containers:
            ax.bar_label(container, fmt="%.0f", fontsize=9, padding=3)

        ax.set_title("Top Entry Pages by Count")
        ax.set_xlabel("Entry Count")
        ax.set_ylabel("Pageview URL")
        plt.tight_layout()

        # Show in Streamlit
        st.pyplot(fig)




        st.markdown("---")
        st.markdown("### ⭐ Top 5 Visited Pages")

        top_pages = (final_df_2["pageview_url"].value_counts().reset_index())
        top_pages.columns=['pageview_url','Total_views']
        top_n = 5
        top_pages = top_pages.head(top_n)
        # Show the table in Streamlit
        st.dataframe(top_pages)

        # Create the bar chart
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=top_pages,x="pageview_url",y="Total_views",color="skyblue",ax=ax)

        for container in ax.containers:
            ax.bar_label(container, fmt="%.0f", fontsize=9, padding=3)

        ax.set_title("Top 5 Visited Pages")
        ax.set_xlabel("Page URL")
        ax.set_ylabel("Page views")
        plt.tight_layout()

        # Display the chart in Streamlit
        st.pyplot(fig)



        st.markdown("---")
        st.markdown("### 🎯 Landing Page Conversion Rates")

        landing_pages = (final_df_2.sort_values(by=['website_session_id', 'created_at_webpage']) .groupby('website_session_id').first()                                               
                        .reset_index()[['website_session_id', 'pageview_url']] .rename(columns={'pageview_url': 'landing_page'}))

        landing_pages['converted'] = landing_pages['website_session_id'].isin(orders['website_session_id'])

        landing_page_cvr = (landing_pages.groupby('landing_page').agg(total_sessions=('website_session_id', 'nunique'),conversions=('converted', 'sum')).reset_index())
        
        landing_page_cvr['conversion_rate'] = (landing_page_cvr['conversions'] / landing_page_cvr['total_sessions'])

        landing_page_cvr['conversion_rate'] = (landing_page_cvr['conversion_rate'] * 100).round(2)

        # Sort by conversion rate descending
        landing_page_cvr_sorted = landing_page_cvr.sort_values(by="conversion_rate",ascending=False)

        st.dataframe(landing_page_cvr_sorted)

        fig, ax = plt.subplots(figsize=(10, 8))
        sns.barplot(data=landing_page_cvr_sorted,x="conversion_rate",y="landing_page",color="skyblue",ax=ax)

        ax.set_title("Landing Page Conversion Rate (%)")
        ax.set_xlabel("Conversion Rate (%)")
        ax.set_ylabel("Landing Page URL")

        # Add labels
        for container in ax.containers:
            ax.bar_label(container, fmt="%.1f%%", padding=3, fontsize=9)

        plt.tight_layout()
        st.pyplot(fig)



        st.markdown("---")
        st.markdown("### 📊 Page Depth Analysis")
        

        # STEP 1: Count pageviews per session
        page_depth = final_df_2.groupby('website_session_id').size().reset_index(name='pageview_count')

        # STEP 2: View distribution of page depth
        depth_distribution = (page_depth['pageview_count'].value_counts().sort_index().reset_index())
        depth_distribution.columns=['Number of Pageviews','Session Count']

        st.dataframe(depth_distribution)

        # PAGE DEPTH VISUALIZATION
        fig, ax = plt.subplots(figsize=(10, 6))

        # Show plot in Streamlit
        sns.barplot(data=depth_distribution,x='Number of Pageviews',y='Session Count',color='skyblue',ax=ax)

        # Add labels
        for i, row in depth_distribution.iterrows():
            ax.text(i,row["Session Count"],str(int(row["Session Count"])),ha='center',va='bottom',fontsize=9)

  
        # Titles and labels
        ax.set_title('Page Depth Distribution', fontsize=16)
        ax.set_xlabel('Number of Pageviews per Session', fontsize=12)
        ax.set_ylabel('Number of Sessions', fontsize=12)
        plt.tight_layout()
        st.pyplot(fig)




        st.markdown("---")
        st.markdown("### 🕒 Session Duration Summary")

        # Group by session and calculate start and end times
        session_times = (final_df_2.groupby('website_session_id')['created_at_webpage'].agg(session_start='min', session_end='max').reset_index())

        # Calculate duration
        session_times['session_duration_sec'] = ((session_times['session_end'] - session_times['session_start']).dt.total_seconds())
        session_times['session_duration_min'] = (session_times['session_duration_sec'] / 60).round(2)

        session_times['duration_rounded'] = session_times['session_duration_min'].round()

        duration_counts = (session_times['duration_rounded'].value_counts().sort_index().reset_index())
        duration_counts.columns = ['Session Duration (min)', 'Session Count']

        # Display table in Streamlit
        st.dataframe(duration_counts)

        # Plot bar chart
        fig, ax = plt.subplots(figsize=(10,6))

        sns.barplot(data=duration_counts,x='Session Duration (min)',y='Session Count',color='lightgreen',ax=ax)

        # Add count labels on top of each bar
        for i, row in duration_counts.iterrows():
            ax.text(i,row['Session Count'],str(int(row['Session Count'])),ha='center',rotation=45,va='bottom',fontsize=9)

        # Titles and labels
        ax.set_title('Session Duration Distribution', fontsize=16)
        ax.set_xlabel('Session Duration (minutes)', fontsize=12)
        ax.set_xticklabels(duration_counts['Session Duration (min)'].astype(str))
        ax.set_ylabel('Number of Sessions', fontsize=12)
        plt.tight_layout()

        # Show in Streamlit
        st.pyplot(fig)



        st.markdown("---")
        st.markdown("### 🎯 Website Funnel Analysis")


        final_df_2['pageview_url'] = final_df_2['pageview_url'].str.strip().str.lower()

        # Create binary flags for each funnel step per session
        funnel_flags = website_pageviews.pivot_table(index='website_session_id',columns='pageview_url',values='website_pageview_id',
                                                    aggfunc='count',fill_value=0).reset_index()

        # Rename known funnel steps (customize URLs as needed)
        funnel_flags['visited_landing'] = ((funnel_flags.get('/home', 0) > 0) |(funnel_flags.get('/lander-1', 0) > 0) |
                                           (funnel_flags.get('/lander-2', 0) > 0) |(funnel_flags.get('/lander-3', 0) > 0) |
                                           (funnel_flags.get('/lander-4', 0) > 0) |(funnel_flags.get('/lander-5', 0) > 0))

        funnel_flags['visited_product'] = ((funnel_flags.get('/products', 0) > 0) |
                                           (funnel_flags.get('/the-original-mr-fuzzy', 0) > 0) |
                                           (funnel_flags.get('/the-forever-love-bear', 0) > 0) |
                                           (funnel_flags.get('/the-birthday-sugar-panda', 0) > 0) |
                                           (funnel_flags.get('/the-hudson-river-mini-bear', 0) > 0))

        funnel_flags['visited_cart'] = funnel_flags.get('/cart', 0) > 0

        funnel_flags['visited_billing'] = ((funnel_flags.get('/billing', 0) > 0) |(funnel_flags.get('/billing-2', 0) > 0))

        funnel_flags['visited_shipping'] = funnel_flags.get('/shipping', 0) > 0

        funnel_flags['visited_order'] = funnel_flags.get('/thank-you-for-your-order', 0) > 0

        # Everyone in this table is considered as having started a session (landing)
        funnel_flags['visited_landing'] = True

        #Count sessions at each step
        funnel_counts = {
                        'Landing': funnel_flags['visited_landing'].sum(),
                        'Product': funnel_flags['visited_product'].sum(),
                        'Cart': funnel_flags['visited_cart'].sum(),
                        'Shipping': funnel_flags['visited_shipping'].sum(),
                        'Billing': funnel_flags['visited_billing'].sum(),
                        'Order': funnel_flags['visited_order'].sum()
                        }

        #Create funnel DataFrame with drop-off and conversion rate
        funnel_df = pd.DataFrame(list(funnel_counts.items()), columns=['Step', 'Sessions'])
        funnel_df['Dropoff'] = funnel_df['Sessions'].shift(1) - funnel_df['Sessions']
        funnel_df['Conversion_Rate (%)'] = (funnel_df['Sessions'] / funnel_df['Sessions'].shift(1) * 100).round(2)
        funnel_df.fillna({'Dropoff': 0, 'Conversion_Rate (%)': 100}, inplace=True)
        funnel_df['Dropoff_Rate (%)'] = (funnel_df['Dropoff'] / funnel_df['Sessions'].shift(1) * 100).round(2)
        funnel_df['Dropoff_Rate (%)'] = funnel_df['Dropoff_Rate (%)'].fillna(0)

        st.dataframe(funnel_df)


        fig, ax = plt.subplots(figsize=(10, 6))
        colors = sns.color_palette("Oranges", n_colors=len(funnel_df))
        bars = ax.bar(funnel_df['Step'], funnel_df['Sessions'], color=colors)

        # Annotate sessions and dropoff % on each bar
        for i, (session_count, dropoff_pct) in enumerate(zip(funnel_df['Sessions'], funnel_df['Dropoff_Rate (%)'])):
            # Session count above
            ax.text(i, session_count + (0.01 * session_count), f'{int(session_count)}',ha='center', fontsize=10, fontweight='bold')
            # Dropoff % below (from step 2 onward)
            if i > 0:
                ax.text(i, session_count / 2, f'-{dropoff_pct}%',ha='center', va='center', fontsize=9, color='black', fontweight='bold')

        ax.set_title('Website Funnel - Sessions per Step', fontsize=14, fontweight='bold')
        ax.set_xlabel('Funnel Step', fontsize=12)
        ax.set_ylabel('Sessions/ Droffoff %', fontsize=12)
        plt.tight_layout()

        st.pyplot(fig)





    elif selection == "Traffic Source Analysis":
        st.title("📊 Traffic Source Analysis")


        # Extract Year for filtering
        w_sessions['year'] = w_sessions["created_at"].dt.year

         # Extract Month for filtering
        w_sessions["month"] = w_sessions["created_at"].dt.month_name()
        month_order = ["January", "February", "March", "April", "May", "June","July", "August", "September", "October", "November", "December"]
        w_sessions["month"] = pd.Categorical(w_sessions["month"],categories=month_order,ordered=True)

       

        # Filter options
        Years = w_sessions["year"].dropna().sort_values().unique()
        Month =w_sessions["month"].dropna().sort_values().unique()
        Sources = w_sessions["utm_source"].dropna().unique()
        Campaigns = w_sessions["utm_campaign"].dropna().unique()
        Devices = w_sessions["device_type"].dropna().unique()
        
        

        st.sidebar.title("🔍 Filters")
        selected_years = st.sidebar.multiselect("Year", Years)
        
        selected_months = st.sidebar.multiselect("Month", Month)
        
        selected_sources = st.sidebar.multiselect("UTM Source", Sources)
        
        selected_campaigns =st.sidebar.multiselect("UTM Campaign",Campaigns)
        
        selected_devices = st.sidebar.multiselect("Device Type", Devices)


        # Apply filters
        final_df_3 = w_sessions.copy()
        if selected_years:
            final_df_3 = final_df_3[final_df_3["year"].isin(selected_years)]
        if selected_months:
            final_df_3= final_df_3[final_df_3["product_name"].isin(selected_months)]
        if selected_sources:
            final_df_3 = final_df_3[final_df_3["utm_source"].isin(selected_sources)]
        if selected_campaigns:
            final_df_3= final_df_3[final_df_3["utm_campaign"].isin(selected_campaigns)]
        if selected_devices:
            final_df_3= final_df_3[final_df_3["device_type"].isin(selected_devices)]


        

        st.markdown("### 🟢 Session Count by Source")
        # Compute session counts by source
        source_breakdown = (w_sessions.groupby("utm_source")["website_session_id"].count().reset_index().rename(columns={"website_session_id": "session_count"}))

        st.dataframe(source_breakdown)

        # Sort for clarity (optional)
        source_breakdown = source_breakdown.sort_values('session_count', ascending=False)

        # Create bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=source_breakdown,x='utm_source',y='session_count',color='skyblue',ax=ax)

        # Add labels
        for container in ax.containers:
            ax.bar_label(container, fmt="%.0f", fontsize=9, padding=3)

        ax.set_title("Session Count by Source")
        ax.set_xlabel("UTM Source")
        ax.set_ylabel("Sessions")
        plt.tight_layout()

        # Show in Streamlit
        st.pyplot(fig)



        st.markdown("---")
        st.markdown("### 🚦 Sessions by Traffic Source and Campaign")

        # Step 1: Group sessions by source and campaign
        source_campaign = (w_sessions.groupby(['utm_source', 'utm_campaign']).agg(sessions=('website_session_id', 'count')).reset_index())
        st.dataframe(source_campaign)

        # Step 2: Create bar chart
        fig, ax = plt.subplots(figsize=(12, 8))

        # We'll sort to make bars easier to read
        source_campaign_sorted = source_campaign.sort_values('sessions', ascending=False)

        sns.barplot(data=source_campaign_sorted,x='sessions',y='utm_source',hue='utm_campaign',palette='tab10',dodge=True,ax=ax)

        # Add data labels on each bar
        for container in ax.containers:
            ax.bar_label(container, fmt='%.0f', fontsize=9, padding=3)

        ax.set_title('Sessions by Source and Campaign')
        ax.set_xlabel('Sessions')
        ax.set_ylabel('UTM Source')
        ax.legend(title='UTM Campaign', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()

        # Show chart in Streamlit
        st.pyplot(fig)



        st.markdown("---")
        st.markdown("### 📊 Sessions by Weekday")


        # Step 1: Convert to datetime if not already
        w_sessions["created_at"] = pd.to_datetime(w_sessions["created_at"])

        # Step 2: Extract weekday names
        w_sessions["weekday"] = w_sessions["created_at"].dt.day_name()

        # Step 3: Chronological weekday order
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        w_sessions["weekday"] = pd.Categorical(w_sessions["weekday"], categories=weekday_order, ordered=True)

        # Step 4: Aggregate session counts by weekday
        weekday_sessions = (w_sessions.groupby("weekday").agg(sessions=("website_session_id", "count")).reset_index())

        # Show DataFrame
        st.dataframe(weekday_sessions)

        # Step 5: Plot bar chart with labels
        fig, ax = plt.subplots(figsize=(12, 8))
        sns.barplot(data=weekday_sessions,x="weekday",y="sessions",color="skyblue",ax=ax)

        # Add labels on top of bars
        for container in ax.containers:
            ax.bar_label(container, fmt="%.0f", fontsize=9, padding=3)

        ax.set_title("Sessions by Weekday")
        ax.set_xlabel("Weekday")
        ax.set_ylabel("Sessions")
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Show chart
        st.pyplot(fig)



        st.markdown("---")
        st.markdown("### 💻 Source Breakdown by Device")
        
        source_device = (w_sessions.groupby(['utm_source', 'device_type']).agg(session_count=('website_session_id', 'count')).reset_index())
        st.dataframe(source_device)

        # Sort by session count for better readability
        source_device_sorted = source_device.sort_values('session_count', ascending=False)

        # Create the bar chart
        fig, ax = plt.subplots(figsize=(12, 5))
        sns.barplot(data=source_device_sorted,x='session_count',y='utm_source',hue='device_type',dodge=True,palette="Set2",ax=ax)

        # Add data labels on each bar
        for container in ax.containers:
            ax.bar_label(container, fmt="%.0f", fontsize=9, padding=3)

        ax.set_title("Sessions by Source and Device Type")
        ax.set_xlabel("Sessions")
        ax.set_ylabel("UTM Source")
        ax.legend(title="Device Type", bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()

        st.pyplot(fig)



        st.markdown("---")
        st.markdown("### 🚪 Bounce Rate by UTM Source")
        # STEP 1: Count pageviews per session
        pageview_counts = (website_pageviews.groupby('website_session_id').size().reset_index(name='pageview_count'))

        # STEP 2: Add bounce flag (only 1 pageview)
        pageview_counts['is_bounce'] = pageview_counts['pageview_count'] == 1

        # STEP 3: Merge with session data to get utm_source
        session_data = w_sessions.merge(pageview_counts[['website_session_id', 'is_bounce']],on='website_session_id',how='left')

        # Fill NaN (sessions with no pageviews) as not bounced
        session_data['is_bounce'] = session_data['is_bounce'].fillna(False)

        # STEP 4: Group by utm_source and calculate bounce rate
        bounce_by_source = (session_data.groupby('utm_source').agg(Total_sessions=('website_session_id', 'nunique'),Bounce_sessions=('is_bounce', 'sum')).reset_index())

        bounce_by_source['bounce_rate (%)'] = (bounce_by_source['Bounce_sessions'] / bounce_by_source['Total_sessions'] * 100).round(2)

        # Sort by bounce rate
        bounce_by_source = bounce_by_source.sort_values(by='bounce_rate (%)', ascending=False)


        st.dataframe(bounce_by_source)

        # Bar Chart
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=bounce_by_source,x='utm_source',y='bounce_rate (%)',color='skyblue',ax=ax)

        # Add percentage labels on bars
        for container in ax.containers:
            ax.bar_label(container, labels=[f"{v.get_height():.1f}%" for v in container], fontsize=9, padding=3)

        ax.set_title("Bounce Rate (%) by UTM Source")
        ax.set_xlabel("UTM Source")
        ax.set_ylabel("Bounce Rate (%)")
        plt.tight_layout()

        # Show chart in Streamlit
        st.pyplot(fig)




        st.markdown("---")
        st.markdown("### 💰 Monetization Efficiency by UTM Source")
        # STEP 1: Merge orders with sessions to attribute revenue to sources
        orders_with_source = orders.merge(w_sessions[['website_session_id', 'utm_source']],on='website_session_id',how='left')

        # STEP 2: Total revenue per source
        revenue_per_source = (orders_with_source.groupby('utm_source').agg(total_revenue=('price_usd', 'sum')).reset_index())

        # STEP 3: Total sessions per source
        session_counts = (w_sessions.groupby('utm_source').agg(total_sessions=('website_session_id', 'nunique')).reset_index())

        # STEP 4: Merge revenue and sessions, compute revenue per session
        monetization_efficiency = revenue_per_source.merge(session_counts, on='utm_source', how='outer')

        monetization_efficiency['revenue_per_session'] = (monetization_efficiency['total_revenue'] / monetization_efficiency['total_sessions']).round(2)

        # Handle NaNs
        monetization_efficiency.fillna({'total_revenue': 0, 'revenue_per_session': 0, 'total_sessions': 0},inplace=True)

        # Sort for clarity
        monetization_efficiency = monetization_efficiency.sort_values(by='revenue_per_session', ascending=False)

        st.dataframe(monetization_efficiency)

        # Bar Chart
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=monetization_efficiency,x='utm_source',y='revenue_per_session',color='skyblue',ax=ax)

        # Add labels on top of bars
        for container in ax.containers:
            ax.bar_label(container, labels=[f"${v.get_height():.2f}" for v in container], fontsize=9, padding=3)

        ax.set_title("Revenue per Session by UTM Source")
        ax.set_xlabel("UTM Source")
        ax.set_ylabel("Revenue per Session (USD)")
        plt.tight_layout()

        # Show chart in Streamlit
        st.pyplot(fig)













    elif selection == "Channel Portfolio Management":
        st.header("📊 Channel Portfolio Management")
        # Start with order_items
        filtered_data = order_items.copy()

        # merge with orders
        filtered_data = filtered_data.merge(orders, how="left", on="order_id",suffixes=("_orderitem", "_order"))

        # merge with products
        filtered_data = filtered_data.merge(products, how="left", left_on="product_id",right_on="product_id",suffixes=("","_products"))

        # merge with refund
        filtered_data = filtered_data.merge(order_item_refunds, how="left", on="order_item_id",suffixes=("","_refunds"))

        # merge with w_sessions
        filtered_data = filtered_data.merge(w_sessions,how="left",left_on="website_session_id",right_on="website_session_id",suffixes=("","_sessions"))

        # Extract Year for filtering
        filtered_data["year"] = filtered_data["created_at_orderitem"].dt.year

        # cogs time to decimal
        def time_to_hour_min_decimal(t):
            try:
                h, m, s = str(t).split(":")
                return float(h) + float(m)/100
            except:
                return None

        filtered_data["cogs_usd_decimal"] = filtered_data["cogs_usd_orderitem"].apply(time_to_hour_min_decimal)




        # Filter options
        Years = filtered_data["year"].dropna().sort_values().unique()
        Products = filtered_data["product_name"].dropna().unique()
        Sources = filtered_data["utm_source"].dropna().unique() 
        Campaigns = filtered_data["utm_campaign"].dropna().unique()
        Devices = filtered_data["device_type"].dropna().unique()
        
        

        
        st.sidebar.title("🔍 Filters")
        selected_years = st.sidebar.multiselect("Year", Years)
        
        selected_products = st.sidebar.multiselect("Product", Products)
        
        selected_sources = st.sidebar.multiselect("UTM Source", Sources)
        
        selected_campaigns =st.sidebar.multiselect("UTM Campaign",Campaigns)
        
        selected_devices = st.sidebar.multiselect("Device Type", Devices)


        # Apply filters
        final_df = filtered_data.copy()
        if selected_years:
            final_df = final_df[final_df["year"].isin(selected_years)]
        if selected_products:
            final_df = final_df[final_df["product_name"].isin(selected_products)]
        if selected_sources:
            final_df = final_df[final_df["utm_source"].isin(selected_sources)] 
        if selected_campaigns:
            final_df = final_df[final_df["utm_campaign"].isin(selected_campaigns)]
        if selected_devices:
            final_df = final_df[final_df["device_type"].isin(selected_devices)]



        if not filtered_data.empty:
            st.markdown("### 💸 Revenue by UTM Source")
            revenue_chart = final_df.groupby('utm_source')['price_usd_orderitem'].sum().div(1000000).reset_index().sort_values('price_usd_orderitem', ascending=False)
            revenue_chart.columns=['UTM_Source','Total_sales_amount']
            st.dataframe(revenue_chart)
            #Plot
            fig1, ax1 = plt.subplots(figsize=(10, 5))
            bars1 = sns.barplot(data=revenue_chart, x='UTM_Source', y='Total_sales_amount', color='skyblue', ax=ax1)

            for bar in bars1.patches:
                height = bar.get_height()
                ax1.annotate(f"{height:,.2f}", xy=(bar.get_x() + bar.get_width() / 2, height),xytext=(0, 5), textcoords='offset points',ha='center', va='bottom', fontsize=9, color='black')
            ax1.set_title("Revenue by UTM Source", fontsize=14, weight='bold')
            ax1.set_xlabel("UTM Source", fontsize=11)
            ax1.set_ylabel("Revenue(in Millions USD))", fontsize=11)
            ax1.tick_params(axis='x', rotation=30)
            ax1.grid(axis='y', linestyle='--', alpha=0.3)
            st.pyplot(fig1)



            st.markdown("---")
            st.markdown("### 🔁 Repeat vs New Sessions by UTM Source")
            w_sessions['session_type'] = w_sessions['is_repeat_session'].apply(lambda x: 'Repeat' if x == 1 else 'New')
            session_counts = w_sessions.groupby(['utm_source', 'session_type'])['website_session_id'].count().reset_index()
            session_counts.columns=['UTM_source','Session_type','Total_website_sessions']
            st.dataframe(session_counts)

            session_counts = session_counts.sort_values(by='Total_website_sessions',ascending=True)
            
            fig, ax = plt.subplots(figsize=(10,6))
            sns.barplot(data=session_counts,x='UTM_source',y='Total_website_sessions',hue='Session_type',ax=ax)

            ax.set_title('Revenue by UTM Source')
            ax.set_xlabel('UTM Source')
            ax.set_ylabel('Session Count')
            ax.legend(title='Session_type', loc='upper left')
            plt.xticks(rotation=0)

            for container in ax.containers:
                ax.bar_label(container, fmt='%.2f', label_type='edge', padding=3, fontsize=8)

            fig.tight_layout()
            st.pyplot(fig)




        st.markdown("---")
        st.markdown("### 📈 Conversion Rate by UTM Campaign")
        # Mark converted sessions
        converted_sessions = final_df["website_session_id"].unique()
        w_sessions["converted"] = w_sessions["website_session_id"].isin(converted_sessions).astype(int)

        # Group by utm_campaign and compute CVR
        campaign_analysis = (w_sessions.groupby("utm_campaign").agg(Total_sessions=("website_session_id", "count"),Conversions=("converted", "sum")).assign(CVR_percentage=lambda x: round((x["Conversions"] / x["Total_sessions"]) * 100, 2)).sort_values("CVR_percentage", ascending=False).reset_index())

        # Display DataFrame in Streamlit
        st.dataframe(campaign_analysis)

        # Plotting
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=campaign_analysis,x='utm_campaign',y='CVR_percentage',color='skyblue',legend=False,ax=ax)

        # Add chart labels
        for container in ax.containers:
            labels = [f'{v.get_height():.1f}%' for v in container]
            ax.bar_label(container, labels=labels, label_type='edge', padding=3, fontsize=9)

        ax.set_title('Conversion Rate by UTM Campaign')
        ax.set_xlabel('UTM Campaign')
        ax.set_ylabel('CVR (%)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)



        st.markdown("---")
        st.markdown("### 💵 Brand vs Non Brand Efficiency")

        # Tag sessions as brand vs. non-brand
        w_sessions["campaign_type"] = w_sessions["utm_campaign"].apply(lambda x: "Brand" if "brand" in x.lower() else "Non-Brand")

        # Mark converted sessions
        converted_sessions = final_df["website_session_id"].unique()
        w_sessions["converted"] = w_sessions["website_session_id"].isin(converted_sessions).astype(int)

        # Merge revenue from orders to w_sessions
        revenue_map = final_df.groupby("website_session_id")["price_usd_orderitem"].sum().div(1000000).to_dict()
        w_sessions["revenue"] = w_sessions["website_session_id"].map(revenue_map).fillna(0)

        # Group by campaign type
        efficiency_analysis = (w_sessions.groupby("campaign_type").agg(total_sessions=("website_session_id", "count"),conversions=("converted", "sum"),total_revenue=("revenue", "sum"))
       .assign(CVR_percentage=lambda x: round((x["conversions"] / x["total_sessions"]) * 100, 2)).reset_index())

        # Display DataFrame
        st.dataframe(efficiency_analysis)

        # Plotting
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=efficiency_analysis,x='campaign_type',y='total_revenue',color='skyblue',ax=ax,legend=False)

        # Add formatted data labels
        for container in ax.containers:
            labels = [f'{bar.get_height():,.2f}' for bar in container]
            ax.bar_label(container, labels=labels, label_type='edge', padding=3, fontsize=9)

        ax.set_title('Revenue by Campaign Type')
        ax.set_xlabel('Campaign Type')
        ax.set_ylabel('Total Revenue ( in Millions USD)')

        plt.tight_layout()

        # Show plot in Streamlit
        st.pyplot(fig)




        st.markdown("---")
        st.markdown("### 💡 Pilot Campaugn Metrics")

        # Step 1: Filter 'Pilot' campaign sessions (case-insensitive)
        pilot_sessions = w_sessions[w_sessions["utm_campaign"].str.lower() == "pilot"].copy()

        # Step 2: Proceed only if data exists
        if not pilot_sessions.empty:
        # Mark conversions
            converted_sessions = final_df["website_session_id"].unique()
            pilot_sessions["converted"] = pilot_sessions["website_session_id"].isin(converted_sessions).astype(int)

        # Map revenue
            revenue_map = final_df.groupby("website_session_id")["price_usd_orderitem"].sum().to_dict()
            pilot_sessions["revenue"] = pilot_sessions["website_session_id"].map(revenue_map).fillna(0)

            # Aggregate metrics
            total_sessions = len(pilot_sessions)
            conversions = pilot_sessions["converted"].sum()
            total_revenue = pilot_sessions["revenue"].sum()
            cvr = round((conversions / total_sessions) * 100, 2)

        else:
        # Default if no sessions
            total_sessions = 0
            conversions = 0
            total_revenue = 0
            cvr = 0

        # Step 3: Create summarized DataFrame
        pilot_roi = pd.DataFrame([{"utm_campaign": "Pilot",
                                    "total_sessions": total_sessions,
                                    "conversions": conversions,
                                    "total_revenue": total_revenue,
                                    "CVR_percentage": cvr}])

       
        st.dataframe(pilot_roi)

        # Step 5: Prepare for Plotting
        metrics = ['Total Sessions', 'Conversions', 'Total Revenue']
        values = [total_sessions, conversions, total_revenue]
        labels = [f'{int(total_sessions)}', f'{int(conversions)}', f'{total_revenue:,.0f}']

        # Step 6: Plot in Streamlit
        fig, ax = plt.subplots(figsize=(7, 4))
        bars = ax.bar(metrics, values, color=['#4C72B0', '#55A868', '#C44E52'])

        # Add data labels
        for bar, label in zip(bars, labels):
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, yval, label,ha='center', va='bottom', fontsize=10)

        ax.set_title("Pilot Campaign Metrics")
        ax.set_ylabel("Counts / Revenue (USD)")
        plt.tight_layout()

        # Show chart in Streamlit
        st.pyplot(fig)






    elif selection == "Business Patterns and Seasonality":
        st.header("📊 Business Patterns and Seasonality")
        # Start with order_items
        filtered_data = order_items.copy()

        # merge with orders
        filtered_data = filtered_data.merge(orders, how="left", on="order_id",suffixes=("_orderitem", "_order"))

        # merge with products
        filtered_data = filtered_data.merge(products, how="left", left_on="product_id",right_on="product_id",suffixes=("","_products"))

        # merge with refund
        filtered_data = filtered_data.merge(order_item_refunds, how="left", on="order_item_id",suffixes=("","_refunds"))

        # merge with w_sessions
        filtered_data = filtered_data.merge(w_sessions,how="left",left_on="website_session_id",right_on="website_session_id",suffixes=("","_sessions"))

        # Extract Year for filtering
        filtered_data["year"] = filtered_data["created_at_orderitem"].dt.year

        # cogs time to decimal
        def time_to_hour_min_decimal(t):
            try:
                h, m, s = str(t).split(":")
                return float(h) + float(m)/100
            except:
                return None

        filtered_data["cogs_usd_decimal"] = filtered_data["cogs_usd_orderitem"].apply(time_to_hour_min_decimal)

        # Filter options
        Years = filtered_data["year"].dropna().sort_values().unique()
        Products = filtered_data["product_name"].dropna().unique()
        Sources = filtered_data["utm_source"].dropna().unique()
        Campaigns = filtered_data["utm_campaign"].dropna().unique()
        Devices = filtered_data["device_type"].dropna().unique()
        
        st.sidebar.title("🔍 Filters")
        selected_years = st.sidebar.multiselect("Year", Years)
        
        selected_products = st.sidebar.multiselect("Product", Products)
        
        selected_sources = st.sidebar.multiselect("UTM Source", Sources)
        
        selected_campaigns =st.sidebar.multiselect("UTM Campaign",Campaigns)
        
        selected_devices = st.sidebar.multiselect("Device Type", Devices)

        # Apply filters
        final_df = filtered_data.copy()
        if selected_years:
            final_df = final_df[final_df["year"].isin(selected_years)]
        if selected_products:
            final_df = final_df[final_df["product_name"].isin(selected_products)]
        if selected_sources:
            final_df = final_df[final_df["utm_source"].isin(selected_sources)]
        if selected_campaigns:
            final_df = final_df[final_df["utm_campaign"].isin(selected_campaigns)]
        if selected_devices:
            final_df = final_df[final_df["device_type"].isin(selected_devices)]



        


        st.markdown("### 🎯 Monthly Orders and Revenue by Year")
        # Step 1: Convert to datetime and extract month & year
        final_df["created_at_orderitem"] = pd.to_datetime(final_df["created_at_orderitem"])
        final_df["month"] = final_df["created_at_orderitem"].dt.strftime("%b")  # e.g., Jan, Feb
        final_df["year"] = final_df["created_at_orderitem"].dt.year

        # Optional: Keep months in correct calendar order
        month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        final_df["month"] = pd.Categorical(final_df["month"], categories=month_order, ordered=True)

        # Step 2: Aggregate by month and year
        monthly_analysis = (final_df.groupby(["year", "month"]).agg(Total_orders=("order_id", "count"),Total_revenue=("price_usd_orderitem", "sum")).reset_index().sort_values(["year", "month"]))
        monthly_analysis["Total_revenue"] = monthly_analysis["Total_revenue"].div(1000000)

        # Step 3: Show DataFrame in Streamlit
        st.dataframe(monthly_analysis)

        # Step 4: Plot total orders over months
        fig1, ax1 = plt.subplots(figsize=(12, 6))
        sns.lineplot(data=monthly_analysis,x='month',y='Total_orders',hue='year',marker='o',palette='tab10',ax=ax1)

        # Add labels for each point
        for _, row in monthly_analysis.iterrows():
            ax1.text(
            x=row["month"],
            y=row["Total_orders"],
            s=f'{int(row["Total_orders"])}',
            ha='center',
            va='bottom',
            fontsize=9)

        ax1.set_title("Monthly Total Orders by Year")
        ax1.set_xlabel("Month")
        ax1.set_ylabel("Number of Orders")
        ax1.set_xticks(range(len(month_order)))
        ax1.set_xticklabels(month_order, rotation=45)
        ax1.legend(title='Year')
        plt.tight_layout()
        st.pyplot(fig1)

        # Step 5: Plot total revenue over months
        fig2, ax2 = plt.subplots(figsize=(12, 6))
        sns.lineplot(data=monthly_analysis,x='month',y='Total_revenue',hue='year',marker='o',palette='tab10',ax=ax2)

        for _, row in monthly_analysis.iterrows():
            ax2.text(
            x=row["month"],
            y=row["Total_revenue"],
            s=f'{row["Total_revenue"]:.3f}',
            ha='center',
            va='bottom',
            fontsize=9
            )
        ax2.set_title("Monthly Total Revenue by Year")
        ax2.set_xlabel("Month")
        ax2.set_ylabel("Revenue (in Million USD)")
        ax2.set_xticks(range(len(month_order)))
        ax2.set_xticklabels(month_order, rotation=45)
        ax2.legend(title='Year')
        plt.tight_layout()
        st.pyplot(fig2)




        st.markdown("---")

        # Step 1: Ensure 'created_at' is datetime
        w_sessions["created_at"] = pd.to_datetime(w_sessions["created_at"])

        # Step 2: Extract weekday and hour
        w_sessions["weekday"] = w_sessions["created_at"].dt.day_name()
        w_sessions["hour"] = w_sessions["created_at"].dt.hour

        # Step 3: Chronological weekday ordering
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        w_sessions["weekday"] = pd.Categorical(w_sessions["weekday"], categories=weekday_order, ordered=True)

        # Step 4: Count sessions per day/hour
        traffic_time_pattern = (w_sessions.groupby(["weekday", "hour"], observed=True).agg(session_count=("website_session_id", "count")).reset_index())

        # Step 5: Pivot table for visualization
        traffic_pivot = traffic_time_pattern.pivot(index="hour", columns="weekday", values="session_count").fillna(0)

        # Step 6: Display in Streamlit
        st.markdown("### 🕒 Website Sessions by Hour and Weekday")
        st.dataframe(traffic_pivot)

        # Step 7: Heatmap plot
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.heatmap(traffic_pivot,cmap="YlGnBu",linewidths=0.5,linecolor="gray",annot=True,fmt=".0f",ax=ax)

        ax.set_title("Website Sessions by Hour and Weekday")
        ax.set_xlabel("Weekday")
        ax.set_ylabel("Hour of Day")

        plt.tight_layout()

        # Show in Streamlit
        st.pyplot(fig)



        st.markdown("---")
        # Step 1: Convert timestamp to datetime
        w_sessions["created_at"] = pd.to_datetime(w_sessions["created_at"])

        # Step 2: Extract weekday and hour
        w_sessions["weekday"] = w_sessions["created_at"].dt.day_name()
        w_sessions["hour"] = w_sessions["created_at"].dt.hour

        # Optional: Chronological weekday order
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        w_sessions["weekday"] = pd.Categorical(w_sessions["weekday"], categories=weekday_order, ordered=True)

        # Step 3: Mark whether session converted
        converted_sessions = orders["website_session_id"].unique()
        w_sessions["converted"] = w_sessions["website_session_id"].isin(converted_sessions).astype(int)

        # Step 4: Group and calculate session counts & conversions
        conversion_trends = (w_sessions.groupby(["weekday", "hour"], observed=True).agg(Total_sessions=("website_session_id", "count"),conversions=("converted", "sum"))
                            .assign(CVR_percentage=lambda x: round((x["conversions"] / x["Total_sessions"]) * 100, 2)).reset_index())

        # Step 5: Pivot table for heatmap
        conversion_pivot = (conversion_trends.pivot(index="hour", columns="weekday", values="CVR_percentage").fillna(0))

        # Step 6: Display DataFrame in Streamlit
        st.markdown("### ⚡ Conversion Rate (%) by Hour and Weekday")
        st.dataframe(conversion_pivot)

        # Step 7: Heatmap plot in Streamlit
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.heatmap(conversion_pivot,cmap="YlGnBu",linewidths=0.5,linecolor="gray",annot=True,fmt=".2f",ax=ax)

        ax.set_title("Conversion Rate (%) by Hour and Weekday")
        ax.set_xlabel("Weekday")
        ax.set_ylabel("Hour of Day")
        plt.tight_layout()

        # Show in Streamlit
        st.pyplot(fig)



        st.markdown("---")
        # Step 1: Convert to datetime and create 'order_month'
        final_df["created_at_orderitem"] = pd.to_datetime(final_df["created_at_orderitem"])
        final_df["order_month"] = final_df["created_at_orderitem"].dt.to_period("M").astype(str)  # e.g., '2024-06'

        # Step 2: Aggregate monthly revenue
        monthly_analysis = (final_df.groupby("order_month").agg(Total_revenue=("price_usd_orderitem", "sum")).reset_index())

        # Step 3: Convert 'order_month' to datetime for growth calculations
        monthly_analysis["order_month"] = pd.to_datetime(monthly_analysis["order_month"])

        # Step 4: Extract year and month
        monthly_analysis["year"] = monthly_analysis["order_month"].dt.year
        monthly_analysis["month"] = monthly_analysis["order_month"].dt.month

        # Step 5: Sort and calculate Month-over-Month (MoM) growth
        monthly_analysis = monthly_analysis.sort_values(["year", "month"]).reset_index(drop=True)
        monthly_analysis["MoM_growth_%"] = monthly_analysis["Total_revenue"].pct_change().round(4) * 100

        # Step 6: Year-over-Year (YoY) comparison using pivot
        revenue_pivot = monthly_analysis.pivot_table(index="month", columns="year", values="Total_revenue")

        # Step 7: Calculate YoY growth between last two years
        if revenue_pivot.shape[1] >= 2:
            latest_year = revenue_pivot.columns[-2]
            previous_year = revenue_pivot.columns[-3]
            revenue_pivot["YoY_growth_% (wrt 2014 and 2013)"] = ((revenue_pivot[latest_year] - revenue_pivot[previous_year]) / revenue_pivot[previous_year]).round(4) * 100
        else:
            revenue_pivot["YoY_growth_%"] = None

        st.markdown("### 📊 Year-over-Year Growth Comparison")
        st.dataframe(revenue_pivot)

        # Convert datetime to abbreviated month names
        monthly_analysis["month_name"] = monthly_analysis["order_month"].dt.strftime("%b")

        # Optional: Ensure months are ordered chronologically
        month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun","Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        monthly_analysis["month_name"] = pd.Categorical(monthly_analysis["month_name"], categories=month_order, ordered=True)



        st.markdown("---")
        st.markdown("### 📈 Month-over-Month Revenue Growth")
        # Step 9: Line Chart for MoM Growth

        monthly_plot_df = (monthly_analysis.groupby("month_name", as_index=False).agg({"MoM_growth_%": "mean"}))
        
        fig, ax = plt.subplots(figsize=(12,6))
        sns.lineplot(data=monthly_plot_df,x="month_name",y="MoM_growth_%",marker="o",color="steelblue",ax=ax,ci=None)

        # Add labels on each point
        for _, row in monthly_plot_df.iterrows():
            if pd.notnull(row["MoM_growth_%"]):
                ax.text(x=row["month_name"],y=row["MoM_growth_%"],s=f"{row['MoM_growth_%']:.1f}%",ha="center",va="bottom",fontsize=9)

        ax.set_title("Month-over-Month Revenue Growth")
        ax.set_xlabel("Month")
        ax.set_ylabel("MoM Growth (%)")
        ax.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()

        # Show chart
        st.pyplot(fig)


        















        

    elif selection == "Product Analysis":
        st.header("📊 Product Analysis")
        # Start with order_items
        filtered_data = order_items.copy()

        # merge with orders
        filtered_data = filtered_data.merge(orders, how="left", on="order_id",suffixes=("_orderitem", "_order"))

        # merge with products
        filtered_data = filtered_data.merge(products, how="left", left_on="product_id",right_on="product_id",suffixes=("","_products"))

        # merge with refund
        filtered_data = filtered_data.merge(order_item_refunds, how="left", on="order_item_id",suffixes=("","_refunds"))

        # merge with w_sessions
        filtered_data = filtered_data.merge(w_sessions,how="left",left_on="website_session_id",right_on="website_session_id",suffixes=("","_sessions"))

        # Extract Year for filtering
        filtered_data["year"] = filtered_data["created_at_orderitem"].dt.year

        # cogs time to decimal
        def time_to_hour_min_decimal(t):
            try:
                h, m, s = str(t).split(":")
                return float(h) + float(m)/100
            except:
                return None

        filtered_data["cogs_usd_decimal"] = filtered_data["cogs_usd_orderitem"].apply(time_to_hour_min_decimal)

        # Filter options
        Years = filtered_data["year"].dropna().sort_values().unique()
        Products = filtered_data["product_name"].dropna().unique()
        Sources = filtered_data["utm_source"].dropna().unique()
        Campaigns = filtered_data["utm_campaign"].dropna().unique()
        Devices = filtered_data["device_type"].dropna().unique()
        
        st.sidebar.title("🔍 Filters")
        selected_years = st.sidebar.multiselect("Year", Years)
        selected_products = st.sidebar.multiselect("Product", Products)
        selected_sources = st.sidebar.multiselect("UTM Source", Sources)
        selected_campaigns =st.sidebar.multiselect("UTM Campaign",Campaigns)
        selected_devices = st.sidebar.multiselect("Device Type", Devices)

        # Apply filters
        final_df = filtered_data.copy()
        if selected_years:
            final_df = final_df[final_df["year"].isin(selected_years)]
        if selected_products:
            final_df = final_df[final_df["product_name"].isin(selected_products)]
        if selected_sources:
            final_df = final_df[final_df["utm_source"].isin(selected_sources)]
        if selected_campaigns:
            final_df = final_df[final_df["utm_campaign"].isin(selected_campaigns)]
        if selected_devices:
            final_df = final_df[final_df["device_type"].isin(selected_devices)]


        if not final_df.empty:
            st.markdown("### 💸 Product Wise Total Sales")
            
            Products_Sales=final_df.groupby('product_name')['price_usd_orderitem'].sum()/1000000
            Products_Sales = Products_Sales.reset_index()
            Products_Sales.columns = ['Product_Name', 'Total_sales_amount']
            st.dataframe(Products_Sales)

            sorted_products_sales = Products_Sales.sort_values(by='Total_sales_amount',ascending=False)

            #Plotting product_wise sales in millions
            # Plot bar chart
            fig, ax = plt.subplots(figsize=(9, 4))
            bars = ax.bar(sorted_products_sales['Product_Name'],sorted_products_sales['Total_sales_amount'],color='skyblue')
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            ax.set_title("Product-wise Sales in Millions")
            ax.set_xlabel("Product Name")
            ax.set_ylabel("Sales (USD in Millions)")

            # Add labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height:.2f}",xy=(bar.get_x() + bar.get_width() / 2, height),xytext=(0, 3),  textcoords="offset points",ha='center',va='bottom',fontsize=8)

            # Display plot
            st.pyplot(fig)
           


            st.markdown("---")
            st.markdown("### 🛒 Product wise Orders")

            product_orders = final_df.groupby('product_name')['order_id'].nunique().reset_index()
            product_orders.columns = ['Product_Name', 'Total_orders']
            st.dataframe(product_orders)

            sorted_product_orders = product_orders.sort_values(by='Total_orders',ascending=False)

            #Plotting product_wise orders
            # Plot bar chart
            fig, ax = plt.subplots(figsize=(9, 4))
            bars = ax.bar(sorted_product_orders ['Product_Name'],sorted_product_orders ['Total_orders'],color='skyblue')
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            ax.set_title("Product-wise Orders")
            ax.set_xlabel("Product Name")
            ax.set_ylabel("Total_orders")

            # Add labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height}",xy=(bar.get_x() + bar.get_width() / 2, height),xytext=(0, 3),  textcoords="offset points",ha='center',va='bottom',fontsize=8)

            # Display plot
            st.pyplot(fig)



            st.markdown("---")
            st.markdown("### 🎯 Product wise Profitability")

            product_sales = final_df.groupby('product_name').agg({'order_item_id': 'count', 'price_usd_orderitem': 'sum','cogs_usd_decimal' : 'sum','refund_amount_usd' : 'sum'}).reset_index()
            product_sales.columns = ['Product_name', 'Total Quantity', 'Total Revenue','Total Cost', 'Total Refund']
            product_sales['Profit'] = (product_sales['Total Revenue'] - product_sales['Total Cost']-product_sales['Total Refund'])/1000

            profit_productwise= product_sales[['Product_name', 'Profit']]
            st.dataframe(profit_productwise)

            sorted_product_profit = product_sales.sort_values(by='Profit',ascending=False)
            # Plot bar chart
            fig, ax = plt.subplots(figsize=(9, 4))
            bars = ax.bar(profit_productwise['Product_name'], sorted_product_profit ['Profit'],color='skyblue')
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            ax.set_title("Product-wise Profitability ")
            ax.set_xlabel("Product Name")
            ax.set_ylabel("Total_profit(in Thousands)")

            # Add labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height:.2f}",xy=(bar.get_x() + bar.get_width() / 2, height),xytext=(0, 3),  textcoords="offset points",ha='center',va='bottom',fontsize=8)

            # Display plot
            st.pyplot(fig)



            st.markdown("---")
            st.markdown("### 🧩 Product wise conversion rate")
            Total_orders = final_df['order_id'].nunique()
            Total_sessions = w_sessions['website_session_id'].count()

            conversion_rate= Total_orders / Total_sessions
            

            # Product wise conversion rate
            product_conversion_rate = final_df.groupby('product_name')['order_id'].nunique() / Total_sessions
            product_conversion_rate=product_conversion_rate.reset_index()
            product_conversion_rate.columns = ['Product_name', 'Conversion Rate']
            st.dataframe(product_conversion_rate,use_container_width=True, hide_index=True)

            sorted_product_conversion = product_conversion_rate.sort_values(by='Conversion Rate',ascending=False)

            # Plot bar chart
            fig, ax = plt.subplots(figsize=(9, 4))
            bars = ax.bar(profit_productwise['Product_name'],sorted_product_conversion ['Conversion Rate'],color='skyblue')
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            ax.set_title("Product-wise Conversion rate")
            ax.set_xlabel("Product Name")
            ax.set_ylabel("Conversion Rate")

            # Add labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height:.4f}",xy=(bar.get_x() + bar.get_width() / 2, height),xytext=(0, 3),  textcoords="offset points",ha='center',va='bottom',fontsize=8)

            # Display plot
            st.pyplot(fig)




            st.markdown("---")


            st.markdown("### 🔼 Product wise Purchase Rate")
            Total_orders = final_df['order_id'].nunique()
            product_purchase_rate = (final_df.groupby('product_name')['order_id'].nunique() / Total_orders)
            product_purchase_rate =product_purchase_rate .reset_index()
            product_purchase_rate .columns = ['Product_name', 'Purchase Rate']
            st.dataframe(product_purchase_rate)

            sorted_product_purchaserate = product_purchase_rate.sort_values(by='Purchase Rate',ascending=False)

            # Plot bar chart
            fig, ax = plt.subplots(figsize=(9, 4))
            bars = ax.bar(profit_productwise['Product_name'],sorted_product_purchaserate['Purchase Rate'],color='skyblue')
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            ax.set_title("Product-wise Purchase Rate")
            ax.set_xlabel("Product Name")
            ax.set_ylabel("Purchase Rate")

            # Add labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height:.2f}",xy=(bar.get_x() + bar.get_width() / 2, height),xytext=(0, 3),  textcoords="offset points",ha='center',va='bottom',fontsize=8)

            # Display plot
            st.pyplot(fig)


            st.markdown("---")
            st.markdown("### 🔁 Product wise Refund Rate")
            Total_orders = final_df['order_id'].nunique()
            Refund_rate=( final_df.groupby('product_name')['order_item_refund_id'].count() / Total_orders)
            product_refund_rate =Refund_rate .reset_index()
            product_refund_rate.columns = ['Product_name', 'Refund Rate']
            st.dataframe(product_refund_rate)

            sorted_product_refund_rate = product_refund_rate.sort_values(by='Refund Rate',ascending=False)

            # Plot bar chart
            fig, ax = plt.subplots(figsize=(9, 4))
            bars = ax.bar(profit_productwise['Product_name'],sorted_product_refund_rate['Refund Rate'],color='skyblue')
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
            ax.set_title("Product-wise Refund Rate")
            ax.set_xlabel("Product Name")
            ax.set_ylabel("Refund Rate")

            # Add labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height:.3f}",xy=(bar.get_x() + bar.get_width() / 2, height),xytext=(0, 3),  textcoords="offset points",ha='center',va='bottom',fontsize=8)

            # Display plot
            st.pyplot(fig)




            st.markdown("---")
            st.markdown("### 🧃 Product sales and product lauches")

            Yearly_product_sales = final_df.groupby([final_df['created_at_orderitem'].dt.year,'product_name'])['price_usd_orderitem'].sum().div(1000000).reset_index()
            Yearly_product_sales.columns=['Year','Product_name','Total Sales']
            st.dataframe(Yearly_product_sales)

            Yearly_product_sales = Yearly_product_sales.sort_values(by='Year',ascending=True)
            
            fig, ax = plt.subplots(figsize=(8,6))
            sns.barplot(data=Yearly_product_sales,x='Year',y='Total Sales',hue='Product_name',ax=ax)

            ax.set_title('Yearly Sales by Product')
            ax.set_xlabel('Year')
            ax.set_ylabel('Total_Sales_Million_USD')
            ax.legend(title='Product Name', loc='upper left')
            plt.xticks(rotation=0)

            for container in ax.containers:
                ax.bar_label(container, fmt='%.2f', label_type='edge', padding=3, fontsize=8)

            fig.tight_layout()

            st.pyplot(fig)


            st.markdown("---")
            st.markdown("### 🔄 Cross-Sell Products")
            merge1 = order_items.merge(products, on='product_id')
            items_merge = merge1.merge(merge1,on='order_id',suffixes=('_x', '_y'))

            pairs = items_merge[items_merge['product_id_x'] != items_merge['product_id_y']]

            pair_counts = (pairs.groupby(['product_name_x', 'product_name_y']).size().reset_index(name='count'))

            st.dataframe(pair_counts)

            # Plot
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.barplot(data=pair_counts,x='product_name_x',y='count',hue='product_name_y',ax=ax)
            ax.set_title('Cross-Sell Products')
            ax.set_xlabel('Product')
            ax.set_ylabel('Cross-Sell Count')
            ax.legend(title='Cross-Sold With', loc='upper left')
            plt.xticks(rotation=45, ha='right')
            for container in ax.containers:
                ax.bar_label(container, fmt='%.0f', label_type='edge', padding=3, fontsize=8)

            fig.tight_layout()
            st.pyplot(fig)


            

        

    elif selection == "User Analysis":
        st.title("📊 User Analysis")
        # Filters
        # Start with order_items
        filtered_data = order_items.copy()

        # merge with orders
        filtered_data = filtered_data.merge(orders, how="left", on="order_id",suffixes=("_orderitem", "_order"))

        # merge with products
        filtered_data = filtered_data.merge(products, how="left", left_on="product_id",right_on="product_id",suffixes=("","_products"))

        # merge with refund
        filtered_data = filtered_data.merge(order_item_refunds, how="left", on="order_item_id",suffixes=("","_refunds"))

        # merge with w_sessions
        filtered_data = filtered_data.merge(w_sessions,how="left",left_on="website_session_id",right_on="website_session_id",suffixes=("","_sessions"))

        # Extract Year for filtering
        filtered_data["year"] = filtered_data["created_at_orderitem"].dt.year

        # cogs time to decimal
        def time_to_hour_min_decimal(t):
            try:
                h, m, s = str(t).split(":")
                return float(h) + float(m)/100
            except:
                return None

        filtered_data["cogs_usd_decimal"] = filtered_data["cogs_usd_orderitem"].apply(time_to_hour_min_decimal)

        # Filter options
        Years = filtered_data["year"].dropna().sort_values().unique()
        Products = filtered_data["product_name"].dropna().unique()
        Sources = filtered_data["utm_source"].dropna().unique()
        Campaigns = filtered_data["utm_campaign"].dropna().unique()
        Devices = filtered_data["device_type"].dropna().unique()
        
        st.sidebar.title("🔍 Filters")
        selected_years = st.sidebar.multiselect("Year", Years)
        selected_products = st.sidebar.multiselect("Product", Products)
        selected_sources = st.sidebar.multiselect("UTM Source", Sources)
        selected_campaigns =st.sidebar.multiselect("UTM Campaign",Campaigns)
        selected_devices = st.sidebar.multiselect("Device Type", Devices)

        # Apply filters
        final_df = filtered_data.copy()
        if selected_years:
            final_df = final_df[final_df["year"].isin(selected_years)]
        if selected_products:
            final_df = final_df[final_df["product_name"].isin(selected_products)]
        if selected_sources:
            final_df = final_df[final_df["utm_source"].isin(selected_sources)]
        if selected_campaigns:
            final_df = final_df[final_df["utm_campaign"].isin(selected_campaigns)]
        if selected_devices:
            final_df = final_df[final_df["device_type"].isin(selected_devices)]

        if not final_df.empty:
            st.markdown("### 🧑‍💻 New vs Repeat Visitors")
            visitor_types=final_df.groupby('is_repeat_session')['website_session_id'].count().reset_index()
            visitor_types.columns = ['Visitors_type', 'session_count']
            
            mapping={0: 'New Visitor', 1: 'Repeat Visitor'}
            visitor_types['Visitors_type'] = visitor_types['Visitors_type'].map(mapping)
            st.dataframe(visitor_types)

            # Plot pie chart
            fig, ax = plt.subplots(figsize=(2,2))
            ax.pie(visitor_types['session_count'],
            labels=visitor_types['Visitors_type'],
            autopct='%1.2f%%',
            startangle=90,
            textprops={'fontsize': 6})
            ax.set_title("User Type Distribution",fontsize=6)
            ax.axis('equal')  # Equal aspect ratio ensures pie is a circle
            
            # Display chart in Streamlit
            st.pyplot(fig)




            st.markdown("---")

        
            st.markdown("### 💰 Customer Segmentation by Monetary Value")
            customer_summary = filtered_data.groupby('user_id').agg(Total_spent=('price_usd_orderitem', 'sum'),Total_orders=('order_id', 'nunique')).reset_index()
            # Compute percentiles
            p66 = np.percentile(customer_summary['Total_spent'], 66)
            p33 = np.percentile(customer_summary['Total_spent'], 33)

            # Customer Segmentation Function
            def Monetary_segment(x):
                if x >= p66:
                    return 'High Value'
                elif x >= p33:
                    return 'Medium Value'
                else:
                    return 'Low Value'

            # Assign segment
            customer_summary['Segment_Monetary'] = customer_summary['Total_spent'].apply(Monetary_segment)

            # Summarize segments
            Monetary_segment_summary = (customer_summary.groupby('Segment_Monetary')['user_id'].count().reset_index().rename(columns={'user_id': 'Number_of_Customers'}))
            st.dataframe(Monetary_segment_summary)

            # Step 5: Sort by customer count
            Monetary_segment_summary = Monetary_segment_summary.sort_values(by='Number_of_Customers', ascending=False)

            # Plot bar chart
            fig, ax = plt.subplots(figsize=(9, 4))
            bars = ax.bar(Monetary_segment_summary['Segment_Monetary'],Monetary_segment_summary['Number_of_Customers'],color='skyblue')
            ax.set_title("Customer Segmentation by Monetary Value")
            ax.set_xlabel("Customer Segment")
            ax.set_ylabel("Number of Customers")

            # Add labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height}",xy=(bar.get_x() + bar.get_width() / 2, height),xytext=(0, 3),  textcoords="offset points",ha='center',va='bottom',fontsize=8)

            # Display plot
            st.pyplot(fig)




            st.markdown("---")

            st.markdown("### 📦 Customer Segmentation by Frequency Value")
            customer_summary = filtered_data.groupby('user_id').agg(Total_spent=('price_usd_orderitem', 'sum'),Total_orders=('order_id', 'nunique')).reset_index()
         
            # Customer Segmentation Function
            def Frequency_segment(x):
                if x >= 3:
                    return 'High Value'
                elif x >= 2:
                    return 'Medium Value'
                else:
                    return 'Low Value'

            # Assign segment
            customer_summary['Segment_Frequency'] = customer_summary['Total_orders'].apply(Frequency_segment)

            # Summarize segments
            Frequency_segment_summary = (customer_summary.groupby('Segment_Frequency')['user_id'].count().reset_index().rename(columns={'user_id': 'Number_of_Customers'}))
            st.dataframe(Frequency_segment_summary)

            # Step 5: Sort by customer count
            Frequency_segment_summary = Frequency_segment_summary.sort_values(by='Number_of_Customers', ascending=False)

            # Plot bar chart
            fig, ax = plt.subplots(figsize=(9, 4))
            bars = ax.bar(Frequency_segment_summary['Segment_Frequency'],Frequency_segment_summary['Number_of_Customers'],color='skyblue')
            ax.set_title("Customer Segmentation by Frequency Value")
            ax.set_xlabel("Customer Segment")
            ax.set_ylabel("Number of Customers")

            # Add labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height}",xy=(bar.get_x() + bar.get_width() / 2, height),xytext=(0, 3),  textcoords="offset points",ha='center',va='bottom',fontsize=8)

            # Display plot
            st.pyplot(fig)




            st.markdown("---")
        
            st.markdown("### ⏳ Customer Segmentation by Recency Value")
            customer_summary['Last_purchase']= final_df.groupby('user_id')['created_at_orderitem'].transform('max')
            #Recency Calculation
            customer_summary['Recency'] = (pd.to_datetime('now') - customer_summary['Last_purchase']).dt.days
            
            # Customer Segmentation
            def Recency_segment(x):
                if x >= np.percentile(customer_summary['Recency'],66):
                    return 'Low Value'
                elif x>= np.percentile(customer_summary['Recency'],33):
                    return 'Medium Value'
                else:
                    return 'High Value'
    
            customer_summary['Segment_Recency'] = customer_summary['Recency'].apply(Recency_segment)
            
            # Summarize the Recency segments
            Recency_segment_summary = customer_summary.groupby('Segment_Recency')['user_id'].count().reset_index()
            Recency_segment_summary.columns = ['Segment_Recency', 'Number_of_Customers']
            st.dataframe(Recency_segment_summary)

            # Step 5: Sort by customer count
            Recency_segment_summary = Recency_segment_summary.sort_values(by='Number_of_Customers', ascending=False)

            # Plot bar chart
            fig, ax = plt.subplots(figsize=(9, 4))
            bars = ax.bar(Recency_segment_summary['Segment_Recency'],Recency_segment_summary['Number_of_Customers'],color='skyblue')
            ax.set_title("Customer Segmentation by Recency Value")
            ax.set_xlabel("Customer Segment")
            ax.set_ylabel("Number of Customers")

            # Add labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height}",xy=(bar.get_x() + bar.get_width() / 2, height),xytext=(0, 3),  textcoords="offset points",ha='center',va='bottom',fontsize=8)

            # Display plot
            st.pyplot(fig)
            



            st.markdown("---")

            st.markdown("### 🌐 RFM Segmentation ")
            customer_summary = filtered_data.groupby('user_id').agg(Total_spent=('price_usd_orderitem', 'sum'),Total_orders=('order_id', 'nunique')).reset_index()
            customer_summary['Segment_Monetary'] = customer_summary['Total_spent'].apply(Monetary_segment)
            customer_summary['Segment_Frequency'] = customer_summary['Total_orders'].apply(Frequency_segment)
            customer_summary['Last_purchase']= final_df.groupby('user_id')['created_at_orderitem'].transform('max')
            customer_summary['Recency'] = (pd.to_datetime('now') - customer_summary['Last_purchase']).dt.days
            customer_summary['Segment_Recency'] = customer_summary['Recency'].apply(Recency_segment)

            # Map categorical values to numeric scores
            mapping = {"Low Value": 1, "Medium Value": 2, "High Value": 3}
            RFM_Final = customer_summary.copy()
            RFM_Final = RFM_Final.replace({"Segment_Monetary": mapping,"Segment_Frequency": mapping,"Segment_Recency": mapping})

            # Compute RFM Score
            RFM_Final['RFM_Score'] = (RFM_Final['Segment_Monetary']+ RFM_Final['Segment_Frequency']+ RFM_Final['Segment_Recency'])

            # Segment based on total RFM Score
            def RFM_segment(x):
                if x > np.percentile(RFM_Final['RFM_Score'], 66):
                    return 'High Value'
                elif x > np.percentile(RFM_Final['RFM_Score'], 33):
                    return 'Medium Value'
                else:
                    return 'Low Value'

            RFM_Final['Segment_RFM'] = RFM_Final['RFM_Score'].apply(RFM_segment)

            # Create summary table
            RFM_Final_summary = (RFM_Final.groupby('Segment_RFM')['user_id'].count().reset_index().rename(columns={'user_id': 'Number_of_Customers'}))

            # Sort segments for display order
            RFM_Final_summary['Segment_RFM'] = pd.Categorical(RFM_Final_summary['Segment_RFM'],categories=['Low Value', 'Medium Value', 'High Value'],ordered=True)
            RFM_Final_summary = RFM_Final_summary.sort_values('Segment_RFM')
            st.dataframe(RFM_Final_summary)

            # Plot bar chart
            fig, ax = plt.subplots(figsize=(9, 4))
            bars = ax.bar(RFM_Final_summary['Segment_RFM'],RFM_Final_summary['Number_of_Customers'],color='skyblue')
            ax.set_title("Customer Segmentation by RFM Value")
            ax.set_xlabel("Customer Segment")
            ax.set_ylabel("Number of Customers")

            # Add labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height}",xy=(bar.get_x() + bar.get_width() / 2, height),xytext=(0, 3),  textcoords="offset points",ha='center',va='bottom',fontsize=8)

            # Display plot
            st.pyplot(fig)




            st.markdown("---")

            st.markdown("### 🔧 Behavioural Segmentation by Website Views")
            # Behavioural Segmentation
            page_counts = website_pageviews.groupby('website_session_id')['pageview_url'].nunique().reset_index(name='pages_viewed')
            
            session_page_merged=w_sessions.merge(page_counts, on='website_session_id', how='left')
            session_page_merged.head(2)

            pageview_summary= session_page_merged.groupby('pages_viewed')['user_id'].nunique().reset_index(name='Number_of_Users')

            def segment_behavior(x):
                if x >= np.percentile(pageview_summary['pages_viewed'],66):
                    return 'Deep Engagement'
                elif x >= np.percentile(pageview_summary['pages_viewed'],33):
                    return 'Moderate Engagement'
                else:
                    return 'Low Engagement'
    
            pageview_summary['Segment'] = pageview_summary['pages_viewed'].apply(segment_behavior)

            Behaviour_summary=pageview_summary.groupby('Segment')['Number_of_Users'].sum().reset_index()
            st.dataframe(Behaviour_summary)

            # Step 5: Sort by customer count
            Behaviour_summary = Behaviour_summary.sort_values(by='Number_of_Users', ascending=False)

            # Plot bar chart
            fig, ax = plt.subplots(figsize=(9, 4))
            bars = ax.bar(Behaviour_summary['Segment'],Behaviour_summary['Number_of_Users'],color='skyblue')
            ax.set_title("Customer Segmentation by page views")
            ax.set_xlabel("Customer Segment")
            ax.set_ylabel("Number of Customers")

            # Add labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height}",xy=(bar.get_x() + bar.get_width() / 2, height),xytext=(0, 3),  textcoords="offset points",ha='center',va='bottom',fontsize=8)

            # Display plot
            st.pyplot(fig)





            st.markdown("---")

            #Cohort Analysis
            st.markdown("### 🔧 Cohort Analysis")

            final_df['cohort_month'] = final_df.groupby('user_id')['created_at_orderitem'].transform('min').dt.to_period('M')
            final_df['order_month'] = final_df['created_at_orderitem'].dt.to_period('M')

            cohort_data = final_df.groupby(['cohort_month','order_month']).agg({'user_id':'nunique'}).reset_index()
            cohort_pivot = cohort_data.pivot(index='cohort_month', columns='order_month', values='user_id')

            # Display the pivot table in Streamlit
            st.subheader("📊 Cohort Table (Counts of Unique Users)")
            st.dataframe(cohort_pivot)





    if st.button("Logout"):
        st.session_state["authenticated"] = False

# Run app
if not st.session_state["authenticated"]:
    login()
else:
    main_app()