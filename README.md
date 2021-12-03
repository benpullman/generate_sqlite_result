## Usage

To use this tool, paste the following snippet into tool.xml, and include all results files where you want to pregenerate the SQLite files for.  result_view corresponds to the view name in result.xml for the given file.

```
<pathSet base="/Users/bpullman/miniconda3/envs/datasette_env/bin">
  <toolPath tool="convert_tsv_to_sqlite" path="python3" />
</pathSet>
<pathSet base="generate_sqlite_result/0.4">
  <pathVar name="convert_tsv_to_sqlite.script" path="convert_tsv_to_sqlite.py" />
</pathSet>
<tool name="convert_tsv_to_sqlite">
  <require name="input"  type="file"/>
  <produce name="output" type="folder"/>
  <execution env="binary" argConvention="adhoc">
    <arg pathRef="convert_tsv_to_sqlite.script"/>
    <arg option="d" valueRef="#<result_view_name>:+input+#:<index1>,<index2>,<index1a>+<index1b>"/>
    <arg option="o" valueRef="output"/>
  </execution>
</tool>
```
