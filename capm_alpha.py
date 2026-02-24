"""
CAPM & Fama-French Alpha Calculator

Takes a weighted portfolio of stocks/ETFs, downloads historical returns,
runs both a single-factor CAPM and a Fama-French 5-factor regression,
and reports alpha, factor loadings, and related statistics.

Usage:
    python capm_alpha.py AVUV:0.40 VT:0.35 AVDV:0.25
    python capm_alpha.py AVUV:0.40 VT:0.35 AVDV:0.25 --period max --factors 3
"""

import argparse
import sys

import numpy as np
import pandas as pd
import statsmodels.api as sm
import yfinance as yf


def parse_portfolio(holdings: list[str]) -> dict[str, float]:
    """Parse 'TICKER:WEIGHT' strings into a dict. Weights must sum to ~1."""
    portfolio = {}
    for item in holdings:
        try:
            ticker, weight = item.split(":")
            portfolio[ticker.upper()] = float(weight)
        except ValueError:
            sys.exit(f"Error: '{item}' is not in TICKER:WEIGHT format (e.g. AAPL:0.40)")

    total = sum(portfolio.values())
    if not np.isclose(total, 1.0, atol=0.01):
        sys.exit(f"Error: weights sum to {total:.4f}, must sum to 1.0")

    return portfolio


def fetch_prices(tickers: list[str], period: str, interval: str) -> pd.DataFrame:
    """Download adjusted close prices for portfolio tickers."""
    print(f"Downloading price data for {', '.join(tickers)}  (period={period}, interval={interval}) ...")
    data = yf.download(tickers, period=period, interval=interval, auto_adjust=True)

    if data.empty:
        sys.exit("Error: no data returned from Yahoo Finance.")

    if isinstance(data.columns, pd.MultiIndex):
        prices = data["Close"]
    else:
        prices = data[["Close"]].rename(columns={"Close": tickers[0]})

    prices = prices.dropna()

    missing = [t for t in tickers if t not in prices.columns]
    if missing:
        sys.exit(f"Error: no price data for {', '.join(missing)}")

    return prices


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Compute simple periodic returns from a price DataFrame."""
    return prices.pct_change().dropna()


def fetch_ff_factors(num_factors: int, start_date: str) -> pd.DataFrame:
    """Download global Fama-French factor data from Kenneth French's data library."""
    import io
    import urllib.request
    import zipfile

    dataset = {
        3: "Developed_3_Factors",
        5: "Developed_5_Factors",
    }[num_factors]

    print(f"Downloading Fama-French {num_factors}-factor (global) data ...")
    url = f"https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/{dataset}_CSV.zip"
    resp = urllib.request.urlopen(url)
    z = zipfile.ZipFile(io.BytesIO(resp.read()))
    csv_name = [n for n in z.namelist() if n.endswith(".csv")][0]

    with z.open(csv_name) as f:
        raw = f.read().decode("utf-8")

    # Find the header line and extract the monthly data (stop at annual section)
    lines = raw.split("\n")
    header_idx = next(i for i, line in enumerate(lines) if "Mkt-RF" in line)
    data_lines = [lines[header_idx]]
    for line in lines[header_idx + 1 :]:
        stripped = line.strip()
        if not stripped or not stripped[0].isdigit():
            break
        data_lines.append(line)

    ff = pd.read_csv(io.StringIO("\n".join(data_lines)), index_col=0)
    ff.index = ff.index.astype(str).str.strip()
    ff.index = pd.to_datetime(ff.index, format="%Y%m") + pd.offsets.MonthEnd(0)

    # Filter to start_date
    ff = ff[ff.index >= pd.to_datetime(start_date)]

    # Returns come in percent — convert to decimal
    ff = ff / 100.0

    return ff


def run_capm(portfolio_returns: pd.Series, market_returns: pd.Series, rf_rate: float, periods_per_year: int):
    """
    Run CAPM regression:  R_p - R_f = alpha + beta * (R_m - R_f) + epsilon
    """
    rf_per_period = (1 + rf_rate) ** (1 / periods_per_year) - 1

    excess_portfolio = portfolio_returns - rf_per_period
    excess_market = market_returns - rf_per_period

    X = sm.add_constant(excess_market)
    model = sm.OLS(excess_portfolio, X).fit()

    alpha_per_period = model.params.iloc[0]
    beta = model.params.iloc[1]
    alpha_annualized = (1 + alpha_per_period) ** periods_per_year - 1

    return {
        "alpha_per_period": alpha_per_period,
        "alpha_annualized": alpha_annualized,
        "beta": beta,
        "r_squared": model.rsquared,
        "model": model,
    }


def run_fama_french(portfolio_returns: pd.Series, ff_factors: pd.DataFrame, periods_per_year: int):
    """
    Run Fama-French regression:
      R_p - R_f = alpha + b1*MktRF + b2*SMB + b3*HML [+ b4*RMW + b5*CMA] + epsilon
    """
    # Normalize both indices to month-end for alignment
    port = portfolio_returns.copy()
    port.index = port.index.to_period("M").to_timestamp("M")
    ff = ff_factors.copy()
    if hasattr(ff.index, 'to_period'):
        ff.index = ff.index.to_period("M").to_timestamp("M")

    combined = pd.concat([port, ff], axis=1, join="inner").dropna()
    port_ret = combined.iloc[:, 0]
    factors = combined.iloc[:, 1:]

    excess_portfolio = port_ret - factors["RF"]
    factor_cols = [c for c in factors.columns if c != "RF"]
    X = sm.add_constant(factors[factor_cols])
    model = sm.OLS(excess_portfolio, X).fit()

    alpha_per_period = model.params["const"]
    alpha_annualized = (1 + alpha_per_period) ** periods_per_year - 1

    return {
        "alpha_per_period": alpha_per_period,
        "alpha_annualized": alpha_annualized,
        "factor_loadings": {col: model.params[col] for col in factor_cols},
        "r_squared": model.rsquared,
        "n_obs": int(model.nobs),
        "model": model,
    }


