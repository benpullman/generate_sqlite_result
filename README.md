## Usage

To use this tool, paste the following snippet into tool.xml, and include all results files where you want to pregenerate the SQLite files for.  result_view corresponds to the view name in result.xml for the given file.

```
<pathSet base="/Users/bpullman/miniconda3/envs/datasette_env/bin">
  <toolPath tool="convert_tsv_to_sqlite" path="python3" />
</pathSet>
<pathSet base="generate_sqlite_result/0.3">
  <pathVar name="convert_tsv_to_sqlite.script" path="convert_tsv_to_sqlite.py" />
</pathSet>
<tool name="convert_tsv_to_sqlite">
  <require name="<result_file_1>"      type="file"/>
  <require name="<result_file_2>"      type="file"/>
  <require name="<result_file_3>"      type="file"/>
  ...
  <produce name="sqlite"               type="folder"/>
  <execution env="binary" argConvention="adhoc">
    <arg pathRef="convert_tsv_to_sqlite.script"/>
    <arg valueRef="sqlite"/>
    <arg option="<result_view_1>"       valueRef="<result_file_1>"/>
    <arg option="<result_view_2>:<index1>,<index2>"       valueRef="<result_file_2>"/>
    <arg option="<result_view_3>:<index1a>+<index1b>"       valueRef="<result_file_3>"/>
    ...
  </execution>
</tool>
```
