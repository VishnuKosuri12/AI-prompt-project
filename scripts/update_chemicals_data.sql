-- Update chemicals table structure and data for ChemTrack application

-- Connect to the database
\c chemtrack

-- 1. Alter the chemicals table to add new columns
--ALTER TABLE chemicals 
--ADD COLUMN chemical_description TEXT,
--ADD COLUMN cas_number VARCHAR(20),
--ADD COLUMN chemical_formula VARCHAR(50),
--ADD COLUMN molecular_weight DECIMAL(10,4),
--ADD COLUMN physical_state VARCHAR(20),
--ADD COLUMN signal_word VARCHAR(20),
--ADD COLUMN hazard_classification TEXT,
--ADD COLUMN sds_link TEXT;

-- 2. Delete existing chemicals (they will be replaced with more comprehensive data)
TRUNCATE chemicals CASCADE;
-- Reset the chemicals id sequence
ALTER SEQUENCE chemicals_id_seq RESTART WITH 1;
-- Also clear inventory as we'll regenerate it
TRUNCATE inventory CASCADE;
-- Reset the inventory id sequence
ALTER SEQUENCE inventory_id_seq RESTART WITH 1;

-- 3. Insert new chemical data with all fields populated
INSERT INTO chemicals (name, unit_of_measure, chemical_description, cas_number, chemical_formula, molecular_weight, physical_state, signal_word, hazard_classification, sds_link) VALUES
('Acetone', 'L', 'Clear, colorless, volatile liquid with a characteristic sweet odor. Used as a solvent.', '67-64-1', 'C3H6O', 58.0800, 'Liquid', 'Danger', 'Flammable Liquid Category 2, Eye Irritation Category 2A, STOT SE Category 3', 'https://www.sigmaaldrich.com/US/en/sds/sial/179124'),
('Ethanol', 'L', 'Clear, colorless liquid with a wine-like odor. Common alcohol found in beverages.', '64-17-5', 'C2H6O', 46.0700, 'Liquid', 'Danger', 'Flammable Liquid Category 2, Eye Irritation Category 2A', 'https://www.sigmaaldrich.com/US/en/sds/sial/459836'),
('Methanol', 'L', 'Clear, colorless, volatile liquid with a mild alcoholic odor. Highly toxic alcohol.', '67-56-1', 'CH4O', 32.0400, 'Liquid', 'Danger', 'Flammable Liquid Category 2, Acute Toxicity Category 3, STOT SE Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/179337'),
('Hydrochloric Acid', 'L', 'Clear to slightly yellow aqueous solution with pungent odor. Strong mineral acid.', '7647-01-0', 'HCl', 36.4600, 'Liquid', 'Danger', 'Skin Corrosion Category 1B, STOT SE Category 3', 'https://www.sigmaaldrich.com/US/en/sds/sial/320331'),
('Sodium Hydroxide', 'kg', 'White, odorless pellets or flakes. Strong base used in many applications.', '1310-73-2', 'NaOH', 40.0000, 'Solid', 'Danger', 'Skin Corrosion Category 1A, Eye Damage Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/306576'),
('Sulfuric Acid', 'L', 'Clear, colorless, odorless, viscous liquid. Strong mineral acid.', '7664-93-9', 'H2SO4', 98.0800, 'Liquid', 'Danger', 'Skin Corrosion Category 1A, Eye Damage Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/258105'),
('Toluene', 'L', 'Clear, colorless liquid with a sweet, pungent odor. Common aromatic solvent.', '108-88-3', 'C7H8', 92.1400, 'Liquid', 'Danger', 'Flammable Liquid Category 2, Skin Irritation Category 2, Repr. Category 2, STOT SE Category 3, STOT RE Category 2, Asp. Toxicity Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/179418'),
('Chloroform', 'L', 'Clear, colorless, volatile liquid with an ethereal odor. Used as a solvent.', '67-66-3', 'CHCl3', 119.3800, 'Liquid', 'Danger', 'Acute Toxicity Category 4, Skin Irritation Category 2, Eye Irritation Category 2A, Carc. Category 2, STOT RE Category 2', 'https://www.sigmaaldrich.com/US/en/sds/sial/372978'),
('Acetic Acid', 'L', 'Clear, colorless liquid with a pungent, vinegar-like odor. Carboxylic acid.', '64-19-7', 'C2H4O2', 60.0500, 'Liquid', 'Danger', 'Flammable Liquid Category 3, Skin Corrosion Category 1A', 'https://www.sigmaaldrich.com/US/en/sds/sial/695092'),
('Hydrogen Peroxide', 'L', 'Clear, colorless liquid with a slightly sharp odor. Strong oxidizer.', '7722-84-1', 'H2O2', 34.0147, 'Liquid', 'Danger', 'Oxidizing Liquid Category 1, Acute Toxicity Category 4, Skin Corrosion Category 1A', 'https://www.sigmaaldrich.com/US/en/sds/sial/216763'),
('Benzene', 'L', 'Clear, colorless, highly flammable liquid with an aromatic odor.', '71-43-2', 'C6H6', 78.1100, 'Liquid', 'Danger', 'Flammable Liquid Category 2, Skin Irritation Category 2, Eye Irritation Category 2, Muta. Category 1B, Carc. Category 1A, STOT RE Category 1, Asp. Toxicity Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/270709'),
('Hexane', 'L', 'Clear, colorless, volatile liquid with a slight gasoline-like odor.', '110-54-3', 'C6H14', 86.1800, 'Liquid', 'Danger', 'Flammable Liquid Category 2, Skin Irritation Category 2, Repr. Category 2, STOT SE Category 3, STOT RE Category 2, Asp. Toxicity Category 1, Aquatic Chronic Category 2', 'https://www.sigmaaldrich.com/US/en/sds/sial/270504'),
('Isopropyl Alcohol', 'L', 'Clear, colorless liquid with a slight alcohol-like odor. Common disinfectant.', '67-63-0', 'C3H8O', 60.1000, 'Liquid', 'Danger', 'Flammable Liquid Category 2, Eye Irritation Category 2A, STOT SE Category 3', 'https://www.sigmaaldrich.com/US/en/sds/sial/190764'),
('Formaldehyde', 'L', 'Clear, colorless solution with a pungent, suffocating odor.', '50-00-0', 'CH2O', 30.0300, 'Liquid', 'Danger', 'Acute Toxicity Category 3, Skin Corrosion Category 1B, Skin Sens. Category 1, Muta. Category 2, Carc. Category 1B, STOT SE Category 3', 'https://www.sigmaaldrich.com/US/en/sds/sial/252549'),
('Xylene', 'L', 'Clear, colorless liquid with an aromatic odor. Mixture of isomers.', '1330-20-7', 'C8H10', 106.1700, 'Liquid', 'Warning', 'Flammable Liquid Category 3, Acute Toxicity Category 4, Skin Irritation Category 2', 'https://www.sigmaaldrich.com/US/en/sds/sial/214736'),
('Nitric Acid', 'L', 'Clear to yellowish liquid with a characteristic choking odor. Strong oxidizer.', '7697-37-2', 'HNO3', 63.0100, 'Liquid', 'Danger', 'Oxidizing Liquid Category 3, Skin Corrosion Category 1A, Eye Damage Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/438073'),
('Ammonia Solution', 'L', 'Clear, colorless solution with a pungent, suffocating odor.', '1336-21-6', 'NH4OH', 35.0500, 'Liquid', 'Danger', 'Skin Corrosion Category 1B, Eye Damage Category 1, STOT SE Category 3, Aquatic Acute Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/318612'),
('Phosphoric Acid', 'L', 'Clear, colorless, odorless, viscous liquid. Used in many applications.', '7664-38-2', 'H3PO4', 98.0000, 'Liquid', 'Danger', 'Skin Corrosion Category 1B, Eye Damage Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/345245'),
('Dimethyl Sulfoxide', 'L', 'Clear, colorless, hygroscopic liquid with a characteristic odor.', '67-68-5', 'C2H6OS', 78.1300, 'Liquid', 'Warning', 'Skin Irritation Category 2, Eye Irritation Category 2A', 'https://www.sigmaaldrich.com/US/en/sds/sial/472301'),
('Ethyl Acetate', 'L', 'Clear, colorless liquid with a sweet, fruity odor. Common solvent.', '141-78-6', 'C4H8O2', 88.1100, 'Liquid', 'Danger', 'Flammable Liquid Category 2, Eye Irritation Category 2A, STOT SE Category 3', 'https://www.sigmaaldrich.com/US/en/sds/sial/270989'),
('Diethyl Ether', 'L', 'Clear, colorless, highly volatile liquid with a sweet, ethereal odor.', '60-29-7', 'C4H10O', 74.1200, 'Liquid', 'Danger', 'Flammable Liquid Category 1, Acute Toxicity Category 4, STOT SE Category 3', 'https://www.sigmaaldrich.com/US/en/sds/sial/296082'),
('Potassium Hydroxide', 'kg', 'White or slightly yellow deliquescent pellets or flakes. Strong base.', '1310-58-3', 'KOH', 56.1100, 'Solid', 'Danger', 'Acute Toxicity Category 4, Skin Corrosion Category 1A, Eye Damage Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/221473'),
('Dichloromethane', 'L', 'Clear, colorless, volatile liquid with a mild, sweet odor. Common solvent.', '75-09-2', 'CH2Cl2', 84.9300, 'Liquid', 'Warning', 'Skin Irritation Category 2, Eye Irritation Category 2A, Carc. Category 2, STOT SE Category 3, STOT RE Category 2', 'https://www.sigmaaldrich.com/US/en/sds/sial/270997'),
('Ammonium Hydroxide', 'L', 'Clear, colorless solution with a strong, pungent odor. Basic solution.', '1336-21-6', 'NH4OH', 35.0500, 'Liquid', 'Danger', 'Skin Corrosion Category 1B, Eye Damage Category 1, STOT SE Category 3, Aquatic Acute Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/318612'),
('Tetrahydrofuran', 'L', 'Clear, colorless liquid with an ethereal odor. Heterocyclic compound.', '109-99-9', 'C4H8O', 72.1100, 'Liquid', 'Danger', 'Flammable Liquid Category 2, Eye Irritation Category 2A, Carc. Category 2, STOT SE Category 3', 'https://www.sigmaaldrich.com/US/en/sds/sial/186562'),
('Acetonitrile', 'L', 'Clear, colorless liquid with an ethereal, somewhat sweet odor.', '75-05-8', 'C2H3N', 41.0500, 'Liquid', 'Danger', 'Flammable Liquid Category 2, Acute Toxicity Category 4, Eye Irritation Category 2A', 'https://www.sigmaaldrich.com/US/en/sds/sial/271004'),
('Glacial Acetic Acid', 'L', 'Clear, colorless liquid with a strong, pungent vinegar-like odor.', '64-19-7', 'C2H4O2', 60.0500, 'Liquid', 'Danger', 'Flammable Liquid Category 3, Skin Corrosion Category 1A, Eye Damage Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/695092'),
('Sodium Chloride', 'kg', 'White crystalline solid with a characteristic salty taste. Common salt.', '7647-14-5', 'NaCl', 58.4400, 'Solid', 'Warning', 'Eye Irritation Category 2B', 'https://www.sigmaaldrich.com/US/en/sds/sial/s9888'),
('Calcium Chloride', 'kg', 'White, deliquescent solid with various applications.', '10043-52-4', 'CaCl2', 110.9800, 'Solid', 'Warning', 'Eye Irritation Category 2A', 'https://www.sigmaaldrich.com/US/en/sds/sial/c1016'),
('Potassium Chloride', 'kg', 'White crystalline solid used in various applications.', '7447-40-7', 'KCl', 74.5500, 'Solid', 'Not classified', 'Not classified as hazardous', 'https://www.sigmaaldrich.com/US/en/sds/sial/p9333'),
('Aluminum Chloride', 'kg', 'White to pale yellow crystalline solid. Lewis acid used as catalyst.', '7446-70-0', 'AlCl3', 133.3400, 'Solid', 'Danger', 'Skin Corrosion Category 1B, STOT SE Category 3', 'https://www.sigmaaldrich.com/US/en/sds/aldrich/563919'),
('Sodium Bicarbonate', 'kg', 'White crystalline powder. Common baking soda with many applications.', '144-55-8', 'NaHCO3', 84.0100, 'Solid', 'Not classified', 'Not classified as hazardous', 'https://www.sigmaaldrich.com/US/en/sds/sial/s6014'),
('Iron(III) Chloride', 'kg', 'Brown-black solid that is highly deliquescent. Used in various applications.', '7705-08-0', 'FeCl3', 162.2000, 'Solid', 'Danger', 'Acute Toxicity Category 4, Skin Corrosion Category 1B, Eye Damage Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/236489'),
('Magnesium Sulfate', 'kg', 'White crystalline solid with various applications. Common as Epsom salt.', '7487-88-9', 'MgSO4', 120.3700, 'Solid', 'Not classified', 'Not classified as hazardous', 'https://www.sigmaaldrich.com/US/en/sds/sial/m7506'),
('Copper Sulfate', 'kg', 'Blue crystalline solid used in many applications.', '7758-98-7', 'CuSO4', 159.6100, 'Solid', 'Warning', 'Acute Toxicity Category 4, Skin Irritation Category 2, Eye Irritation Category 2A, Aquatic Acute Category 1, Aquatic Chronic Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/209198'),
('Zinc Chloride', 'kg', 'White crystalline solid that is highly deliquescent.', '7646-85-7', 'ZnCl2', 136.2900, 'Solid', 'Danger', 'Acute Toxicity Category 4, Skin Corrosion Category 1B, Aquatic Acute Category 1, Aquatic Chronic Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/229997'),
('Sodium Carbonate', 'kg', 'White crystalline solid. Common washing soda with many applications.', '497-19-8', 'Na2CO3', 105.9900, 'Solid', 'Warning', 'Eye Irritation Category 2A', 'https://www.sigmaaldrich.com/US/en/sds/sial/s7795'),
('Ammonium Chloride', 'kg', 'White crystalline solid with a characteristic odor.', '12125-02-9', 'NH4Cl', 53.4900, 'Solid', 'Warning', 'Acute Toxicity Category 4, Eye Irritation Category 2A', 'https://www.sigmaaldrich.com/US/en/sds/sial/a9434'),
('Silver Nitrate', 'kg', 'Colorless crystalline solid that turns gray or black when exposed to light.', '7761-88-8', 'AgNO3', 169.8700, 'Solid', 'Danger', 'Oxidizing Solid Category 2, Skin Corrosion Category 1B, Aquatic Acute Category 1, Aquatic Chronic Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/209139'),
('Potassium Permanganate', 'kg', 'Purple-bronze crystalline solid. Strong oxidizer with many applications.', '7722-64-7', 'KMnO4', 158.0340, 'Solid', 'Danger', 'Oxidizing Solid Category 2, Acute Toxicity Category 4, Aquatic Acute Category 1, Aquatic Chronic Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/223468'),
('Iodine', 'kg', 'Bluish-black crystals with a metallic luster and characteristic odor.', '7553-56-2', 'I2', 253.8000, 'Solid', 'Danger', 'Acute Toxicity Category 4, Skin Corrosion Category 2, Eye Damage Category 2, STOT SE Category 3, Aquatic Acute Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/207772'),
('Urea', 'kg', 'White crystalline solid with a slight ammonia odor. Used in many applications.', '57-13-6', 'CH4N2O', 60.0600, 'Solid', 'Not classified', 'Not classified as hazardous', 'https://www.sigmaaldrich.com/US/en/sds/sial/u5128'),
('Glycerol', 'L', 'Clear, colorless, viscous liquid with a sweet taste. Used in many applications.', '56-81-5', 'C3H8O3', 92.0900, 'Liquid', 'Not classified', 'Not classified as hazardous', 'https://www.sigmaaldrich.com/US/en/sds/sial/g9012'),
('Sodium Phosphate', 'kg', 'White crystalline solid used in various applications.', '7601-54-9', 'Na3PO4', 163.9400, 'Solid', 'Warning', 'Skin Irritation Category 2, Eye Irritation Category 2A, STOT SE Category 3', 'https://www.sigmaaldrich.com/US/en/sds/sial/342483'),
('Ammonium Nitrate', 'kg', 'White crystalline solid used primarily as a fertilizer.', '6484-52-2', 'NH4NO3', 80.0400, 'Solid', 'Warning', 'Oxidizing Solid Category 3, Eye Irritation Category 2A', 'https://www.sigmaaldrich.com/US/en/sds/sial/221244'),
('Boric Acid', 'kg', 'White crystalline solid used in many applications.', '10043-35-3', 'H3BO3', 61.8300, 'Solid', 'Warning', 'Reproductive Toxicity Category 1B', 'https://www.sigmaaldrich.com/US/en/sds/sial/b6768'),
('Potassium Iodide', 'kg', 'White crystalline solid with various applications.', '7681-11-0', 'KI', 166.0000, 'Solid', 'Warning', 'Skin Irritation Category 2, Eye Irritation Category 2A, STOT SE Category 3', 'https://www.sigmaaldrich.com/US/en/sds/sial/793582'),
('Lithium Chloride', 'kg', 'White deliquescent crystalline solid with various applications.', '7447-41-8', 'LiCl', 42.3900, 'Solid', 'Warning', 'Acute Toxicity Category 4, Skin Irritation Category 2, Eye Irritation Category 2A', 'https://www.sigmaaldrich.com/US/en/sds/sial/203637'),
('Magnesium Chloride', 'kg', 'White or colorless crystalline solid with various applications.', '7786-30-3', 'MgCl2', 95.2100, 'Solid', 'Not classified', 'Not classified as hazardous', 'https://www.sigmaaldrich.com/US/en/sds/sial/m8266'),
('Phenol', 'kg', 'White to colorless crystalline solid with characteristic sweet, medicinal odor.', '108-95-2', 'C6H6O', 94.1100, 'Solid', 'Danger', 'Acute Toxicity Category 3, Skin Corrosion Category 1B, Muta. Category 2, STOT RE Category 2', 'https://www.sigmaaldrich.com/US/en/sds/sial/p1037'),
('Carbon Tetrachloride', 'L', 'Clear, colorless, dense liquid with a characteristic sweet odor.', '56-23-5', 'CCl4', 153.8200, 'Liquid', 'Danger', 'Acute Toxicity Category 3, STOT RE Category 1, Aquatic Chronic Category 3, Ozone Category 1', 'https://www.sigmaaldrich.com/US/en/sds/sial/289116');

