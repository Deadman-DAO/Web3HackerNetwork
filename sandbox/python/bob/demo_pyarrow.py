import pyarrow as pa
import pyarrow.parquet as pq

col_type = pa.array(['dog', 'cat', 'monkey'])
col_val = pa.array([1.0, 0.5, 0.7])
col_weight = pa.array([26, 5, 9])

col_names = ["type", "value", "weight"]

data = [ col_type, col_val, col_weight ]
batch = pa.RecordBatch.from_arrays(
    data, col_names
)

table = pa.Table.from_batches([batch])

fixed_schema = pa.schema(
    [
        pa.field('type', pa.string(), metadata={"name": "Pet Type"}),
        pa.field('value', pa.float64(), metadata={"name": "Value"}),
        pa.field('weight', pa.float64(), metadata={"name": "Weight"})
    ]
)

fixed_table = table.cast(fixed_schema)

print(str(fixed_table))
print(str(fixed_table.schema))

# pq.write_table(fixed_table, 'example.parquet')
pq.write_to_dataset(fixed_table,
                    root_path='example_partitioned',
                    partition_cols=['type'])

