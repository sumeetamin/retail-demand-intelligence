# Retail replenishment shadow-pilot protocol

Status: **planned, not run**. This document is a preparation artifact; it is not evidence of customer use.

## Goal

Test whether the retail demand and inventory planner can improve replenishment decisions for an authorized retailer using its own recent sales, inventory and supplier lead-time data.

## Participants and authorization

- One retailer's inventory owner and one data owner approve the pilot and the permitted fields.
- Participation is opt-in. No messages have been sent and no partner has been recruited.
- Use aggregated SKU-day data only. Exclude customer names, IDs, addresses, payment data, supplier contact details and confidential contract text.
- Keep source data in the retailer-approved environment; do not commit raw data, secrets or row-level outputs to GitHub.
- The retailer reviews every proposed order. The system stays in shadow mode and cannot place orders.

## Design

- Duration: 4 weeks after a 2-week data-quality and baseline period.
- Scope: 5–20 SKUs selected before outcomes are reviewed; include fast, intermittent and low-volume items when the partner has enough history.
- Inputs: date, pseudonymous SKU, units sold, available inventory, lead time, order quantity and stockout indicator.
- Baselines: the retailer's current policy and the public-data seasonal policy, scored on the same dates and lead times.
- Freeze the SKU set, cost assumptions, service target, forecast horizon and decision rule before the measurement window.
- Record daily forecasts and recommended reorder quantities without sending orders.

## Outcomes

Primary: realized inventory cost per SKU-week using the partner-approved holding and stockout costs.

Secondary: stockout days, fill rate, excess inventory, forecast MAE/WAPE, recommendation acceptance rate, and inventory-owner usefulness feedback.

Report the paired difference versus the current policy, sample size, uncertainty interval and missing-data rate. Do not call results causal unless the design supports a causal comparison. Do not generalize beyond the participating retailer and period.

## Stop conditions

Stop data processing if authorization is withdrawn, unexpected personal/confidential fields appear, the frozen cost assumptions are disputed, or shadow recommendations could affect a live order. Delete partner data and derived row-level files on the agreed schedule.

## Evidence required before publication

Written permission for the specific aggregate outputs; a data dictionary and source period; frozen protocol and costs; paired policy results with uncertainty; completeness and QA checks; participant feedback; and an explicit limitations statement. Publish only approved aggregate results. Do not publish names, raw rows, operationally sensitive details or an unsupported impact claim.
