-- =============================================================================
-- Home Maintenance Tracker - Seed Data
-- =============================================================================
-- Common maintenance tasks for a typical Kansas home.
-- Disable (SET active=0) anything that doesn't apply to your house.
-- Adjust frequency_days to taste.

-- =============================================================================
-- LOCATIONS (customize to your actual layout)
-- =============================================================================

INSERT INTO locations (name, notes) VALUES
    ('Interior - General',  'Whole-house items'),
    ('Kitchen',             NULL),
    ('Bathroom(s)',         NULL),
    ('Laundry Room',       NULL),
    ('Basement',           NULL),
    ('Attic',              NULL),
    ('Garage',             NULL),
    ('Exterior - General', NULL),
    ('Yard / Landscaping', NULL),
    ('Mechanical Room',    'Furnace, water heater, etc.');

-- =============================================================================
-- SCHEDULES
-- =============================================================================
-- asset_id is NULL for all seed schedules since you haven't added your specific
-- assets yet. Once you add your furnace, water heater, etc., you can update
-- these to link to the right asset.
--
-- frequency_days is approximate. Adjust based on your actual usage patterns.
--
-- impact values:
--   safety      — fire, CO, structural collapse, electrocution
--   protective  — prevents water/weather/pest damage to the house itself
--   efficiency  — saves energy or money, extends equipment life
--   cosmetic    — appearance only
--   comfort     — quality of life, cleanliness, convenience
-- =============================================================================

-- ─── MONTHLY (every 30 days) ─────────────────────────────────────────────────

INSERT INTO schedules (name, description, category, frequency_days, frequency_label, priority, impact, estimated_minutes, pro_recommended, notes) VALUES
('Replace HVAC air filter',
 'Check and replace the furnace/AC air filter. Cheaper fiberglass filters need monthly replacement; pleated MERV 8-11 filters can go 60-90 days. If you have pets, lean toward more frequent.',
 'HVAC', 30, 'Monthly', 'high', 'efficiency', 5, 0,
 'Buy filters in bulk. Common sizes: 16x25x1, 20x25x1. Check your existing filter for size printed on the frame.'),

('Test smoke and CO detectors',
 'Press the test button on each smoke detector and carbon monoxide detector. Replace batteries if the chirp is weak.',
 'Safety', 30, 'Monthly', 'critical', 'safety', 10, 0,
 'Detectors themselves should be replaced every 10 years. Check manufacture date on the back.'),

('Check water softener salt',
 'Inspect the brine tank and add salt if below half full. Kansas has hard water so this is important for protecting pipes and appliances.',
 'Plumbing', 30, 'Monthly', 'normal', 'protective', 5, 0,
 'Use evaporated salt pellets, not rock salt, for less residue.'),

('Run garbage disposal cleaning',
 'Run ice cubes through the disposal to clean the blades, then follow with citrus peels or baking soda + vinegar to deodorize.',
 'Plumbing', 30, 'Monthly', 'low', 'comfort', 5, 0, NULL),

('Check under sinks for leaks',
 'Quick visual inspection under kitchen and bathroom sinks. Look for moisture, drips, staining, or mold on the cabinet floor.',
 'Plumbing', 30, 'Monthly', 'normal', 'protective', 5, 0, NULL),

('Inspect and clean range hood filter',
 'Remove the metal mesh filter from your range hood and soak in hot water + degreaser or run through the dishwasher.',
 'Appliance', 30, 'Monthly', 'low', 'comfort', 15, 0,
 'If the filter is aluminum mesh, dishwasher is fine. If it''s charcoal/carbon, it needs replacement not cleaning.');

-- ─── QUARTERLY (every 90 days) ───────────────────────────────────────────────

INSERT INTO schedules (name, description, category, frequency_days, frequency_label, priority, impact, estimated_minutes, pro_recommended, notes) VALUES
('Clean dishwasher filter and interior',
 'Remove and rinse the bottom filter/screen. Run an empty hot cycle with a cup of white vinegar or a dishwasher cleaner tablet. Check spray arms for clogs.',
 'Appliance', 90, 'Quarterly', 'normal', 'comfort', 15, 0, NULL),

('Clean washing machine',
 'Run an empty hot cycle with washing machine cleaner or 2 cups white vinegar. Wipe door gasket (front-loader) or agitator area. Clean lint filter if applicable.',
 'Appliance', 90, 'Quarterly', 'normal', 'comfort', 10, 0,
 'Front-loaders: always leave the door cracked after use to prevent mold.'),

