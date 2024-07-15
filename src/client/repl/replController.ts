import * as vscode from 'vscode';
import { createPythonServer } from './pythonServer';

export function createReplController(
    interpreterPath: string,
    disposables: vscode.Disposable[],
): vscode.NotebookController {
    const server = createPythonServer([interpreterPath]);
    disposables.push(server);

    const controller = vscode.notebooks.createNotebookController('pythonREPL', 'interactive', 'Python REPL');
    controller.supportedLanguages = ['python'];
    controller.supportsExecutionOrder = true;

    controller.description = 'Python REPL';

    controller.interruptHandler = async () => {
        server.interrupt();
    };

    controller.executeHandler = async (cells) => {
        for (const cell of cells) {
            const exec = controller.createNotebookCellExecution(cell);
            exec.start(Date.now());
            try {
                const result = JSON.stringify(await server.execute(cell.document.getText()));
                const parsedResult = JSON.parse(result);
                const executionStatus = parsedResult.status;
                const executionOutput = parsedResult.output;

                if (result) {
                    if (executionOutput !== '') {
                        // Only append output if there is something to show.
                        exec.replaceOutput([
                            new vscode.NotebookCellOutput([
                                vscode.NotebookCellOutputItem.text(executionOutput, 'text/plain'),
                            ]),
                        ]);
                    }
                }
                exec.end(executionStatus);
            } catch (err) {
                const error = err as Error;
                exec.replaceOutput([
                    new vscode.NotebookCellOutput([
                        vscode.NotebookCellOutputItem.error({
                            name: error.name,
                            message: error.message,
                            stack: error.stack,
                        }),
                    ]),
                ]);
                exec.end(false);
            }
        }
    };
    disposables.push(controller);
    return controller;
}
