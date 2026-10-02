-- ARCHIVED RECONSTRUCTION: NOT VERIFIED AS THE EXACT ORIGINAL EXPORT QUERY
-- Engine: Dune SQL (V2)
-- Table: nft.trades

SELECT
    block_time,
    CAST(token_id AS VARCHAR) AS token_id,
    amount_usd AS price_usd,
    amount_original AS price_eth,
    buyer,
    seller,
    tx_hash,
    project,
    marketplace
FROM nft.trades
WHERE nft_contract_address = 0xED5AF388653567Af2F388E6224dC7C4b3241C544 -- Azuki Smart Contract Address
  AND block_time >= timestamp '2022-01-12' -- Azuki Launch Date
  AND block_time < timestamp '2026-04-15'  -- End of study period
  AND amount_usd > 0 -- Exclude transfers and zero-value trades
ORDER BY block_time ASC;

-- Note: The resulting CSV should be saved as 'azuki_all_trades.csv' in the project root.
