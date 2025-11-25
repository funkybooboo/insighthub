import { Command } from 'commander';

export const docsCommand = new Command('docs').description('Manage documents');

docsCommand
    .command('list')
    .description('List documents in workspace')
    .action(async () => {
        console.log('Document listing not yet implemented');
    });

docsCommand
    .command('upload <file>')
    .description('Upload a document')
    .action(async (file: string) => {
        console.log(`Document upload not yet implemented for: ${file}`);
    });
