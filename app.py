def show_comparison(india_df, city_df):
    st.subheader("📊 State vs City Comparison")

    selected_state = st.session_state.get("selected_state")
    selected_city = st.session_state.get("selected_city")

    if not selected_state or not selected_city:
        st.warning("Please select a state and city first.")
        return

    # State-level data
    state_data = india_df[india_df["State"] == selected_state]

    # City-level data
    city_data = city_df[city_df["City"] == selected_city]

    if state_data.empty or city_data.empty:
        st.error("Data not available for selected state or city.")
        return

    # Metrics
    state_avg_price = state_data["Price per Sqft (INR)"].mean()
    city_avg_price = city_data["Price per Sqft (INR)"].mean()

    state_median_sale = state_data["Estimated Sale Price (INR)"].median()
    city_median_sale = city_data["Estimated Sale Price (INR)"].median()

    state_rental_yield = state_data["Rental Yield (%)"].mean()
    city_rental_yield = city_data["Rental Yield (%)"].mean()

    state_score = state_data["Buyer Attraction Score (1-10)"].mean()
    city_score = city_data["Buyer Attraction Score (1-10)"].mean()

    comparison_df = pd.DataFrame({
        "Metric": [
            "Average Price per Sqft",
            "Median Sale Price",
            "Average Rental Yield",
            "Buyer Attraction Score",
            "Property Count"
        ],
        "State Level": [
            round(state_avg_price, 2),
            round(state_median_sale, 2),
            round(state_rental_yield, 2),
            round(state_score, 2),
            len(state_data)
        ],
        "City Level": [
            round(city_avg_price, 2),
            round(city_median_sale, 2),
            round(city_rental_yield, 2),
            round(city_score, 2),
            len(city_data)
        ]
    })

    st.dataframe(comparison_df, use_container_width=True)

    st.bar_chart(
        comparison_df.set_index("Metric")[["State Level", "City Level"]]
    )

    if city_avg_price > state_avg_price:
        st.success(f"{selected_city} has a higher average price per sqft than {selected_state}.")
    else:
        st.info(f"{selected_city} is more affordable compared to the state average.")
