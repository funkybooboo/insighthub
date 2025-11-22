import { init } from './init';
import { status } from './status';

export function runCommand(args: string[]) {
    const [command, ...rest] = args;

    switch (command) {
        case 'init':
            return init(rest);

        case 'status':
            return status(rest);

        default:
            console.log('Unknown command:', command);
            console.log('Available commands: init, status');
    }
}
