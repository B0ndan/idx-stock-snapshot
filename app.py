import pandas as pd
import streamlit as st
from sectors import SectorsError, get_company_overview


@st.cache_data(ttl=3600)
def get_cached_company_overview(ticker):
	return get_company_overview(ticker)

st.set_page_config(page_title="Investment Goal Calculator", page_icon="📈")

st.title("Investment Goal Calculator")
st.write("See how regular monthly savings could grow over time.")

ticker = st.text_input("IDX ticker", value="BBCA")
company = None
try:
	company = get_cached_company_overview(ticker)
except SectorsError as error:
	st.warning(str(error))

if company:
	st.header(company.get("company_name", "Company details"))
	last_close_price = company.get("last_close_price")
	if last_close_price is not None:
		formatted_price = "Rp {:,.0f}".format(last_close_price).replace(",", ".")
	else:
		formatted_price = "Unavailable"
	st.write(
		"Sector: {} | Sub-sector: {} | Last close: {}".format(
			company.get("sector", "Unavailable"),
			company.get("sub_sector", "Unavailable"),
			formatted_price,
		)
	)

starting_amount = st.number_input(
	"Starting amount (Rp)",
	min_value=0,
	max_value=100_000_000_000,
	value=0,
	step=100_000,
	format="%d",
)
monthly_saving = st.number_input(
	"Monthly saving (Rp)",
	min_value=0,
	max_value=100_000_000_000,
	value=1_000_000,
	step=100_000,
	format="%d",
)
years = st.slider("Number of years", min_value=1, max_value=50, value=10)
annual_return = st.number_input(
	"Expected yearly return (%)",
	min_value=-50.0,
	max_value=100.0,
	value=8.0,
	step=0.5,
)

monthly_return = (1 + annual_return / 100) ** (1 / 12) - 1
balance = float(starting_amount)
yearly_balances = [{"Year": 0, "Total savings": balance}]

for month in range(1, years * 12 + 1):
	balance *= 1 + monthly_return
	balance += monthly_saving
	if month % 12 == 0:
		yearly_balances.append({"Year": month // 12, "Total savings": round(balance)})

st.subheader("Your estimated final amount")
st.metric("After {} years".format(years), "Rp {:,.0f}".format(balance).replace(",", "."))

if company and last_close_price is not None and last_close_price > 0:
	lot_price = last_close_price * 100
	lots = int(monthly_saving // lot_price)
	leftover = monthly_saving - lots * lot_price
	st.write("Your monthly saving buys {} lots of this stock.".format(lots))
	st.write("Left over: Rp {:,.0f}".format(leftover).replace(",", "."))
elif company:
	st.warning("The latest close price is unavailable, so the lot estimate cannot be calculated.")

st.subheader("Growth year by year")
chart_data = pd.DataFrame(yearly_balances).set_index("Year")
st.line_chart(chart_data, y="Total savings")

st.caption(
	"This estimate assumes a constant return compounded monthly, with savings added at each month-end. "
	"Actual returns vary. For learning and planning only, not investment advice."
)
st.image(
	"https://upload.wikimedia.org/wikipedia/commons/5/57/Gedung-bursa-efek-1_%281%29.jpg",
	width="stretch",
)
st.caption(
	"Photo: [Bursa Efek Indonesia, CC BY-SA 4.0]("
	"https://commons.wikimedia.org/wiki/File:Gedung-bursa-efek-1_(1).jpg)"
)
st.caption("vitto")

with st.expander("Raw company data"):
	if company:
		st.json(company)
	else:
		st.info("Company data is not available until a valid ticker is loaded.")
