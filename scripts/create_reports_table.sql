-- Create a table to store report definitions
CREATE TABLE IF NOT EXISTS reports (
  report_id SERIAL PRIMARY KEY,
  report_name VARCHAR(50) NOT NULL,
  sql_query   TEXT NOT NULL,
  parameters  JSON
);

-- Insert the first report: Inventory Totals
INSERT INTO reports (
  report_name,
  sql_query,
  parameters
) VALUES (
  'Inventory Totals',
  'SELECT
     c.name,
     c.chemical_description,
     SUM(i.quantity)       AS total_quantity,
     c.unit_of_measure
   FROM chemicals c
   JOIN inventory i
     ON c.id = i.id
   GROUP BY
     c.name,
     c.chemical_description,
     c.unit_of_measure
   ORDER BY c.name',
  '[]'
);
