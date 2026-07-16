### The ERP Maintenance Matching Agent (Data Deduplication)

* **The Business Pain:** A property risk management company conducts 4,000 risk inspections a year, logging over 70,000 individual safety hazards. They integrate their digital portal with real estate ERP and property management platforms (like Retta or Hausvise). 
  
  When they log a hazard (e.g., *"Savunpoistoluukku / Smoke extraction hatch failed inspection"*), that building's housing manager might already have a ticket open for it in their own ERP, or a maintenance company might have already fixed it. Matching unstructured text fields across two completely different corporate databases to see if a hazard is already being handled is impossible for standard scripts.
* **The AI Agent's Job:** A lightweight semantic matching agent sits between the company's data pipeline and incoming customer ERP webhooks. It evaluates the semantic meaning of text fields rather than looking for exact keyword matches. 
  
  It can read the company's ticket (*"Basement door warp prevents flush seal"*) and accurately match it to the property manager’s internal ticket (*"Kellarin ovi ei sulkeudu kunnolla"*).
* **The Downstream Script:** If a semantic match probability is above 90%, the script automatically link-matches the entries, updates the company's real-time safety index, and closes the loophole without requiring a human operator to cross-check dashboards.
* **The Commercial Value:** Eliminates massive communication friction between property managers (*isännöitsijät*) and the company, preventing redundant service calls.