('Test garage door auto-reverse',
 'Place a 2x4 flat on the ground under the door. Close the door—it should reverse when it contacts the board. Also test the photo-eye sensors by blocking them while the door is closing.',
 'Safety', 90, 'Quarterly', 'high', 'safety', 10, 0, NULL),

('Check caulking in bathrooms',
 'Inspect caulk around tubs, showers, and sinks. Look for cracks, gaps, peeling, or discoloration. Re-caulk as needed to prevent water damage behind walls.',
 'Plumbing', 90, 'Quarterly', 'normal', 'protective', 15, 0,
 'Use 100% silicone caulk for wet areas, not latex.'),

('Exercise plumbing shutoff valves',
 'Turn each shutoff valve (toilets, sinks, washing machine, dishwasher) fully closed then fully open. This prevents them from seizing up so they actually work in an emergency.',
 'Plumbing', 90, 'Quarterly', 'normal', 'protective', 15, 0,
 'If a valve is very stiff, don''t force it—you might need to replace it. Note which ones are stiff.'),

('Test GFCI outlets',
 'Press the TEST button on each GFCI outlet (kitchens, bathrooms, garage, exterior). The outlet should lose power. Press RESET to restore. Replace any that don''t trip.',
 'Electrical', 90, 'Quarterly', 'high', 'safety', 10, 0, NULL),

('Flush drains preventatively',
 'Flush each drain (tubs, showers, bathroom sinks) with boiling water or enzyme drain cleaner to prevent slow buildup. Do NOT use chemical drain cleaners—they damage pipes.',
 'Plumbing', 90, 'Quarterly', 'low', 'comfort', 15, 0, NULL),

('Check and replace HVAC humidifier pad/filter',
 'If you have a whole-house humidifier on your furnace, check the evaporator pad. Replace if crusty with mineral buildup. Kansas hard water eats these faster.',
 'HVAC', 90, 'Quarterly', 'normal', 'comfort', 15, 0,
 'Skip this if you don''t have a whole-house humidifier. Set active=0.');

-- ─── TWICE YEARLY (every 180 days, spring + fall) ───────────────────────────

INSERT INTO schedules (name, description, category, frequency_days, frequency_label, season_hint, priority, impact, estimated_minutes, pro_recommended, notes) VALUES
('HVAC professional service',
 'Have a technician inspect and service the system. Spring: AC tune-up (refrigerant, coils, condensate drain). Fall: furnace tune-up (heat exchanger, burners, ignitor, flue).',
 'HVAC', 180, 'Twice yearly', 'spring,fall', 'high', 'efficiency', 60, 1,
 'Book early—HVAC companies get slammed right before the season starts. Typical cost $80-150 per visit.'),

('Clean gutters and downspouts',
 'Remove leaves and debris from all gutters. Flush with a hose to check flow. Make sure downspouts direct water at least 4-6 feet away from foundation.',
 'Exterior', 180, 'Twice yearly', 'spring,fall', 'high', 'protective', 60, 0,
 'Kansas thunderstorms + clogged gutters = foundation water problems. This one matters.'),

('Test sump pump',
 'Pour a bucket of water into the sump pit to trigger the float switch. Verify the pump activates and water drains. Check the discharge line for clogs.',
 'Plumbing', 180, 'Twice yearly', 'spring,fall', 'high', 'protective', 10, 0,
 'Skip if you don''t have a basement/sump. Consider a battery backup sump if you don''t have one—Kansas storms knock out power.'),

('Check weatherstripping on doors and windows',
 'Inspect weatherstripping on all exterior doors and windows. Close a dollar bill in the door—if you can pull it out easily, the seal is worn. Replace as needed.',
 'Exterior', 180, 'Twice yearly', 'spring,fall', 'normal', 'efficiency', 30, 0,
 'Foam tape is cheap but wears out fast. V-strip (vinyl or metal) lasts much longer.'),

('Check attic for issues',
 'Look for signs of water intrusion (stains, damp insulation), pest entry (droppings, nesting), and verify soffit vents aren''t blocked by insulation. Check that bathroom exhaust vents exit through the roof, not into the attic.',
 'Structural', 180, 'Twice yearly', 'spring,fall', 'normal', 'protective', 20, 0,
 'Best done when it''s not 110°F up there. Spring and late fall.'),

