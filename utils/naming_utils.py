import os,uuid
def output_name(original,extension,prefix=None):
    stem=os.path.splitext(os.path.basename(original))[0];stem=''.join(c if c.isalnum() or c in '._-' else '_' for c in stem)[:80] or 'output';return f'{prefix+"_" if prefix else ""}{stem}_{uuid.uuid4().hex[:10]}.{extension.lstrip(".")}'
