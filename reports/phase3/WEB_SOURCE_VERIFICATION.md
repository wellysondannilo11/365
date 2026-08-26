# WEB SOURCE VERIFICATION — GLOBAL FOOTBALL RESEARCH

This report records source capabilities verified on 2026-08-20. Verification is not the same as byte-level materialization.

## Football-Data.co.uk
The provider states that its historical archive contains 31+ seasons of results, 26+ seasons of betting odds and 26+ seasons of match statistics, with data available across multiple countries and divisions. It also describes pre-closing and closing odds sets for later seasons. Exact decision-time availability is not guaranteed by these CSV fields alone.

## DataHub EPL
The DataHub English Premier League dataset exposes stable season CSV resources, including season-2324.csv, and documents results, referee, shots, corners and cards. The dataset identifies Football-Data.co.uk as its source.

## StatsBomb Open Data
The official public repository provides competition/season match files plus event and lineup JSON and selected 360 data. It is suitable for football performance/event feature research but does not provide bookmaker odds.

## The Odds API
The official historical API documents timestamped bookmaker snapshots, with featured-market history from June 2020, 10-minute snapshots initially and 5-minute snapshots from September 2022; additional markets are available from May 2023. The API returns the closest snapshot equal to or earlier than the requested timestamp. Historical access is paid and requires credentials.

## Runtime acquisition status
The execution runtime could not resolve external hosts, so no new external bytes were promoted into the empirical dataset during this run. Web verification therefore remains source discovery, not processed evidence.
