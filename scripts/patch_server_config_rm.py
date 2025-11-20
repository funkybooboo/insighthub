from pathlib import Path
p=Path('/home/nate/projects/insighthub/packages/server/tests/unit/test_config.py')
lines=p.read_text().splitlines()
start=101  # 0-based index for line 102
end=138    # inclusive index for line 138
new=lines[:start]+lines[end:]
p.write_text('\n'.join(new)+"\n")
print('patched')
