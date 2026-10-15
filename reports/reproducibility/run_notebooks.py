"""Execute notebooks in order in fresh IPython processes; stop on first error."""
import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
REPORT = ROOT / 'reports/reproducibility'
NOTEBOOKS = ['01_problem_statement.ipynb', '02_data_cleaning_split.ipynb',
             '03_eda.ipynb', '04_feature_engineering.ipynb',
             '05_model_evaluation.ipynb', '06_final_results_&_conclusions.ipynb']

def execute_notebook(filename):
    import nbformat
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from IPython.core.interactiveshell import InteractiveShell
    from IPython.utils.capture import capture_output
    from IPython.display import display
    notebook = nbformat.read(ROOT / filename, as_version=4)
    shell = InteractiveShell.instance()
    shell.user_ns['display'] = display
    def show_figures(*args, **kwargs):
        for number in plt.get_fignums():
            figure = plt.figure(number)
            buffer = io.BytesIO()
            figure.savefig(buffer, format='png', dpi=130, bbox_inches='tight')
            display({'image/png': base64.b64encode(buffer.getvalue()).decode('ascii'),
                     'text/plain': f'Matplotlib figure {number}'}, raw=True)
            plt.close(figure)
    plt.show = show_figures
    start = time.monotonic()
    executed = 0
    for position, cell in enumerate(notebook.cells):
        if cell.cell_type != 'code':
            continue
        print(f'{filename}: cell {position + 1} START {cell.source.splitlines()[0] if cell.source else "empty"}', flush=True)
        with capture_output(stdout=True, stderr=True, display=True) as captured:
            result = shell.run_cell(cell.source, store_history=True)
        outputs = []
        if captured.stdout:
            outputs.append(nbformat.v4.new_output('stream', name='stdout', text=captured.stdout))
        if captured.stderr:
            outputs.append(nbformat.v4.new_output('stream', name='stderr', text=captured.stderr))
        for rich in captured.outputs:
            outputs.append(nbformat.v4.new_output('display_data', data=rich.data, metadata=rich.metadata))
        if result.result is not None:
            data, metadata = shell.display_formatter.format(result.result)
            outputs.append(nbformat.v4.new_output('execute_result', data=data, metadata=metadata,
                                                  execution_count=executed + 1))
        error = result.error_before_exec or result.error_in_exec
        if error:
            outputs.append(nbformat.v4.new_output('error', ename=type(error).__name__,
                                                  evalue=str(error), traceback=captured.stdout.splitlines()))
        cell.outputs = outputs
        executed += 1
        cell.execution_count = executed
        nbformat.write(notebook, ROOT / filename)
        if error:
            print(captured.stdout, flush=True)
            raise RuntimeError(f'{filename}, cell {position + 1}: {type(error).__name__}: {error}')
        print(f'{filename}: cell {position + 1} PASS ({time.monotonic() - start:.1f}s elapsed)', flush=True)
    nbformat.validate(notebook)
    return {'notebook': filename, 'status': 'passed', 'executed_code_cells': executed,
            'seconds': round(time.monotonic() - start, 2),
            'sha256': hashlib.sha256((ROOT / filename).read_bytes()).hexdigest()}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--notebook', choices=NOTEBOOKS)
    args = parser.parse_args()
    os.chdir(ROOT)
    REPORT.mkdir(parents=True, exist_ok=True)
    if args.notebook:
        result = execute_notebook(args.notebook)
        (REPORT / (Path(args.notebook).stem + '_execution.json')).write_text(json.dumps(result, indent=2))
        return
    summary = {'execution_mode': 'fresh IPython process per notebook, every code cell in order',
               'python': sys.version.split()[0], 'status': 'running', 'notebooks': []}
    for filename in NOTEBOOKS:
        log = REPORT / (Path(filename).stem + '.log')
        env = os.environ.copy()
        env.update(OMP_NUM_THREADS='4', OPENBLAS_NUM_THREADS='4',
                   MPLCONFIGDIR='/private/tmp/capstone-mpl', PLOTLY_RENDERERS='plotly_mimetype')
        print('Executing', filename, flush=True)
        with log.open('w') as stream:
            completed = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--notebook', filename],
                                       env=env, stdout=stream, stderr=subprocess.STDOUT, cwd=ROOT)
        if completed.returncode:
            summary['status'] = 'failed'
            summary['failed_notebook'] = filename
            (REPORT / 'execution_summary.json').write_text(json.dumps(summary, indent=2))
            print(log.read_text()[-12000:], flush=True)
            sys.exit(completed.returncode)
        result = json.loads((REPORT / (Path(filename).stem + '_execution.json')).read_text())
        summary['notebooks'].append(result)
        (REPORT / 'execution_summary.json').write_text(json.dumps(summary, indent=2))
        print('Passed', filename, result['seconds'], 'seconds', flush=True)
    summary['status'] = 'passed'
    (REPORT / 'execution_summary.json').write_text(json.dumps(summary, indent=2))
    print('All six notebooks passed in order.', flush=True)

if __name__ == '__main__':
    main()
