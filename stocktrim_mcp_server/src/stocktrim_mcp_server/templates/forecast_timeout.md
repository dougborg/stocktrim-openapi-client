# Forecast Update Status

**Status**: ⚠️ Timeout

**Time Elapsed**: {elapsed:.1f} seconds

**Progress**: {current_percentage}%

The forecast calculation did not complete within {timeout_seconds} seconds. The
calculation is still running in the background.

**Last Status**: {status_message}

## Next Steps

- Wait a few minutes and check again with wait_for_completion=false
- Use `forecasts_get_for_products` to see if any forecasts were updated
- Consider increasing timeout_seconds for future operations