-- 4. Now randomly assign inventory to all locations ensuring 5-20 chemicals per location
-- First, determine the number of chemicals to assign to each location in the specified range
WITH location_assignments AS (
  SELECT 
    location_id,
    -- Random number between 5 and 20
    FLOOR(random() * 16 + 5)::INTEGER AS num_chemicals
  FROM 
    locations
)
-- Insert inventory assignments for each location
INSERT INTO inventory (chemical_id, quantity, reorder_quantity, location_id)
WITH inventory_data AS (
  SELECT 
    chemicals.id AS chemical_id,
    -- Random quantity between 1.0 and 10.0
    ROUND((random() * 9 + 1)::numeric, 1) AS quantity,
    la.location_id
  FROM 
    location_assignments la
  CROSS JOIN LATERAL (
    SELECT id 
    FROM chemicals 
    ORDER BY random() 
    LIMIT la.num_chemicals
  ) AS chemicals
)
SELECT
  chemical_id,
  quantity,
  -- Random reorder quantity between 0.5 and quantity/2
  ROUND((random() * (quantity/2 - 0.5) + 0.5)::numeric, 1) AS reorder_quantity,
  location_id
FROM 
  inventory_data;

-- Verify data was properly inserted
SELECT 'Number of chemicals created:' AS info, COUNT(*) AS value FROM chemicals;
SELECT 'Number of inventory items created:' AS info, COUNT(*) AS value FROM inventory;
SELECT 'Minimum chemicals per location:' AS info, MIN(count) AS value FROM (SELECT location_id, COUNT(*) FROM inventory GROUP BY location_id) AS counts;
SELECT 'Maximum chemicals per location:' AS info, MAX(count) AS value FROM (SELECT location_id, COUNT(*) FROM inventory GROUP BY location_id) AS counts;