('Inspect foundation and grading',
 'Walk the perimeter and inspect foundation walls for new cracks. Check that soil grades away from the house (6 inches of drop over 10 feet). Fill in any spots where soil has settled toward the foundation.',
 'Structural', 180, 'Twice yearly', 'spring,fall', 'high', 'protective', 20, 0,
 'Expansive clay soils in parts of Kansas make this extra important.');

-- ─── ANNUALLY (every 365 days) ──────────────────────────────────────────────

INSERT INTO schedules (name, description, category, frequency_days, frequency_label, season_hint, priority, impact, estimated_minutes, pro_recommended, notes) VALUES
('Flush water heater',
 'Drain several gallons from the bottom valve to flush sediment. For a full flush: turn off power/gas, connect a hose to the drain valve, open a hot faucet upstairs for airflow, and drain until water runs clear.',
 'Plumbing', 365, 'Annually', 'fall', 'high', 'protective', 30, 0,
 'Kansas hard water = more sediment. This extends tank life significantly. Check anode rod every 2-3 years too.'),

('Clean dryer vent duct',
 'Disconnect the dryer duct from the wall and clean the full run to the exterior vent. Use a dryer vent brush kit or hire a pro. Clear lint from the exterior vent hood too.',
 'Safety', 365, 'Annually', NULL, 'critical', 'safety', 30, 0,
 'Lint buildup is a serious fire hazard. If your clothes take longer to dry, this might be overdue.'),

('Inspect roof',
 'Visual inspection from the ground with binoculars or safely from a ladder. Look for missing/damaged/curling shingles, damaged flashing around vents and chimneys, and any sagging.',
 'Structural', 365, 'Annually', 'spring', 'high', 'protective', 20, 0,
 'After any major Kansas hail storm, do an extra inspection regardless of schedule. Document with photos for insurance.'),

('Check fire extinguisher',
 'Verify the pressure gauge is in the green zone, the pin is intact, and the hose isn''t cracked. Check the manufacture/certification date.',
 'Safety', 365, 'Annually', NULL, 'high', 'safety', 5, 0,
 'Non-rechargeable extinguishers expire after ~10 years. Keep one in the kitchen and one near the furnace/garage.'),

('Lubricate garage door',
 'Apply white lithium grease or silicone spray to the springs, hinges, rollers, and track. Do NOT use WD-40 (it''s a solvent, not a lubricant). Check cables for fraying.',
 'Exterior', 365, 'Annually', NULL, 'normal', 'comfort', 15, 0, NULL),

('Deep clean carpet/flooring',
 'Rent or use a carpet cleaner for all carpeted areas. For hard floors, strip and recoat if applicable. Move furniture to clean underneath.',
 'Interior', 365, 'Annually', NULL, 'low', 'cosmetic', 120, 0, NULL),

('Touch up exterior caulk and paint',
 'Inspect exterior caulking around windows, doors, trim, and utility penetrations. Re-caulk gaps. Touch up any peeling or chipped exterior paint to prevent moisture infiltration.',
 'Exterior', 365, 'Annually', 'fall', 'normal', 'protective', 60, 0, NULL),

('Clean bathroom exhaust fans',
 'Remove the cover and clean accumulated dust and lint from the fan blades and housing. A clogged exhaust fan can''t remove moisture, leading to mold.',
 'HVAC', 365, 'Annually', NULL, 'normal', 'protective', 15, 0, NULL),

('Test water heater pressure relief valve',
 'Lift the lever on the TPR (temperature-pressure relief) valve briefly. Water should flow freely then stop when released. If it drips continuously or doesn''t flow, replace it.',
 'Plumbing', 365, 'Annually', NULL, 'high', 'safety', 5, 0,
 'Have a bucket handy. The discharge pipe should route to a drain or the floor, not be capped.');

-- ─── FALL / WINTER PREP (annually, Kansas-specific) ─────────────────────────

INSERT INTO schedules (name, description, category, frequency_days, frequency_label, season_hint, priority, impact, estimated_minutes, pro_recommended, notes) VALUES
('Winterize outdoor faucets',
 'Disconnect all garden hoses. Shut off interior valves to outdoor hose bibs if you have them. Install insulated faucet covers. Drain any outdoor irrigation lines.',
 'Plumbing', 365, 'Annually', 'fall', 'critical', 'protective', 20, 0,
 'Kansas freezes are no joke. A burst pipe from a frozen hose bib can cause thousands in damage.'),

