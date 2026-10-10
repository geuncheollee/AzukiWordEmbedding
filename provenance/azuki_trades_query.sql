-- Azuki transaction retrieval query supplied by the authors for resubmission.
-- Run in the Dune SQL editor: https://dune.com
-- This query retrieves all available columns for Ethereum Azuki trades.
-- It has no date, amount, primary/secondary-trade, or ordering filter.
-- Results depend on the execution date and the current nft.trades table.
-- It is not guaranteed to reproduce the historical 110,561-row export.
-- The original execution/query identifier was not retained.
-- Providing this query does not assert a redistribution license for Dune data.

SELECT *
FROM nft.trades
WHERE blockchain = 'ethereum'
  AND nft_contract_address IN (
    0xed5af388653567af2f388e6224dc7c4b3241c544
  );
