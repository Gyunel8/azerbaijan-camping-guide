-- 2. Average rating by region
SELECT region, ROUND(AVG(rating), 1) AS avg_rating
FROM camping_azerbaijan_real
GROUP BY region
ORDER BY avg_rating DESC;

-- 3. Hard to reach places only
SELECT name, region, rating, transport
FROM camping_azerbaijan_real
WHERE difficulty = 'Hard'
ORDER BY rating DESC;

-- 4. Best camp per season
SELECT season, name, region, rating
FROM camping_azerbaijan_real
ORDER BY season, rating DESC;

-- 5. Camps without mosquitoes, rating above 4
SELECT name, region, rating, highlight
FROM camping_azerbaijan_real
WHERE mosquitoes = 'No' AND rating >= 4
ORDER BY rating DESC;