## Usage

To use this tool, paste the following snippet into tool.xml, and include all results files where you want to pregenerate the SQLite files for.  result_view corresponds to the view name in result.xml for the given file.

```
<pathSet base="/Users/bpullman/miniconda3/envs/datasette_env/bin">
  <pathVar name="csvs-to-sqlite" path="csvs-to-sqlite"/>
</pathSet>
<pathSet base="generate_sqlite_result/0.1">
  <pathVar name="convert_tsv_to_sqlite.script" path="convert_tsv_to_sqlite.py" />
</pathSet>
<pathSet base="anaconda3">
  <toolPath tool="convert_tsv_to_sqlite" path="bin/python3.5" />
</pathSet>
<tool name="convert_tsv_to_sqlite">
  <require name="<result_file_1>"      type="file"/>
  <require name="<result_file_2>"      type="file"/>
  ...
  <produce name="sqlite"               type="folder"/>
  <execution env="binary" argConvention="adhoc">
    <arg pathRef="convert_tsv_to_sqlite.script"/>
    <arg pathRef="csvs-to-sqlite"/>
    <arg valueRef="sqlite"/>
    <arg option="<result_view_1>"       valueRef="<result_file_1>"/>
    <arg option="<result_view_2>"       valueRef="<result_file_2>"/>
    ...
  </execution>
</tool>
```
