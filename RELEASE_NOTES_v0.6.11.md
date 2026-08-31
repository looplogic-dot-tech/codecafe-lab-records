# Registros Clínicos by CodeCafe v0.6.11 — Branding + Weight Readings

- Visible product identity changed to **Registros Clínicos** with **by CodeCafe** as secondary branding (English UI: Clinical Records).
- Internal package IDs and legacy data paths remain `codecafe-lab-records` / `CodeCafe Lab Records` so upgrades preserve existing records.
- Daily Measurements now supports weight in kg or lb.
- Weight is normalized to kilograms for trends and cross-unit continuity.
- Adds latest-weight card, weight history entries, weight trend graph and doctor-view weight entries.
- Existing blood-pressure and glucose records are migrated in place without deletion.
- Keeps the v0.6.10 native-print and safe RPM staging fixes.
