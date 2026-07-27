"""Optional DataFrame helpers.

The client returns raw ``list[dict]`` so it depends on no DataFrame library. These
helpers turn that into a pandas or polars frame *if* the caller installed the extra
(``pip install 'opendartclient[pandas]'`` / ``[polars]``). Neither import runs unless
the helper is called, so the core stays dependency-free.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd
    import polars as pl

Rows = list[dict[str, Any]]


def to_pandas(rows: Rows) -> pd.DataFrame:
    """Build a pandas DataFrame from OpenDART rows. Requires the ``pandas`` extra."""
    try:
        import pandas as pd
    except ImportError as err:
        raise ImportError(
            "to_pandas needs pandas -- install with: pip install 'opendartclient[pandas]'"
        ) from err
    return pd.DataFrame(rows)


def to_polars(rows: Rows) -> pl.DataFrame:
    """Build a polars DataFrame from OpenDART rows. Requires the ``polars`` extra."""
    try:
        import polars as pl
    except ImportError as err:
        raise ImportError(
            "to_polars needs polars -- install with: pip install 'opendartclient[polars]'"
        ) from err
    return pl.DataFrame(rows)
