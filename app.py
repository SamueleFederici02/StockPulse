import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from utils import (
    get_stock_data, create_price_chart, prepare_metrics_data, 
    prepare_table_data, search_stock, get_world_indices, get_top_movers
)
from styles import apply_custom_styles

# Page configuration must be the first Streamlit command
st.set_page_config(
    page_title="Stock Data Visualization",
    page_icon="📈",
    layout="wide"
)

def show_stock_details(symbol, company_name=None):
    """Helper function to display stock details"""
    period = '1y'  # Default period
    
    # Add auto-refresh
    st.empty()
    time = datetime.now().strftime("%H:%M:%S")
    st.caption(f"Last updated: {time}")
    st.experimental_rerun()
    
    with st.spinner('Fetching stock data...'):
        hist_data, info = get_stock_data(symbol, period)

    if hist_data is not None and info is not None:
        # Display company name and current price
        st.markdown(f"### {company_name or info.get('longName', symbol)} ({symbol})")
        
        # Time period selection
        periods = {
            "1D": "1d", "5D": "5d", "1M": "1mo",
            "6M": "6mo", "YTD": "ytd", "1Y": "1y",
            "5Y": "5y", "All": "max"
        }
        period_cols = st.columns(len(periods))
        for i, (label, value) in enumerate(periods.items()):
            with period_cols[i]:
                if st.button(label, key=f"period_{value}"):
                    hist_data, info = get_stock_data(symbol, value)
        current_price = hist_data['Close'].iloc[-1]
        price_change = hist_data['Close'].iloc[-1] - hist_data['Close'].iloc[-2]
        price_change_pct = (price_change / hist_data['Close'].iloc[-2]) * 100

        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Current Price",
                f"${current_price:.2f}",
                f"{price_change_pct:.2f}% (${price_change:+.2f})"
            )

        # Display interactive chart with tabs
        st.subheader("Price Chart")
        chart_tab1, chart_tab2, chart_tab3 = st.tabs(["Candlestick", "Area", "Baseline"])

        # Display key metrics
        st.subheader("Key Metrics")
        metrics = prepare_metrics_data(info)
        cols = st.columns(3)
        for i, (metric, value) in enumerate(metrics.items()):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="metric-card">
                    <h4>{metric}</h4>
                    <p>{value}</p>
                </div>
                """, unsafe_allow_html=True)
        
        with chart_tab1:
            fig1 = go.Figure()
            fig1.add_trace(go.Candlestick(
                x=hist_data.index, open=hist_data['Open'],
                high=hist_data['High'], low=hist_data['Low'],
                close=hist_data['Close'], name='Candlestick'
            ))
            fig1.update_layout(height=600, template='plotly_white', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig1, use_container_width=True)
            
        with chart_tab2:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=hist_data.index, y=hist_data['Close'],
                fill='tozeroy', name='Area'
            ))
            fig2.update_layout(height=600, template='plotly_white', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig2, use_container_width=True)
            
        with chart_tab3:
            fig3 = go.Figure()
            baseline = hist_data['Close'].iloc[0]
            fig3.add_trace(go.Scatter(
                x=hist_data.index, y=hist_data['Close'],
                name='Baseline', line=dict(color='blue')
            ))
            fig3.add_hline(y=baseline, line_dash="dash", line_color="red", name="Baseline")
            fig3.update_layout(height=600, template='plotly_white', xaxis_rangeslider_visible=False)
            st.plotly_chart(fig3, use_container_width=True)

        # Display and export data table
        st.subheader("Historical Data")
        table_data = prepare_table_data(hist_data)
        st.dataframe(table_data)

        # CSV export
        csv = table_data.to_csv()
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name=f"{symbol}_stock_data.csv",
            mime="text/csv"
        )
    else:
        st.error("Error fetching data. Please check the stock symbol and try again.")

def main():
    # Apply custom styles
    apply_custom_styles()

    # Header and Search Bar
    st.title("📈 Stock Data Visualization Tool")

    # Search bar in a container with custom styling
    with st.container():
        search_query = st.text_input(
            "🔍 Search by stock symbol or company name (e.g., AAPL or Apple)",
            value="",
            key="main_search"
        )

    # Navigation buttons
    tab1, tab2, tab3 = st.tabs(["Stock Details", "World Indices", "Top Movers"])

    with tab1:
        if search_query:
            # Search for stocks
            with st.spinner('Searching for stocks...'):
                results = search_stock(search_query.upper())

            if results:
                if len(results) == 1:
                    symbol = results[0][0]
                    company_name = results[0][1]
                else:
                    st.subheader("Multiple matches found:")
                    options = {f"{symbol} - {name}": symbol for symbol, name in results}
                    selected = st.selectbox(
                        "Select the correct company:",
                        options=list(options.keys())
                    )
                    symbol = options[selected]
                    company_name = dict(results)[symbol]

                show_stock_details(symbol, company_name)
            else:
                st.error("No matching stocks found. Try a different symbol or company name.")

    with tab2:
        st.header("World Indices")
        with st.spinner('Loading market data...'):
            indices_df = get_world_indices()

            # Create mapping of index names to symbols
            index_symbols = {
                'S&P 500': '^GSPC',
                'Dow Jones': '^DJI',
                'NASDAQ': '^IXIC',
                'FTSE 100': '^FTSE',
                'Nikkei 225': '^N225',
                'Hang Seng': '^HSI',
                'DAX': '^GDAXI',
                'CAC 40': '^FCHI'
            }

            # Apply color formatting to Change and Change % columns
            def color_change(x):
                colors = []
                for col, val in x.items():
                    if col in ['Change', 'Change %']:
                        color = 'green' if '+' in str(val) else 'red'
                        colors.append(f'color: {color}')
                    else:
                        colors.append('')
                return colors

            # Display the dataframe with colored text
            styled_df = indices_df.drop('Change_Color', axis=1).style.apply(color_change, axis=1)

            selected_indices = st.data_editor(
                styled_df,
                column_config={
                    "Index": st.column_config.TextColumn("Index", width="medium"),
                    "Price": st.column_config.TextColumn("Price", width="small"),
                    "Change": st.column_config.TextColumn("Change", width="small"),
                    "Change %": st.column_config.TextColumn("Change %", width="small"),
                },
                hide_index=True,
                use_container_width=True,
                num_rows="dynamic"
            )

            # Convert selected index to list for comparison
            current_selection = list(selected_indices.index) if not selected_indices.empty else []
            prev_selection = st.session_state.get('selected_indices_row', [])

            if current_selection != prev_selection:
                st.session_state.selected_indices_row = current_selection
                if selected_indices.shape[0] > 0:
                    selected_name = selected_indices['Index'].iloc[0]
                    if selected_name in index_symbols:
                        show_stock_details(index_symbols[selected_name], selected_name)

    with tab3:
        st.header("Market Movers")
        with st.spinner('Loading top movers...'):
            top_gainers, top_losers = get_top_movers()

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📈 Top Gainers")
                gainers_styled = top_gainers.drop('Change_Color', axis=1).style.apply(
                    lambda x: ['color: green' if col in ['Change', 'Change %'] else '' 
                              for col, val in x.items()], axis=1
                )

                selected_gainers = st.data_editor(
                    gainers_styled,
                    column_config={
                        "Symbol": st.column_config.TextColumn("Symbol", width="small"),
                        "Name": st.column_config.TextColumn("Name", width="medium"),
                        "Price": st.column_config.TextColumn("Price", width="small"),
                        "Change": st.column_config.TextColumn("Change", width="small"),
                        "Change %": st.column_config.TextColumn("Change %", width="small"),
                    },
                    hide_index=True,
                    use_container_width=True,
                    num_rows="dynamic"
                )

                # Convert selected index to list for comparison
                current_gainers = list(selected_gainers.index) if not selected_gainers.empty else []
                prev_gainers = st.session_state.get('selected_gainers_row', [])

                if current_gainers != prev_gainers:
                    st.session_state.selected_gainers_row = current_gainers
                    if selected_gainers.shape[0] > 0:
                        selected = selected_gainers.iloc[0]
                        show_stock_details(selected['Symbol'], selected['Name'])

            with col2:
                st.subheader("📉 Top Losers")
                losers_styled = top_losers.drop('Change_Color', axis=1).style.apply(
                    lambda x: ['color: red' if col in ['Change', 'Change %'] else '' 
                              for col, val in x.items()], axis=1
                )

                selected_losers = st.data_editor(
                    losers_styled,
                    column_config={
                        "Symbol": st.column_config.TextColumn("Symbol", width="small"),
                        "Name": st.column_config.TextColumn("Name", width="medium"),
                        "Price": st.column_config.TextColumn("Price", width="small"),
                        "Change": st.column_config.TextColumn("Change", width="small"),
                        "Change %": st.column_config.TextColumn("Change %", width="small"),
                    },
                    hide_index=True,
                    use_container_width=True,
                    num_rows="dynamic"
                )

                # Convert selected index to list for comparison
                current_losers = list(selected_losers.index) if not selected_losers.empty else []
                prev_losers = st.session_state.get('selected_losers_row', [])

                if current_losers != prev_losers:
                    st.session_state.selected_losers_row = current_losers
                    if selected_losers.shape[0] > 0:
                        selected = selected_losers.iloc[0]
                        show_stock_details(selected['Symbol'], selected['Name'])

    # Footer
    st.markdown("---")
    st.markdown("Data provided by Yahoo Finance")

if __name__ == "__main__":
    main()