def periods_per_year_from_interval(interval: str) -> int:
    mapping = {"1d": 252, "1wk": 52, "1mo": 12, "3mo": 4}
    if interval not in mapping:
        sys.exit(f"Error: unsupported interval '{interval}'. Use one of {list(mapping.keys())}")
    return mapping[interval]


def main():
    parser = argparse.ArgumentParser(
        description="Calculate CAPM & Fama-French alpha for a weighted portfolio.",
        epilog="Example:  python capm_alpha.py AVUV:0.40 VT:0.35 AVDV:0.25",
    )
    parser.add_argument("holdings", nargs="+", help="TICKER:WEIGHT pairs (e.g. AAPL:0.40)")
    parser.add_argument("--benchmark", default="VT", help="Market benchmark for CAPM (default: VT)")
    parser.add_argument("--period", default="5y", help="Historical look-back period (default: 5y)")
    parser.add_argument("--interval", default="1mo", help="Return interval: 1d, 1wk, 1mo, 3mo (default: 1mo)")
    parser.add_argument("--rf", type=float, default=0.043, help="Annual risk-free rate for CAPM (default: 0.043)")
    parser.add_argument("--factors", type=int, default=5, choices=[3, 5], help="Fama-French 3 or 5 factors (default: 5)")
    args = parser.parse_args()

    if args.interval != "1mo":
        sys.exit("Error: Fama-French data is monthly only. Use --interval 1mo (the default).")

    portfolio = parse_portfolio(args.holdings)
    tickers = list(portfolio.keys())
    periods = periods_per_year_from_interval(args.interval)

    # Fetch prices for all tickers + benchmark
    all_tickers = list(set(tickers + [args.benchmark]))
    prices = fetch_prices(all_tickers, args.period, args.interval)
    returns = compute_returns(prices)

    weights = np.array([portfolio[t] for t in tickers])
    portfolio_returns = returns[tickers].dot(weights)
    portfolio_returns.name = "Portfolio"

    market_returns = returns[args.benchmark]

    # ── CAPM ──
    capm = run_capm(portfolio_returns, market_returns, args.rf, periods)

    # ── Fama-French ──
    start_date = returns.index.min().strftime("%Y-%m-%d")
    ff_factors = fetch_ff_factors(args.factors, start_date)
    ff = run_fama_french(portfolio_returns, ff_factors, periods)

    # ── Report ──
    port_annual = (1 + portfolio_returns.mean()) ** periods - 1
    mkt_annual = (1 + market_returns.mean()) ** periods - 1

    print("\n" + "=" * 60)
    print("  Portfolio Alpha Analysis")
    print("=" * 60)
    print(f"  Period:          {args.period}  ({args.interval} returns)")
    print(f"  Benchmark:       {args.benchmark}")
    print(f"  Risk-free rate:  {args.rf:.2%}  (CAPM only)")
    print("-" * 60)
    print("  Portfolio holdings:")
    for t, w in portfolio.items():
        print(f"    {t:8s}  {w:6.1%}")
    print("-" * 60)
    print(f"  Portfolio ann. return:   {port_annual:>8.2%}")
    print(f"  Benchmark ann. return:   {mkt_annual:>8.2%}")

    # CAPM section
    print("\n" + "-" * 60)
    print("  CAPM (single-factor)")
    print("-" * 60)
    print(f"  Beta:                    {capm['beta']:>8.3f}")
    print(f"  Alpha (annualized):      {capm['alpha_annualized']:>8.2%}")
    print(f"  R-squared:               {capm['r_squared']:>8.3f}")

    # Fama-French section
    print("\n" + "-" * 60)
    print(f"  Fama-French {args.factors}-Factor")
    print("-" * 60)
    print(f"  Alpha (annualized):      {ff['alpha_annualized']:>8.2%}")
    p_alpha = ff["model"].pvalues["const"]
    print(f"  Alpha p-value:           {p_alpha:>8.4f}")
    print(f"  R-squared:               {ff['r_squared']:>8.3f}")
    print(f"  Observations:            {ff['n_obs']:>8d}")
    print()
    print("  Factor loadings:")
    for factor, loading in ff["factor_loadings"].items():
        p_val = ff["model"].pvalues[factor]
        sig = "*" if p_val < 0.05 else " "
        print(f"    {factor:8s}  {loading:>+8.3f}   (p={p_val:.3f}) {sig}")
    print("=" * 60)

    print("\n--- CAPM OLS Summary ---")
    print(capm["model"].summary())

    print(f"\n--- Fama-French {args.factors}-Factor OLS Summary ---")
    print(ff["model"].summary())


if __name__ == "__main__":
    main()