('Check furnace before winter',
 'Turn on the furnace and let it run a full cycle before you actually need it. Listen for unusual noises. Sniff for gas smells. Verify all vents/registers are open and unobstructed.',
 'HVAC', 365, 'Annually', 'fall', 'high', 'safety', 15, 0,
 'First run of the season may smell like burning dust—that''s normal for a few minutes. If it persists, call a pro.'),

('Check pipe insulation',
 'Inspect insulation on any exposed water pipes in the basement, crawlspace, attic, or garage. Add foam pipe insulation where missing, especially on hot water lines and any pipes near exterior walls.',
 'Plumbing', 365, 'Annually', 'fall', 'normal', 'protective', 30, 0, NULL),

('Seal air leaks for winter',
 'Check around electrical outlets on exterior walls, window frames, dryer vent, and any other penetrations. Apply caulk, spray foam, or outlet insulation gaskets as needed.',
 'Exterior', 365, 'Annually', 'fall', 'normal', 'efficiency', 30, 0, NULL);

-- ─── SPRING SPECIFIC ────────────────────────────────────────────────────────

INSERT INTO schedules (name, description, category, frequency_days, frequency_label, season_hint, priority, impact, estimated_minutes, pro_recommended, notes) VALUES
('Inspect for winter damage',
 'Walk the property and look for damage from freezing, ice, snow, and wind. Check roof, gutters, foundation, siding, fences, deck/porch, and landscaping.',
 'Structural', 365, 'Annually', 'spring', 'high', 'protective', 30, 0,
 'Document any damage with photos. Check homeowner''s insurance deductible for storm damage claims.'),

('Service AC / clean condenser unit',
 'Clear debris (leaves, cottonwood fluff) from around the outdoor AC condenser. Gently spray coils with a hose from inside out. Trim vegetation to maintain 2 feet clearance around the unit.',
 'HVAC', 365, 'Annually', 'spring', 'high', 'efficiency', 20, 0,
 'Kansas cottonwood season absolutely destroys condenser coils if you don''t stay on top of this.'),

('Check window wells and basement entry',
 'Clear debris from window wells. Verify covers are intact. Check basement stairwell drains (if applicable) are clear.',
 'Structural', 365, 'Annually', 'spring', 'normal', 'protective', 15, 0, NULL);

-- ─── LONGER INTERVALS ───────────────────────────────────────────────────────

INSERT INTO schedules (name, description, category, frequency_days, frequency_label, priority, impact, estimated_minutes, pro_recommended, notes) VALUES
('Check/replace water heater anode rod',
 'The sacrificial anode rod protects the tank from corrosion. Unscrew it from the top of the tank and inspect. Replace if more than 50% corroded. Kansas hard water eats these faster.',
 'Plumbing', 1095, 'Every 2-3 years', 'high', 'protective', 30, 0,
 'Requires a 1-1/16" socket and breaker bar. Can be very tight. This is the single best thing you can do to extend tank water heater life.'),

('Reseal driveway',
 'If you have an asphalt driveway, clean and apply sealcoat. Fill any cracks first. Concrete driveways should be sealed too but less frequently.',
 'Exterior', 730, 'Every 2 years', 'low', 'protective', 120, 0,
 'Skip if you have a concrete driveway (seal every 3-5 years instead). Set active=0 if not applicable.'),

('Replace smoke detectors',
 'Smoke detectors expire after 10 years from manufacture date (not purchase date). Check the date printed on the back. Replace the entire unit.',
 'Safety', 3650, 'Every 10 years', 'critical', 'safety', 30, 0,
 'Replace all at once so they''re on the same cycle. Interconnected ones are best so they all alarm together.'),

('Professional chimney inspection and cleaning',
 'Have a CSIA-certified chimney sweep inspect and clean the chimney. They''ll check for creosote buildup, structural issues, and proper draft.',
 'Safety', 365, 'Annually', 'fall', 'high', 'safety', 60, 1,
 'Only if you have a fireplace/wood stove. Set active=0 if not applicable.');

-- ─── SEPTIC (if applicable) ─────────────────────────────────────────────────

INSERT INTO schedules (name, description, category, frequency_days, frequency_label, priority, impact, estimated_minutes, pro_recommended, active, notes) VALUES
('Pump septic tank',
 'Have the septic tank professionally pumped and inspected. Frequency depends on tank size and household size.',
 'Plumbing', 1095, 'Every 2-3 years', 'high', 'protective', 60, 1, 0,
 'DISABLED BY DEFAULT. Enable if you have a septic system. City sewer = skip this.');
