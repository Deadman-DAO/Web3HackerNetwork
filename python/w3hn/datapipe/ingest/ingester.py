import pyarrow as pa

class Ingester:

    # Same across entire raw tier. (or, if not, needs big rethink)
    PARTITION_KEY_FIELD = pa.field("partition_key", pa.string())
